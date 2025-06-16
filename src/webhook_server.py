from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Any

import arxiv
import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from .query_interface import parse

if TYPE_CHECKING:
    from collections.abc import Generator

# Discord constants
DISCORD_INTERACTION_TYPE_APPLICATION_COMMAND = 2
HTTP_STATUS_OK = 200

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class ArxivWebhookHandler:
    MESSAGE_THRESHOLD = 2000

    def __init__(self) -> None:
        # Check for Discord credentials
        self.public_key = os.getenv("DISCORD_PUBLIC_KEY")
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.application_id = os.getenv("DISCORD_APPLICATION_ID")

        # Create arXiv client
        self.arxiv_client = arxiv.Client()

        logger.info("ArxivWebhookHandler initialized")

    def verify_signature(self, signature: str, timestamp: str, body: bytes) -> bool:
        """Verify Discord webhook signature."""
        if not self.public_key:
            return True  # Skip verification if no public key

        try:
            verify_key = VerifyKey(bytes.fromhex(self.public_key))
            verify_key.verify(timestamp.encode() + body, bytes.fromhex(signature))
        except BadSignatureError:
            return False
        else:
            return True

    async def handle_interaction(
        self,
        interaction_data: dict[str, Any],
        background_tasks: BackgroundTasks,
    ) -> dict[str, Any]:
        """Handle Discord interaction."""
        interaction_type = interaction_data.get("type")

        # Handle ping
        if interaction_type == 1:
            return {"type": 1}

        # Handle application command
        if interaction_type == DISCORD_INTERACTION_TYPE_APPLICATION_COMMAND:
            command_name = interaction_data.get("data", {}).get("name")

            if command_name == "arxiv":
                # Return deferred response immediately
                background_tasks.add_task(
                    self._process_arxiv_command_async,
                    interaction_data,
                )
                return {
                    "type": 5,  # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
                    "data": {"flags": 0},
                }

        return {"type": 4, "data": {"content": "Unknown command"}}

    async def _process_arxiv_command_async(self, interaction_data: dict[str, Any]) -> None:
        """Process arxiv command asynchronously and send followup."""
        try:
            # Extract query
            options = interaction_data.get("data", {}).get("options", [])
            query_param = next((opt for opt in options if opt["name"] == "query"), None)

            if not query_param:
                await self._edit_deferred_response(
                    interaction_data["token"],
                    "Query parameter is required",
                )
                return

            query_text = query_param["value"]
            logger.info("Processing arxiv query: %s", query_text)

            # Parse query
            search_query = parse(query_text)

            if search_query is None:
                await self._edit_deferred_response(
                    interaction_data["token"],
                    "Invalid query format",
                )
                return

            # Get results based on user query
            logger.info("Fetching results")
            results = self.arxiv_client.results(search_query)
            message_list = self._process_results(results)

            # Send query info as deferred response
            await self._edit_deferred_response(
                interaction_data["token"],
                "Processing your query...",
            )

            if not message_list or not any(msg.strip() for msg in message_list):
                await self._send_followup_message(
                    interaction_data["token"],
                    "No results found",
                )
                return

            # Send all result messages as followups
            for message in message_list:
                if message.strip():
                    try:
                        await self._send_followup_message(
                            interaction_data["token"],
                            message.strip(),
                        )
                    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException):
                        logger.exception("Timeout sending followup message")
                        continue
                    except Exception:
                        logger.exception("Failed to send followup message")
                        continue

                    # Delay between messages to avoid rate limiting
                    await asyncio.sleep(1.5)

        except Exception as e:
            logger.exception("Error processing arxiv command")
            await self._edit_deferred_response(
                interaction_data["token"],
                f"An error occurred: {e!s}",
            )

    async def _edit_deferred_response(self, interaction_token: str, content: str) -> None:
        """Edit the deferred response via Discord API."""
        if not self.bot_token or not self.application_id:
            logger.error("DISCORD_BOT_TOKEN or DISCORD_APPLICATION_ID not set")
            return

        url = f"https://discord.com/api/v10/webhooks/{self.application_id}/{interaction_token}/messages/@original"

        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

        data = {"content": content}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(url, headers=headers, json=data)
            if response.status_code != HTTP_STATUS_OK:
                logger.error(
                    "Failed to edit deferred response: %s - %s",
                    response.status_code,
                    response.text,
                )

    async def _send_followup_message(self, interaction_token: str, content: str) -> None:
        """Send followup message via Discord API."""
        if not self.bot_token or not self.application_id:
            logger.error("DISCORD_BOT_TOKEN or DISCORD_APPLICATION_ID not set")
            return

        url = f"https://discord.com/api/v10/webhooks/{self.application_id}/{interaction_token}"

        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

        data = {"content": content}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code != HTTP_STATUS_OK:
                logger.error(
                    "Failed to send followup: %s - %s",
                    response.status_code,
                    response.text,
                )

    def _process_results(self, results: Generator[arxiv.Result]) -> list[str]:
        """Process arXiv results into Discord messages.

        Args:
            results: Generator of arXiv results

        """
        message_list = [""]
        count = 0

        for result in results:
            count += 1
            content = f"**[{count}] {result.title}**\n<{result}>\n"

            # Check if adding this content would exceed the threshold
            if len(message_list[-1]) + len(content) > self.MESSAGE_THRESHOLD:
                # If the current message is not empty, start a new message
                if message_list[-1].strip():
                    message_list.append(content)
                else:
                    # If current message is empty but content is too long, add it anyway
                    message_list[-1] += content
            else:
                message_list[-1] += content

        # Add summary at the end
        if message_list and count > 0:
            summary = f"\n*Found {count} results*"
            # If adding summary would exceed threshold, put it in a new message
            if len(message_list[-1]) + len(summary) > self.MESSAGE_THRESHOLD:
                message_list.append(summary)
            else:
                message_list[-1] += summary

        return message_list


class HandlerSingleton:
    """Singleton pattern for webhook handler."""

    _instance: ArxivWebhookHandler | None = None

    @classmethod
    def get_instance(cls) -> ArxivWebhookHandler:
        """Get singleton instance of webhook handler."""
        if cls._instance is None:
            cls._instance = ArxivWebhookHandler()
        return cls._instance


def get_handler() -> ArxivWebhookHandler:
    """Get webhook handler instance."""
    return HandlerSingleton.get_instance()


@app.post("/interactions")
async def interactions_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """Discord interactions endpoint."""
    handler = get_handler()

    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    body = await request.body()

    # Verify signature
    logger.info("Received interaction request. Public key available: %s", bool(handler.public_key))

    if handler.public_key:
        if not signature or not timestamp:
            raise HTTPException(status_code=401, detail="Missing signature headers")

        if not handler.verify_signature(signature, timestamp, body):
            raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        interaction_data = json.loads(body)
        response = await handler.handle_interaction(interaction_data, background_tasks)
        return JSONResponse(content=response)
    except Exception as e:
        logger.exception("Error handling interaction")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug")
async def debug_endpoint() -> dict[str, Any]:
    """Debug endpoint to check environment variables."""
    handler = get_handler()

    return {
        "status": "debug",
        "environment": {
            "DISCORD_BOT_TOKEN": "***" if handler.bot_token else "NOT_SET",
            "DISCORD_PUBLIC_KEY": "***" if handler.public_key else "NOT_SET",
            "DISCORD_APPLICATION_ID": "***" if handler.application_id else "NOT_SET",
            "PORT": os.getenv("PORT", "8000"),
        },
    }


@app.post("/scheduler")
async def scheduler_endpoint() -> dict[str, str]:
    """Scheduler endpoint for auto channel processing."""
    try:
        from scheduler import ArxivScheduler

        scheduler = ArxivScheduler()
        await scheduler.run_scheduler()
    except Exception as e:
        logger.exception("Error in scheduler endpoint")
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        return {"status": "completed"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    logger.info("Starting server on port %d", port)
    # Bind to all interfaces for Docker/Railway deployment
    uvicorn.run(app, host="0.0.0.0", port=port)  # noqa: S104

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
from typing import TYPE_CHECKING, Any

import arxiv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tools import parse
from scheduler import ArxivScheduler

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)

app = FastAPI()


class ArxivWebhookHandler:
    MESSAGE_THRESHOLD = 2000
    
    def __init__(self) -> None:
        self.arxiv_client = arxiv.Client()
        self.public_key = os.getenv("DISCORD_PUBLIC_KEY")
        if not self.public_key:
            logger.warning("DISCORD_PUBLIC_KEY not set - signature verification disabled")

    def verify_signature(self, signature: str, timestamp: str, body: bytes) -> bool:
        """Verify Discord webhook signature"""
        if not self.public_key:
            logger.warning("Signature verification skipped - no public key")
            return True
            
        try:
            from nacl.signing import VerifyKey
            from nacl.exceptions import BadSignatureError
            
            verify_key = VerifyKey(bytes.fromhex(self.public_key))
            verify_key.verify(timestamp.encode() + body, bytes.fromhex(signature))
            return True
        except (BadSignatureError, Exception):
            return False

    async def handle_interaction(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """Handle Discord interaction"""
        interaction_type = interaction_data.get("type")
        
        # PING
        if interaction_type == 1:
            return {"type": 1}
        
        # APPLICATION_COMMAND
        if interaction_type == 2:
            return await self._handle_application_command(interaction_data)
        
        return {"type": 4, "data": {"content": "Unknown interaction type"}}

    async def _handle_application_command(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """Handle application command interaction"""
        command_name = interaction_data.get("data", {}).get("name")
        
        if command_name == "arxiv":
            return await self._handle_arxiv_command(interaction_data)
        
        return {
            "type": 4,
            "data": {"content": "Unknown command"}
        }

    async def _handle_arxiv_command(self, interaction_data: dict[str, Any]) -> dict[str, Any]:
        """Handle /arxiv command"""
        try:
            options = interaction_data.get("data", {}).get("options", [])
            query_param = next((opt for opt in options if opt["name"] == "query"), None)
            
            if not query_param:
                return {
                    "type": 4,
                    "data": {"content": "Query parameter is required"}
                }
            
            query_text = query_param["value"]
            logger.info("Processing arxiv query: %s", query_text)
            
            # Parse query
            search_query = parse(query_text)
            if search_query is None:
                return {
                    "type": 4,
                    "data": {"content": "Invalid query format"}
                }
            
            # Get results
            results = self.arxiv_client.results(search_query)
            message_list = self._process_results(results)
            
            if not message_list or not any(msg.strip() for msg in message_list):
                return {
                    "type": 4,
                    "data": {"content": "No results found"}
                }
            
            # Return first message immediately, others as followups
            first_message = message_list[0].strip()
            response = {
                "type": 4,
                "data": {"content": first_message}
            }
            
            # Send followup messages if there are more
            if len(message_list) > 1:
                # Note: Followup messages need to be sent via Discord API
                # This is a simplified version - in production you'd need
                # to implement proper followup message handling
                pass
            
            return response
            
        except Exception as e:
            logger.exception("Error processing arxiv command")
            return {
                "type": 4,
                "data": {"content": f"An error occurred: {str(e)}"}
            }

    def _process_results(self, results: Generator[arxiv.Result]) -> list[str]:
        """Process arXiv results into Discord messages"""
        message_list = [""]
        
        for result in results:
            content = f"{result.title}\n<{result}>\n"
            
            if len(message_list[-1]) + len(content) > self.MESSAGE_THRESHOLD:
                message_list.append(content)
            else:
                message_list[-1] += content
        
        return message_list


# Global handler instance - initialize when needed to ensure env vars are loaded
handler = None

def get_handler():
    global handler
    if handler is None:
        handler = ArxivWebhookHandler()
    return handler


@app.post("/interactions")
async def interactions_endpoint(request: Request) -> JSONResponse:
    """Discord interactions endpoint"""
    handler = get_handler()
    
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    
    body = await request.body()
    
    # Proper signature verification
    logger.info(f"Received interaction request. Public key available: {bool(handler.public_key)}")
    
    if handler.public_key:
        if not signature or not timestamp:
            raise HTTPException(status_code=401, detail="Missing signature headers")
        
        if not handler.verify_signature(signature, timestamp, body):
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning("DISCORD_PUBLIC_KEY not set - signature verification skipped")
    
    try:
        interaction_data = json.loads(body)
        response = await handler.handle_interaction(interaction_data)
        return JSONResponse(content=response)
    except Exception as e:
        logger.exception("Error handling interaction")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/scheduler")
async def scheduler_endpoint() -> dict[str, str]:
    """Scheduler endpoint for auto channel processing"""
    try:
        scheduler = ArxivScheduler()
        await scheduler.run_scheduler()
        return {"status": "completed"}
    except Exception as e:
        logger.exception("Error in scheduler endpoint")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
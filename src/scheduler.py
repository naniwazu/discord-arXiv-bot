from __future__ import annotations

import asyncio
import datetime
import json
import logging
import os
from typing import TYPE_CHECKING, Any

import arxiv
import httpx

from tools import parse

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


class ArxivScheduler:
    """Auto-search functionality for channels starting with 'auto'"""
    
    def __init__(self) -> None:
        self.arxiv_client = arxiv.Client()
        self.discord_token = os.getenv("DISCORD_BOT_TOKEN")
        if not self.discord_token:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

    async def get_auto_channels(self) -> list[dict[str, Any]]:
        """Get all channels that start with 'auto' across all guilds"""
        headers = {"Authorization": f"Bot {self.discord_token}"}
        
        async with httpx.AsyncClient() as client:
            # Get guilds
            guilds_response = await client.get(
                "https://discord.com/api/v10/users/@me/guilds",
                headers=headers
            )
            guilds = guilds_response.json()
            
            auto_channels = []
            
            for guild in guilds:
                guild_id = guild["id"]
                
                # Get channels for this guild
                channels_response = await client.get(
                    f"https://discord.com/api/v10/guilds/{guild_id}/channels",
                    headers=headers
                )
                channels = channels_response.json()
                
                # Filter channels that start with 'auto'
                for channel in channels:
                    if (channel.get("type") == 0 and  # TEXT_CHANNEL
                        channel.get("name", "").startswith("auto")):
                        auto_channels.append({
                            "id": channel["id"],
                            "name": channel["name"],
                            "topic": channel.get("topic", ""),
                            "guild_id": guild_id
                        })
            
            return auto_channels

    async def send_message(self, channel_id: str, content: str) -> None:
        """Send message to Discord channel"""
        headers = {
            "Authorization": f"Bot {self.discord_token}",
            "Content-Type": "application/json"
        }
        
        data = {"content": content}
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                headers=headers,
                json=data
            )

    def _process_results(self, results: Generator[arxiv.Result]) -> list[str]:
        """Process arXiv results into Discord messages"""
        message_list = [""]
        message_threshold = 2000
        
        for result in results:
            content = f"{result.title}\n<{result}>\n"
            
            if len(message_list[-1]) + len(content) > message_threshold:
                message_list.append(content)
            else:
                message_list[-1] += content
        
        return message_list

    async def process_auto_channels(self) -> None:
        """Process all auto channels for scheduled searches"""
        try:
            logger.info("Starting auto channel processing")
            
            # Get current time and calculate date range
            dt_now = datetime.datetime.now(datetime.timezone.utc)
            since = dt_now - datetime.timedelta(days=3)
            until = dt_now - datetime.timedelta(days=2)
            since_string = since.strftime("%Y%m%d%H%M%S")
            until_string = until.strftime("%Y%m%d%H%M%S")
            
            # Get auto channels
            auto_channels = await self.get_auto_channels()
            logger.info("Found %d auto channels", len(auto_channels))
            
            for channel in auto_channels:
                try:
                    channel_id = channel["id"]
                    topic = channel.get("topic", "")
                    
                    if not topic:
                        logger.warning("No topic found for channel %s", channel["name"])
                        await self.send_message(channel_id, "No search query found in channel topic")
                        continue
                    
                    # Add date range to query
                    query_text = f"{topic} since:{since_string} until:{until_string}"
                    
                    # Parse and execute query
                    search_query = parse(query_text)
                    if search_query is None:
                        logger.warning("Invalid query for channel %s: %s", channel["name"], query_text)
                        await self.send_message(channel_id, "Invalid query format in channel topic")
                        continue
                    
                    search_query.max_results = None
                    results = self.arxiv_client.results(search_query)
                    message_list = self._process_results(results)
                    
                    # Send results
                    if not message_list or not any(msg.strip() for msg in message_list):
                        logger.info("No results found for channel %s", channel["name"])
                        await self.send_message(channel_id, "No results found")
                    else:
                        for message in message_list:
                            if message.strip():
                                await self.send_message(channel_id, message.strip())
                        logger.info("Sent %d messages to channel %s", len(message_list), channel["name"])
                    
                except Exception as e:
                    logger.exception("Error processing channel %s", channel.get("name", "unknown"))
                    
        except Exception as e:
            logger.exception("Error in auto channel processing")

    async def run_scheduler(self) -> None:
        """Run the scheduler - call this from your deployment platform's cron job"""
        await self.process_auto_channels()


async def main() -> None:
    """Main function for running the scheduler"""
    logging.basicConfig(level=logging.INFO)
    scheduler = ArxivScheduler()
    await scheduler.run_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
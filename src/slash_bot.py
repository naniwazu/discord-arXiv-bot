from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

import arxiv
import discord
from discord import Interaction, app_commands
from discord.ext import commands

from tools import parse

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


class ArxivSlashBot:
    def __init__(self) -> None:
        self.intents = discord.Intents.default()
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        self.arxiv_client = arxiv.Client()
        
        # Event handlers
        self.bot.event(self.on_ready)
        
        # Register slash commands
        self.bot.tree.add_command(self.arxiv_search)
        
        logger.info("ArxivSlashBot initialized")

    async def on_ready(self) -> None:
        logger.info("Bot is ready. Logged in as %s", self.bot.user)
        try:
            synced = await self.bot.tree.sync()
            logger.info("Synced %d command(s)", len(synced))
        except Exception as e:
            logger.error("Failed to sync commands: %s", e)

    @app_commands.command(name="arxiv", description="Search arXiv papers")
    @app_commands.describe(
        query="Search query (e.g., 'ti:machine,learning 20 s since:20240101')",
    )
    async def arxiv_search(self, interaction: Interaction, query: str) -> None:
        await interaction.response.defer()
        
        try:
            logger.info("Processing slash command from %s: %s", interaction.user, query)
            
            search_query = parse(query)
            if search_query is None:
                await interaction.followup.send("Invalid query format")
                return
            
            results = self.arxiv_client.results(search_query)
            message_list = self._process_results(results)
            
            await self._send_results(interaction, message_list)
            
        except Exception as e:
            logger.exception("Error processing slash command")
            await interaction.followup.send(f"An error occurred: {str(e)}")

    def _process_results(self, results: Generator[arxiv.Result]) -> list[str]:
        message_list = [""]
        message_threshold = 2000
        
        for result in results:
            content = f"{result.title}\n<{result}>\n"
            
            if len(message_list[-1]) + len(content) > message_threshold:
                message_list.append(content)
            else:
                message_list[-1] += content
                
        return message_list

    async def _send_results(self, interaction: Interaction, message_list: list[str]) -> None:
        sent = False
        
        for i, message in enumerate(message_list):
            if len(message) > 0:
                content = message[:-1]  # Remove last newline
                
                if i == 0:
                    await interaction.followup.send(content)
                else:
                    await interaction.followup.send(content)
                sent = True
        
        if not sent:
            await interaction.followup.send("No results found")

    def run(self) -> None:
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        
        try:
            logger.info("Starting slash command bot...")
            self.bot.run(token)
        except Exception as e:
            logger.critical("Bot startup failed: %s", e, exc_info=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = ArxivSlashBot()
    bot.run()


if __name__ == "__main__":
    main()
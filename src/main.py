from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import arxiv
import discord
from discord import Message, TextChannel
from discord.ext import tasks

from tools import parse

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class ArxivDiscordBot:
    MESSEAGE_THRESHOLD_LENGTH = 2000
    DEFAULT_AUTO_PROCESS_HOUR = 1
    DEFAULT_AUTO_PROCESS_MINUTE = 0

    def __init__(
        self,
        config_path: Path | str | None = None,
        *,
        auto_process_hour: int = DEFAULT_AUTO_PROCESS_HOUR,
        auto_process_minute: int = DEFAULT_AUTO_PROCESS_MINUTE,
    ) -> None:
        self.auto_process_hour = auto_process_hour
        self.auto_pocess_minute = auto_process_minute
        # Use config.json in the same directory as main.py if config_path is not specified
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"

        # Convert to Path object
        config_path = Path(config_path)

        # Check if config file exists
        if not config_path.is_file():
            raise FileNotFoundError(config_path)

        # Load configuration
        with config_path.open() as config_file:
            self.config: dict[str, str] = json.load(config_file)

        # Discord setup
        self.intents: discord.Intents = discord.Intents.default()
        self.intents.message_content = True
        self.discord_client: discord.Client = discord.Client(intents=self.intents)

        # arXiv client
        self.arxiv_client: arxiv.Client = arxiv.Client()

        # Processing set
        self.to_process: set[TextChannel] = set()

        # Event registrations
        self.discord_client.event(self.on_ready)
        self.discord_client.event(self.on_message)

        # Log output
        logger.info("ArxivDiscordBot initialized with config: %s", config_path)

    async def on_ready(self) -> None:
        logger.info("Bot is ready. Logged in as %s", self.discord_client.user)
        self.loop.start()

    @tasks.loop(seconds=60)
    async def loop(self) -> None:
        try:
            await self.discord_client.wait_until_ready()
            dt_now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

            if dt_now.hour == self.auto_process_hour and dt_now.minute == self.auto_pocess_minute:
                logger.debug("Performing auto channel processing")
                for guild in self.discord_client.guilds:
                    for channel in guild.text_channels:
                        if channel.name[:4] == "auto":
                            self.to_process.add(channel)

            # Date range calculation
            since: datetime.datetime = dt_now - datetime.timedelta(days=3)
            until: datetime.datetime = dt_now - datetime.timedelta(days=2)
            since_string: str = datetime.datetime.strftime(since, "%Y%m%d%H%M%S")
            until_string: str = datetime.datetime.strftime(until, "%Y%m%d%H%M%S")

            processed: set[TextChannel] = set()
            for channel in self.to_process:
                query: arxiv.Search | None = parse(
                    (channel.topic or "") + f" since:{since_string} until:{until_string}",
                )

                if query is None:
                    logger.warning("Invalid query for channel: %s", channel.name)
                    processed.add(channel)
                    await channel.send("Invalid query")
                    continue

                query.max_results = None
                result = self.arxiv_client.results(query)
                return_list: list[str] = self._process_results(result)

                processed.add(channel)
                await self._send_results(channel, return_list)

            for channel in processed:
                self.to_process.remove(channel)

        except Exception:
            logger.exception("Error in loop method")

    async def on_message(self, message: Message) -> None:
        try:
            if message.author.bot:
                return

            if self.discord_client.user not in message.mentions:
                return

            logger.info("Received message from %s: %s", message.author, message.content)

            query: arxiv.Search | None = parse(message.content)
            if query is None:
                logger.warning("Invalid query from %s", message.author)
                await message.channel.send("Invalid query")
                return

            result = self.arxiv_client.results(query)
            return_list: list[str] = self._process_results(result)

            await self._send_results(message.channel, return_list)

        except Exception:
            logger.exception("Found an error")

    def _process_results(self, result: Generator[arxiv.Result]) -> list[str]:
        return_list: list[str] = [""]
        for r in result:
            next_content: str = r.title + "\n<" + str(r) + ">\n"
            if len(return_list[-1]) + len(next_content) > self.MESSEAGE_THRESHOLD_LENGTH:
                return_list.append(next_content)
            else:
                return_list[-1] += next_content
        return return_list

    async def _send_results(self, channel: discord.abc.Messageable, return_list: list[str]) -> None:
        sent: bool = False
        for ret in return_list:
            if len(ret) > 0:
                await channel.send(ret[:-1])  # remove last \n
                sent = True

        if not sent:
            logger.info("No results found")
            await channel.send("No results found")

    def run(self) -> None:
        try:
            logger.info("Starting bot...")
            self.discord_client.run(self.config["token"])
        except (discord.LoginFailure, discord.HTTPException, discord.ConnectionClosed) as e:
            logger.critical("Bot startup failed: %s", e, exc_info=True)


def main() -> None:
    bot: ArxivDiscordBot = ArxivDiscordBot()
    bot.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

#!/usr/bin/env python3
"""Register Discord slash commands"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def register_slash_command():
    """Register /arxiv slash command with Discord"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)

    # Get application ID from token
    headers = {"Authorization": f"Bot {bot_token}"}

    async with httpx.AsyncClient() as client:
        # Get current application info
        response = await client.get(
            "https://discord.com/api/v10/applications/@me",
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Error getting application info: {response.status_code}")
            print(response.text)
            sys.exit(1)

        app_data = response.json()
        app_id = app_data["id"]
        print(f"Application ID: {app_id}")

        # Register slash command
        command_data = {
            "name": "arxiv",
            "description": "Search arXiv papers",
            "options": [
                {
                    "name": "query",
                    "description": "Search query (e.g., 'ti:machine,learning 20 s since:20240101')",
                    "type": 3,  # STRING
                    "required": True,
                },
            ],
        }

        response = await client.post(
            f"https://discord.com/api/v10/applications/{app_id}/commands",
            headers=headers,
            json=command_data,
        )

        if response.status_code in (200, 201):
            print("✅ Successfully registered /arxiv command!")
            print(response.json())
        else:
            print(f"❌ Error registering command: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(register_slash_command())

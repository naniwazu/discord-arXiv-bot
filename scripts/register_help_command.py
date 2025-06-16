#!/usr/bin/env python3
"""Register help command for the new query syntax"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def register_help_command():
    """Register /arxiv-help command"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)

    headers = {"Authorization": f"Bot {bot_token}"}

    async with httpx.AsyncClient() as client:
        # Get application info
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

        # Register both commands
        commands = [
            {
                "name": "arxiv",
                "description": "Search arXiv papers with advanced query syntax",
                "options": [
                    {
                        "name": "query",
                        "description": "Search query. Use /arxiv-help for syntax guide",
                        "type": 3,  # STRING
                        "required": True,
                    },
                ],
            },
            {
                "name": "arxiv-help",
                "description": "Show advanced query syntax guide and examples",
            }
        ]

        for command_data in commands:
            response = await client.post(
                f"https://discord.com/api/v10/applications/{app_id}/commands",
                headers=headers,
                json=command_data,
            )

            if response.status_code in (200, 201):
                print(f"✅ Successfully registered /{command_data['name']} command!")
            else:
                print(f"❌ Error registering /{command_data['name']} command: {response.status_code}")
                print(response.text)


if __name__ == "__main__":
    asyncio.run(register_help_command())
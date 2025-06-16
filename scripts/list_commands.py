#!/usr/bin/env python3
"""List all existing Discord slash commands"""

import asyncio
import os
import sys
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def list_commands():
    """List all existing Discord slash commands"""
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
        app_name = app_data.get("name", "Unknown")
        
        print(f"Application: {app_name}")
        print(f"Application ID: {app_id}")
        print()

        # Get existing commands
        response = await client.get(
            f"https://discord.com/api/v10/applications/{app_id}/commands",
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Error getting commands: {response.status_code}")
            print(response.text)
            sys.exit(1)

        commands = response.json()
        
        if not commands:
            print("📭 No slash commands are currently registered")
            return

        print(f"📋 Found {len(commands)} registered command(s):")
        print("=" * 60)

        for i, cmd in enumerate(commands, 1):
            print(f"{i}. /{cmd['name']}")
            print(f"   Description: {cmd.get('description', 'No description')}")
            print(f"   ID: {cmd['id']}")
            
            # Show options if any
            options = cmd.get('options', [])
            if options:
                print(f"   Options:")
                for opt in options:
                    required = " (required)" if opt.get('required') else ""
                    print(f"     - {opt['name']}: {opt.get('description', 'No description')}{required}")
            
            # Show version if available
            if 'version' in cmd:
                print(f"   Version: {cmd['version']}")
            
            print()

        print("💡 To update commands, run:")
        print("   python scripts/cleanup_all_commands.py  # Remove all")
        print("   python scripts/update_commands.py       # Add new command")
        print()
        
        # Generate invite link
        permissions = 2147485696  # Send Messages, Use Slash Commands, View Channels
        invite_url = (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={app_id}"
            f"&permissions={permissions}"
            f"&scope=bot%20applications.commands"
        )
        print("🔗 Bot invite link:")
        print(f"   {invite_url}")


if __name__ == "__main__":
    print("📋 Discord Command Lister")
    print("=" * 30)
    print()
    asyncio.run(list_commands())
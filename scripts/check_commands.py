#!/usr/bin/env python3
"""Check registered Discord slash commands"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def check_commands():
    """Check registered slash commands"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)
    
    headers = {"Authorization": f"Bot {bot_token}"}
    
    async with httpx.AsyncClient() as client:
        # Get application info
        response = await client.get(
            "https://discord.com/api/v10/applications/@me",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error getting application info: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        app_data = response.json()
        app_id = app_data["id"]
        print(f"Application ID: {app_id}")
        print(f"Application Name: {app_data['name']}")
        
        # Get global commands
        print("\n=== Global Commands ===")
        response = await client.get(
            f"https://discord.com/api/v10/applications/{app_id}/commands",
            headers=headers
        )
        
        if response.status_code == 200:
            commands = response.json()
            if commands:
                for cmd in commands:
                    print(f"- /{cmd['name']}: {cmd['description']}")
            else:
                print("No global commands registered")
        else:
            print(f"Error fetching commands: {response.status_code}")
            print(response.text)
        
        # Generate invite link
        print(f"\n=== Bot Invite Link ===")
        # Permissions: Send Messages (2048) + Use Slash Commands (2147483648)
        permissions = 2048 + 2147483648
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={permissions}&scope=bot%20applications.commands"
        print(f"Invite URL: {invite_url}")


if __name__ == "__main__":
    asyncio.run(check_commands())
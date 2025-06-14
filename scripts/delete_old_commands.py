#!/usr/bin/env python3
"""Delete old Discord slash commands"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def delete_old_commands():
    """Delete the old /arxiv_search command"""
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
        
        # Get all global commands
        response = await client.get(
            f"https://discord.com/api/v10/applications/{app_id}/commands",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error fetching commands: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        commands = response.json()
        print("\nCurrent commands:")
        for cmd in commands:
            print(f"- /{cmd['name']} (ID: {cmd['id']})")
        
        # Delete only the old /arxiv_search command
        deleted = False
        for cmd in commands:
            if cmd['name'] == 'arxiv_search':
                print(f"\nDeleting old command: /{cmd['name']}")
                response = await client.delete(
                    f"https://discord.com/api/v10/applications/{app_id}/commands/{cmd['id']}",
                    headers=headers
                )
                if response.status_code == 204:
                    print(f"✅ Successfully deleted /{cmd['name']}")
                    deleted = True
                else:
                    print(f"❌ Failed to delete /{cmd['name']}: {response.status_code}")
                    print(response.text)
        
        if not deleted:
            print("\n❌ No /arxiv_search command found to delete")
        
        # Show remaining commands
        print("\nRefreshing command list...")
        response = await client.get(
            f"https://discord.com/api/v10/applications/{app_id}/commands",
            headers=headers
        )
        
        if response.status_code == 200:
            commands = response.json()
            print("\nRemaining commands:")
            for cmd in commands:
                print(f"- /{cmd['name']}")
        

if __name__ == "__main__":
    asyncio.run(delete_old_commands())
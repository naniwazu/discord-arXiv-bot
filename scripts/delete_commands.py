#!/usr/bin/env python3
"""Delete Discord slash commands"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def delete_commands():
    """Delete specified slash commands"""
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
        if not commands:
            print("No commands found to delete")
            return
        
        print("\nFound commands:")
        for i, cmd in enumerate(commands):
            print(f"{i+1}. /{cmd['name']} (ID: {cmd['id']})")
        
        # Ask which command to delete
        print("\nWhich command do you want to delete?")
        print("Enter the number, 'all' to delete all, or 'cancel' to exit:")
        
        choice = input("> ").strip().lower()
        
        if choice == 'cancel':
            print("Cancelled")
            return
        
        if choice == 'all':
            for cmd in commands:
                response = await client.delete(
                    f"https://discord.com/api/v10/applications/{app_id}/commands/{cmd['id']}",
                    headers=headers
                )
                if response.status_code == 204:
                    print(f"✅ Deleted /{cmd['name']}")
                else:
                    print(f"❌ Failed to delete /{cmd['name']}: {response.status_code}")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(commands):
                    cmd = commands[idx]
                    response = await client.delete(
                        f"https://discord.com/api/v10/applications/{app_id}/commands/{cmd['id']}",
                        headers=headers
                    )
                    if response.status_code == 204:
                        print(f"✅ Deleted /{cmd['name']}")
                    else:
                        print(f"❌ Failed to delete /{cmd['name']}: {response.status_code}")
                else:
                    print("Invalid number")
            except ValueError:
                print("Invalid input")


if __name__ == "__main__":
    asyncio.run(delete_commands())
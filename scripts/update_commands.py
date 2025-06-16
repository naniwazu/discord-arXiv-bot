#!/usr/bin/env python3
"""Update Discord slash commands with new query syntax"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


async def get_application_info(client: httpx.AsyncClient, headers: dict) -> dict:
    """Get current application info"""
    response = await client.get(
        "https://discord.com/api/v10/applications/@me",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"Error getting application info: {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()


async def get_existing_commands(client: httpx.AsyncClient, app_id: str, headers: dict) -> list:
    """Get list of existing commands"""
    response = await client.get(
        f"https://discord.com/api/v10/applications/{app_id}/commands",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"Error getting existing commands: {response.status_code}")
        print(response.text)
        return []

    return response.json()


async def delete_command(client: httpx.AsyncClient, app_id: str, command_id: str, headers: dict) -> bool:
    """Delete a specific command"""
    response = await client.delete(
        f"https://discord.com/api/v10/applications/{app_id}/commands/{command_id}",
        headers=headers,
    )

    return response.status_code == 204


async def register_new_command(client: httpx.AsyncClient, app_id: str, headers: dict) -> bool:
    """Register the updated /arxiv command with new syntax"""
    command_data = {
        "name": "arxiv",
        "description": "Search arXiv papers with advanced query syntax",
        "options": [
            {
                "name": "query",
                "description": "Advanced search query. Examples: 'quantum | neural', '@hinton #cs.AI', '(bert | gpt) 50 sa'",
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
        print("✅ Successfully registered new /arxiv command!")
        return True
    else:
        print(f"❌ Error registering new command: {response.status_code}")
        print(response.text)
        return False


async def update_slash_commands():
    """Update Discord slash commands with new query syntax"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        sys.exit(1)

    headers = {"Authorization": f"Bot {bot_token}"}

    async with httpx.AsyncClient() as client:
        # Get application info
        app_data = await get_application_info(client, headers)
        app_id = app_data["id"]
        app_name = app_data.get("name", "Unknown")
        
        print(f"Application: {app_name} (ID: {app_id})")
        print()

        # Get existing commands
        print("🔍 Checking existing commands...")
        existing_commands = await get_existing_commands(client, app_id, headers)
        
        if existing_commands:
            print(f"Found {len(existing_commands)} existing command(s):")
            for cmd in existing_commands:
                print(f"  - {cmd['name']}: {cmd['description']}")
            print()

            # Delete all existing commands (arxiv, アーカイブサーチ, etc.)
            deleted_count = 0
            commands_to_delete = ["arxiv", "アーカイブサーチ", "arxiv-help"]
            
            for cmd in existing_commands:
                if cmd["name"] in commands_to_delete or "arxiv" in cmd["name"].lower() or "アーカイブ" in cmd["name"]:
                    print(f"🗑️  Deleting command: /{cmd['name']} (ID: {cmd['id']})...")
                    if await delete_command(client, app_id, cmd["id"], headers):
                        print("   ✅ Successfully deleted")
                        deleted_count += 1
                    else:
                        print("   ❌ Failed to delete")
            
            if deleted_count > 0:
                print(f"Deleted {deleted_count} old command(s)")
                # Wait a moment for Discord to process the deletion
                print("⏳ Waiting for Discord to process deletion...")
                await asyncio.sleep(2)
            print()
        else:
            print("No existing commands found")
            print()

        # Register new command
        print("📝 Registering new /arxiv command with advanced syntax...")
        success = await register_new_command(client, app_id, headers)
        
        if success:
            print()
            print("🎉 Command update completed successfully!")
            print()
            print("📖 New query syntax examples:")
            print("   Basic: quantum computing")
            print("   OR search: quantum | neural")
            print("   NOT search: quantum -classical")
            print("   Field search: @hinton #cs.AI")
            print("   Grouping: (bert | gpt) @google 50 sa")
            print("   Complex: (#cs.AI | #cs.LG) machine learning -survey")
            print()
            print("🔗 Bot invite link:")
            
            # Generate invite link
            permissions = 2147485696  # Send Messages, Use Slash Commands, View Channels
            invite_url = (
                f"https://discord.com/api/oauth2/authorize"
                f"?client_id={app_id}"
                f"&permissions={permissions}"
                f"&scope=bot%20applications.commands"
            )
            print(f"   {invite_url}")
        else:
            print("❌ Failed to register new command")
            sys.exit(1)


if __name__ == "__main__":
    print("🤖 Discord arXiv Bot - Command Updater")
    print("=" * 50)
    print()
    asyncio.run(update_slash_commands())
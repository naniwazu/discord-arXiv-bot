#!/usr/bin/env python3
"""Delete ALL existing Discord slash commands for clean slate"""

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


async def get_all_commands(client: httpx.AsyncClient, app_id: str, headers: dict) -> list:
    """Get all existing commands"""
    response = await client.get(
        f"https://discord.com/api/v10/applications/{app_id}/commands",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"Error getting commands: {response.status_code}")
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


async def cleanup_all_commands():
    """Delete ALL existing Discord slash commands"""
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

        # Get all existing commands
        print("🔍 Fetching all existing commands...")
        all_commands = await get_all_commands(client, app_id, headers)
        
        if not all_commands:
            print("✅ No commands found - already clean!")
            return

        print(f"Found {len(all_commands)} command(s) to delete:")
        for cmd in all_commands:
            print(f"  - /{cmd['name']}: {cmd.get('description', 'No description')}")
        print()

        # Confirm deletion
        confirmation = input("❓ Are you sure you want to delete ALL commands? (yes/no): ").strip().lower()
        if confirmation not in ["yes", "y"]:
            print("❌ Cancelled - no commands were deleted")
            return

        print()
        print("🗑️  Deleting all commands...")

        deleted_count = 0
        failed_count = 0

        for cmd in all_commands:
            print(f"   Deleting /{cmd['name']} (ID: {cmd['id']})...", end=" ")
            
            if await delete_command(client, app_id, cmd["id"], headers):
                print("✅")
                deleted_count += 1
            else:
                print("❌")
                failed_count += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        print()
        print(f"📊 Results:")
        print(f"   Successfully deleted: {deleted_count}")
        print(f"   Failed to delete: {failed_count}")
        
        if deleted_count > 0:
            print()
            print("✅ Cleanup completed! All commands have been removed.")
            print("💡 You can now run update_commands.py to register the new command.")
        else:
            print("❌ No commands were deleted.")


if __name__ == "__main__":
    print("🧹 Discord Command Cleanup Tool")
    print("=" * 40)
    print("⚠️  WARNING: This will delete ALL slash commands!")
    print()
    asyncio.run(cleanup_all_commands())
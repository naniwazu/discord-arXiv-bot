# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- `poetry install` - Install dependencies
- `poetry run python src/webhook_server.py` - Run the webhook server
- `poetry run python src/scheduler.py` - Run scheduler manually
- `poetry run ruff check` - Run linting
- `poetry run ruff format` - Format code

### Environment Variables
- `DISCORD_BOT_TOKEN` - Discord bot token
- `DISCORD_PUBLIC_KEY` - Discord application public key (for webhook signature verification)
- `PORT` - Server port (default: 8000)

## Architecture

This is a serverless Discord bot that searches and shares arXiv research papers using webhooks and slash commands.

### Core Components
1. **webhook_server.py** - FastAPI server handling Discord slash command interactions
2. **scheduler.py** - Separate service for auto-channel processing
3. **tools.py** - Query parser for arXiv search syntax

### Key Features
1. **Slash Commands**: `/arxiv query` - Interactive search with slash commands
2. **Auto Search**: Channels starting with "auto" get daily automated searches via scheduler
3. **Query Format**: Supports arXiv field prefixes (ti, au, abs, cat, etc.), result limits (1-1000), sort options (r/s/l), and date ranges

### Webhook Flow
1. Discord sends POST to `/interactions` endpoint
2. Signature verification using `DISCORD_PUBLIC_KEY`
3. Query parsing via `parse()` function
4. arXiv API search execution
5. Response formatting and return to Discord

### Scheduler Flow
1. Cron job hits `/scheduler` endpoint (or runs scheduler.py directly)
2. Fetches all channels starting with "auto" via Discord API
3. Uses channel topic as search query with date range (48-72 hours ago)
4. Posts results directly to channels via Discord API

### Deployment Options
- **Railway**: Use `railway.toml` and `Dockerfile`
- **Vercel**: Use `vercel.json` with serverless functions
- **Any container platform**: Use `Dockerfile`

### Time Handling
All date inputs are treated as JST (UTC-9). Auto-processing searches papers from 48-72 hours ago to account for arXiv's publication schedule.

## Deployment Status

### Railway Configuration (COMPLETED)
- **URL**: https://discord-arxiv-bot-production.up.railway.app
- **Environment Variables**: DISCORD_BOT_TOKEN, DISCORD_PUBLIC_KEY, PORT
- **Interactions Endpoint**: https://discord-arxiv-bot-production.up.railway.app/interactions
- **Health Check**: /health endpoint available
- **Debug Endpoint**: /debug endpoint for troubleshooting

### Discord Application Setup (COMPLETED)
- Discord Developer Portal configuration completed
- Interactions Endpoint URL validated and authenticated
- Bot permissions: Send Messages, Use Slash Commands
- Environment variables properly loaded and verified

### Setup Complete (2025-06-14)
1. **Slash Command Registration**: ✅ `/arxiv` command registered globally
2. **Auto-Search Cron**: 
   - Option A: Use Railway's native Cron Schedule feature in service settings
   - Set cron expression: `0 21 * * *` (21:00 UTC daily)
   - Create separate service that runs `python src/scheduler.py` and exits
   - Option B: Keep webhook server running and use external service to call `/scheduler` endpoint
3. **Bot Status**: Webhook bot appears "offline" in Discord - this is normal for interaction-based bots

### Helper Scripts
- `scripts/register_commands.py` - Register slash commands
- `scripts/check_commands.py` - Check registered commands and get invite link
- `scripts/delete_old_commands.py` - Delete old/unused commands

### Troubleshooting Notes
- Environment variables load correctly (verified via /debug endpoint)
- Signature verification works when DISCORD_PUBLIC_KEY is set
- Use `curl /debug` to check environment variable status
- Railway logs show startup and request information
- Bot invite link: Use the URL from `check_commands.py` output
- If slash commands don't appear: Re-invite bot, wait a few minutes, refresh Discord (Ctrl+R)

### Railway Cron Schedule Setup
1. **For Native Railway Cron**:
   - Create new Railway service for scheduler
   - In service Settings, set Cron Schedule: `0 21 * * *`
   - Set Start Command: `python src/scheduler.py`
   - Add environment variable: `DISCORD_BOT_TOKEN`
   - Service must exit after task completion
2. **Important**: Cron runs are based on UTC time
3. **Minimum interval**: 5 minutes between executions

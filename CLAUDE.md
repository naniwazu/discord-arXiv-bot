# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- `uv sync` - Install dependencies (preferred)
- `uv run python src/webhook_server.py` - Run the webhook server
- `uv run python src/scheduler.py` - Run scheduler manually
- `uv run ruff check` - Run linting
- `uv run ruff format` - Format code

#### Legacy (Poetry)
- `poetry install` - Install dependencies (legacy)
- `poetry run python src/webhook_server.py` - Run the webhook server (legacy)

### Environment Variables
- `DISCORD_BOT_TOKEN` - Discord bot token
- `DISCORD_PUBLIC_KEY` - Discord application public key (for webhook signature verification)
- `DISCORD_APPLICATION_ID` - Discord application ID (for followup messages)
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
- **Important**: DISCORD_APPLICATION_ID required for deferred responses

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

### Recent Updates (2025-01-15)
1. **Deferred Response Implementation**
   - Switched from immediate response (type 4) to deferred response (type 5)
   - Solves Discord's 3-second timeout issue completely
   - Allows unlimited search results
   - Requires DISCORD_APPLICATION_ID environment variable

2. **Getting Discord Application ID**
   - Go to https://discord.com/developers/applications
   - Select your application
   - Copy Application ID from General Information tab
   - Add to Railway environment variables

3. **Current Architecture**
   - Webhook server immediately returns "thinking..." response
   - Background task fetches arXiv results without time limit
   - Results sent via Discord Followup API
   - Multiple messages automatically split if needed

### Deployment Checklist
1. Ensure all environment variables are set in Railway:
   - DISCORD_BOT_TOKEN
   - DISCORD_PUBLIC_KEY  
   - DISCORD_APPLICATION_ID (required for deferred responses)
2. Region should be set to asia-southeast1 (Singapore) for Japan users
3. For scheduler service: Set Cron Schedule to `0 21 * * *` in Railway settings
4. Run `uvx ruff check src/` before deployment to check code quality

### Railway Cron Schedule Setup
1. **For Native Railway Cron**:
   - Create new Railway service for scheduler
   - In service Settings, set Cron Schedule: `0 21 * * *`
   - Set Start Command: `python src/scheduler.py`
   - Add environment variable: `DISCORD_BOT_TOKEN`
   - Service must exit after task completion
2. **Important**: Cron runs are based on UTC time
3. **Minimum interval**: 5 minutes between executions

## Migration to UV (2025-01-16)

### Package Management Migration
- **From**: Poetry → **To**: UV (for faster builds and dependency management)
- **Configuration**: Standard pyproject.toml format (PEP 621)
- **Lock file**: uv.lock replaces poetry.lock
- **Speed improvement**: 10-100x faster dependency resolution and installation

### UV Setup
```bash
# Create virtual environment
uv venv

# Install dependencies
uv sync

# Run commands
uv run python src/webhook_server.py
uv run pytest tests/
uv run ruff check src/
```

## Git Workflow Best Practices

### Destructive Operations Safety
**CRITICAL**: Always confirm before executing destructive git operations that could lose work.

#### High-Risk Commands Requiring Confirmation
- `git reset --hard` - **ALWAYS confirm branch and backup status first**
- `git push --force-with-lease` - Verify you're on the correct branch
- `git rebase -i` - Ensure you understand the scope of changes
- `git clean -fd` - Could delete untracked files permanently

#### Pre-Destructive Operation Checklist
1. **Verify Current Branch**: `git branch` - Make sure you're on the intended branch
2. **Check Remote Status**: `git status` - Ensure work is pushed or backed up
3. **List Recent Commits**: `git log --oneline -5` - Know what you're potentially losing
4. **Backup if Needed**: Create backup branch if work isn't pushed
5. **Double-Check Target**: For reset operations, verify the target commit hash

#### Safe Recovery Practices
- **Remote Backup**: Ensure important work is pushed to remote before destructive operations
- **Reflog Usage**: `git reflog` can recover lost commits (limited time window)
- **Branch Protection**: Use feature branches; keep main branch stable

#### Example Safe Reset Workflow
```bash
# BEFORE destructive operation
git branch                          # Confirm current branch
git status                         # Check if work is committed/pushed
git log --oneline -5              # See recent commits
git push origin feature-branch    # Backup current work

# THEN proceed with reset
git reset --hard <target-commit>
```

#### Lessons Learned (2025-01-16)
- **Always push feature branch work before reset operations**
- **Confirm target branch before running `git reset --hard`**
- **Use `git fetch origin` + `git reset --hard origin/branch` to restore from remote**
- **Destructive operations on wrong branch can lose hours of work instantly**

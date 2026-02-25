# Quick Start Guide

Get up and running with Team Context in 5 minutes.

## 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Get Your Tokens/Keys

### For Slack:
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Team Context Collector"
4. Select your workspace
5. Go to "OAuth & Permissions"
6. Under "Scopes", add:
   - `channels:history`
   - `users:read`
7. Reinstall the app
8. Copy "Bot User OAuth Token" (starts with `xoxb-`)

### For Discord:
1. Go to https://discord.com/developers/applications
2. Click "New Application" → name it
3. Go to "Bot" tab
4. Click "Add Bot"
5. Under "Privileged Gateway Intents" enable:
   - Message Content Intent
   - Server Members Intent
6. Copy the token

### For Notion:
1. Go to https://www.notion.so/my-integrations
2. Click "Create new integration"
3. Name: "Team Context"
4. Copy "Internal Integration Token" (starts with `secret_`)
5. Go to any Notion page and share it with your integration

## 3. Configure `config.yaml`

Only fill in what you want to use:

```yaml
# SLACK (optional)
slack:
  enabled: true
  bot_token: "xoxb-your-token-here"
  channels: ["#general", "#engineering", "#design"]

# DISCORD (optional)
discord:
  enabled: false
  bot_token: ""
  servers: []

# NOTION (optional)
notion:
  enabled: true
  api_key: "secret_your-notion-key-here"
  pages: ["Architecture", "API Docs", "Decisions"]
```

## 4. Run Initial Setup

```bash
python setup.py
```

This will:
- ✓ Verify your config
- ✓ Connect to your platforms
- ✓ Pull in 30 days of history
- ✓ Build the search index

**Output:**
```
========================================================
  Team Context Collector - Initial Setup
========================================================

Step 1: Loading configuration...
  ✓ Configuration loaded from config.yaml

Step 2: Validating configuration...
  ✓ Configuration is valid

Step 3: Running collection setup...
Team Context Collector Setup
==================================================
Collecting from enabled platforms...
  slack: 450 items collected
  notion: 12 items collected

Building search index...

Total items indexed: 462
Setup complete!

========================================================
  Setup Complete!
========================================================

Next steps:
  1. Start the dashboard: python server.py
  2. View at: http://localhost:8000
  3. Add to Claude Code config (see README for instructions)
```

## 5. Start the Dashboard

```bash
python server.py
```

Open http://localhost:8000 in your browser. You'll see:
- **Statistics**: Total items indexed, breakdown by source
- **Search**: Test search to verify everything works
- **Management**: Buttons to re-collect or rebuild index

## 6. Integrate with Claude Code

Add this to your Claude Code config (check docs for exact location):

```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/Users/yourname/codbot"  // Use your actual path
    }
  }
}
```

Then in Claude Code:
```bash
/help mcp
# You should see "team-context" listed
```

## 7. Test It

Now when you ask Claude Code to help with code, it will automatically search your team context.

Example in Claude Code:
```
I'm implementing authentication. Here's my current code:
[paste code]
Help me implement this the way we decided as a team.
```

Claude Code will:
1. Search your context for "authentication"
2. Find relevant Slack threads and Notion docs
3. Use those to guide the implementation

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'slack_sdk'` | Did you run `pip install -r requirements.txt`? |
| "Slack token not working" | Verify token format starts with `xoxb-` and has correct scopes |
| No results in dashboard search | Run setup.py again to ensure collection worked |
| MCP server not showing in Claude Code | Check config file syntax (JSON), restart Claude Code |

## What's Happening

1. **Collection**: `python setup.py` reads 30 days from your platforms and saves them locally
2. **Indexing**: Converts all messages to embeddings for fast semantic search
3. **Dashboard**: Shows stats and lets you test search at http://localhost:8000
4. **MCP Server**: When Claude Code asks for context, it searches locally and returns relevant items
5. **Integration**: Claude Code includes that context when helping you code

All data stays on your machine. No uploads, no tracking.

## Next Steps

- Read full [README.md](README.md) for detailed docs
- Check [config.yaml](config.yaml) for all options
- Run `pytest tests/` to verify installation
- Adjust `indexing.lookback_days` if you want more history
- Set `search.top_k` higher if you want more results

## Need Help?

Check the README.md FAQ section or feel free to report issues!

# Team Context Collector for Claude Code

A zero-cost tool that brings context from your team's Slack, Discord, and Notion directly into Claude Code. When you're coding, Claude Code automatically has access to relevant messages, discussions, and documentation your team has already written.

---

## 🚀 Ultra-Simple Setup (No Technical Knowledge Required)

**What you need:** Just Python (which you probably have). That's it.

### Copy & Paste These Commands

Open your terminal and run these 4 commands (one at a time):

```bash
# 1. Download the project
git clone https://github.com/romirthedev/codbot.git && cd codbot

# 2. Install everything needed
pip install -r requirements.txt

# 3. [Edit config.yaml] - Add your Slack/Discord/Notion tokens (see instructions below)

# 4. Start it up
python setup.py
```

That's it! Then open http://localhost:8000 in your browser.

### Getting Your Tokens (Copy & Paste URLs)

**Slack?** Go here: https://api.slack.com/apps → Create App → Copy bot token → Paste in config.yaml

**Discord?** Go here: https://discord.com/developers/applications → New App → Copy token → Paste in config.yaml

**Notion?** Go here: https://www.notion.so/my-integrations → New Integration → Copy token → Paste in config.yaml

### Edit config.yaml

Open `config.yaml` in any text editor and add your tokens:

```yaml
slack:
  enabled: true
  bot_token: "PASTE_YOUR_TOKEN_HERE"
  channels: ["#general", "#engineering"]
```

**That's all you need to do.** No coding, no technical stuff.

### Next Steps

- Run `python setup.py` (waits ~30 seconds, then done)
- Visit http://localhost:8000 and watch it work
- Follow MCP_SETUP.md to connect with Claude Code

**Questions?** Every single token URL is in the guide above. Just click them.

---

## Architecture

The system has three main components:

### 1. **The Collector**
Pulls messages and docs from Slack, Discord, and Notion into local plain text files (`/context-store/`).

### 2. **The Brain** (Relevance Search)
Uses free local embeddings (`sentence-transformers`) and vector search (`chromadb`) to figure out what's relevant to what you're currently coding.

### 3. **The Bridge** (MCP Server)
Runs an MCP (Model Context Protocol) server that Claude Code talks to, feeding it relevant context automatically.

## Installation

### Prerequisites
- Python 3.10+
- Virtual environment (optional but recommended)

### Setup Steps

1. **Clone and install dependencies:**
```bash
cd codbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure your platforms in `config.yaml`:**

```yaml
# For Slack
slack:
  enabled: true
  bot_token: "xoxb-your-bot-token"  # Get from https://api.slack.com/apps
  channels: ["#general", "#engineering"]

# For Discord
discord:
  enabled: true
  bot_token: "your-bot-token"  # Get from https://discord.com/developers/applications
  servers:
    - server: "My Dev Server"
      channels: ["general", "tech-discussion"]

# For Notion
notion:
  enabled: true
  api_key: "secret_your-notion-api-key"  # Get from https://www.notion.so/my-integrations
  pages: ["Architecture Decisions", "API Documentation"]
```

3. **Authenticate and perform initial collection:**
```bash
python setup.py
```

This will:
- Validate your configuration
- Connect to Slack/Discord/Notion
- Pull in 30 days of messages/documents
- Build the search index (embeddings)

## Usage

### Starting the Dashboard
```bash
python server.py
```
Visit http://localhost:8000 to see:
- Statistics on indexed messages
- Manual search testing
- Buttons to re-collect or rebuild the index

### Integrating with Claude Code

#### Option 1: Using the MCP Server (Recommended)

Add this to your Claude Code configuration file (`.claude/config.json` or wherever Claude Code stores config):

```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/path/to/codbot"
    }
  }
}
```

Now when you use Claude Code on any code file, it will automatically search your team context and include relevant information in its reasoning.

#### Option 2: Manual Integration

You can also manually call the context search in Claude Code:
```python
from src.search import RelevanceSearch
from src.storage import ContextStorage

storage = ContextStorage()
search = RelevanceSearch(storage)
results = search.search("authentication", top_k=10)
```

## Understanding the Cost

✅ **Completely Free:**
- `sentence-transformers`: Free embedding model, runs locally
- `chromadb`: Free vector database, runs locally
- Slack API: Free tier is sufficient
- Discord API: Free bot API
- Notion API: Free integration API

❌ **No Paid Services:**
- No cloud databases
- No external API calls
- No hosting needed
- Runs entirely on your machine

## How It Works

### Collection Flow
1. **Slack Collector**: Uses Slack SDK to fetch messages from configured channels
2. **Discord Collector**: Uses Discord.py to fetch messages (async-based)
3. **Notion Collector**: Uses Notion SDK to fetch pages and documents

All messages/docs are stored as JSON in `/context-store/` with metadata.

### Search Flow
1. When you ask Claude Code to work on code, it calls the MCP server with the current file/context
2. The server generates embeddings for your code using `sentence-transformers`
3. It queries the `chromadb` vector database for similar items
4. Returns the top K most relevant messages/docs
5. Claude Code includes these in its reasoning

### Example

You're implementing JWT authentication:
```python
# Your current code
def login(username: str, password: str):
    # Need to implement JWT logic
    pass
```

Claude Code sends this to the MCP server, which:
1. Embeds this code snippet
2. Searches stored context for similar content
3. Finds 6 months old Slack thread where team discussed "JWT implementation decisions"
4. Returns that thread to Claude Code
5. Claude Code implements JWT exactly how your team decided

## API Reference

### Config File (`config.yaml`)

All settings are optional. The tool works without any config, using sensible defaults.

```yaml
slack:
  enabled: bool              # Enable Slack collection
  bot_token: str            # Slack bot token (required if enabled)
  channels: [str]           # List of channels to monitor

discord:
  enabled: bool             # Enable Discord collection
  bot_token: str            # Discord bot token (required if enabled)
  servers:                  # List of servers
    - server: str           # Server name
      channels: [str]       # Channels in that server

notion:
  enabled: bool             # Enable Notion collection
  api_key: str              # Notion API key (required if enabled)
  pages: [str]              # Page titles to monitor

indexing:
  lookback_days: int        # Days of history to collect (default: 30)
  sync_interval: int        # Minutes between re-syncs (default: 60)

search:
  top_k: int               # Default number of results (default: 10)
  similarity_threshold: float  # Min similarity score 0-1 (default: 0.5)
```

### Python API

#### ContextStorage
```python
from src.storage import ContextStorage, ContextItem

storage = ContextStorage()
items = storage.load_all_items()
storage.save_items(items, source="slack")
```

#### RelevanceSearch
```python
from src.search import RelevanceSearch

search = RelevanceSearch(storage)
results = search.search("query text", top_k=10, threshold=0.5)
# Returns: [(ContextItem, similarity_score), ...]

formatted = search.search_with_context(code_content, top_k=10)
# Returns: [formatted_string, ...]
```

#### CollectorManager
```python
from src.collector_manager import CollectorManager
from src.config import load_config

config = load_config()
manager = CollectorManager(config)

# Collect from all platforms
results = manager.collect_all()

# Reindex for search
manager.reindex()

# Get statistics
stats = manager.get_stats()
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

Tests cover:
- Configuration loading and validation
- Storage operations (save/load)
- Embedding and search
- Context item creation and serialization

## Troubleshooting

### "Module not found" errors
Make sure you're running from the project root and have installed dependencies:
```bash
pip install -r requirements.txt
```

### Slack token not working
1. Go to https://api.slack.com/apps and create an app
2. Under "OAuth & Permissions", add these scopes:
   - `channels:history` - read channel messages
   - `users:read` - read user info
   - `groups:history` - read private channel messages
3. Copy the "Bot User OAuth Token"

### Discord bot not collecting messages
Discord.py requires intents to be enabled:
1. Go to https://discord.com/developers/applications
2. Select your bot
3. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent

### Notion pages not found
1. Make sure the page titles in config.yaml exactly match your Notion pages
2. Verify the Notion integration has access to those pages
3. Check that pages are shared with the integration

## Development

### Project Structure
```
codbot/
├── src/
│   ├── collectors/        # Platform-specific collectors
│   │   ├── slack.py
│   │   ├── discord.py
│   │   └── notion.py
│   ├── config.py          # Configuration management
│   ├── storage.py         # Local context storage
│   ├── search.py          # Semantic search with embeddings
│   ├── mcp_server.py      # MCP protocol handler
│   ├── dashboard.py       # Web UI
│   └── collector_manager.py
├── tests/                 # Unit tests
├── config.yaml            # Configuration file
├── setup.py              # Initial setup script
├── server.py             # Dashboard server
└── README.md
```

### Adding a New Platform

1. Create `src/collectors/newplatform.py`
2. Extend `BaseCollector`:
```python
from src.collectors.base import BaseCollector

class NewPlatformCollector(BaseCollector):
    @property
    def source(self) -> str:
        return "newplatform"

    def collect(self):
        # Your collection logic
        pass
```
3. Add to `src/collectors/__init__.py`
4. Add config section in `config.yaml`
5. Integrate in `src/collector_manager.py`

## License

MIT - Use for any purpose

## Contributing

PRs welcome! Areas for improvement:
- Async Discord collection
- Scheduled background collection
- Web-based auth flow for tokens
- Better search ranking with date/importance
- Export context to markdown

## FAQ

**Q: Does this upload my data anywhere?**
A: No. Everything stays on your machine. No cloud storage, no external APIs beyond the ones you authenticate with.

**Q: How much disk space does it use?**
A: Typically 100MB-500MB depending on message volume. Much smaller than screenshots or PDFs.

**Q: Can I use this in a team?**
A: Yes, but each person needs to run their own instance with their own credentials. Consider sharing the setup as internal docs.

**Q: What if my Slack is on free plan?**
A: Free workspaces can only read the last 90 days of messages. Pro/Enterprise can read unlimited history.

**Q: How often does it collect?**
A: By default every 60 minutes (configurable). You can also manually trigger collection via the dashboard.

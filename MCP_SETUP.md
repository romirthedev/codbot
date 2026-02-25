# Claude Code MCP Integration

This guide explains how to integrate the Team Context Collector as an MCP server in Claude Code.

## What is MCP?

MCP (Model Context Protocol) is a protocol that lets Claude Code connect to custom tools and data sources. When integrated, Claude Code can automatically call `get_team_context` to retrieve relevant information while you're coding.

## Setup

### Step 1: Find Your Claude Code Config

Claude Code stores configuration in different locations depending on your setup:

**VSCode Extension:**
- Look for `.claude/config.json` in your workspace
- Or check VSCode settings under "Claude Code"

**CLI:**
- `~/.claude/config.json` (on macOS/Linux)
- `%APPDATA%/.claude/config.json` (on Windows)

### Step 2: Add MCP Server Configuration

Add this to your Claude Code config file (create the section if it doesn't exist):

```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/absolute/path/to/codbot"
    }
  }
}
```

**Replace `/absolute/path/to/codbot` with the actual path.** Use full paths, not `~`.

Example (macOS):
```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/Users/alice/codbot"
    }
  }
}
```

### Step 3: Verify Installation

Restart Claude Code, then run:

```
/help mcp
```

You should see `team-context` listed. If not, check:
- Python is in your PATH
- The cwd path is correct and absolute
- No typos in `config.json`

## How It Works

Once integrated:

1. **Claude Code sends code context** → When you ask Claude Code to help with code
2. **MCP server receives query** → The `get_team_context` tool is called
3. **Semantic search runs** → Finds relevant messages/docs from your team
4. **Results sent back** → Claude Code includes them in its reasoning

Example interaction:

```
You: "I'm implementing rate limiting for our API endpoints. What's our strategy?"

[Claude Code searches team context]

Claude finds:
- Slack: "Rate limiting discussion from 3 months ago"
- Notion: "API guidelines document"
- Slack: "Token bucket algorithm implementation notes"

Claude uses this context to implement rate limiting exactly as your team decided.
```

## The `get_team_context` Tool

When integrated, Claude Code has access to this tool:

```
Tool: get_team_context
Input:
  - query (required): Your code, a topic, or question
  - top_k (optional): Max results (default: 10)
  - threshold (optional): Min similarity 0-1 (default: 0.5)

Returns:
  Relevant messages and documents from Slack, Discord, Notion
```

## Troubleshooting

### MCP server not showing up

Check Claude Code logs (varies by setup) for errors like:
- `Command "python" not found` → Python isn't in PATH
- `No such file or directory` → Path is wrong or relative
- `ModuleNotFoundError: src` → Python can't find modules

**Solutions:**
- Use full path to python: `/usr/bin/python3` instead of `python`
- Use absolute path for `cwd` (start with `/` or `C:\`)
- Make sure you've run `pip install -r requirements.txt`

### Tool calls fail

If Claude Code calls the tool but gets errors:

1. Check the dashboard is running: `python server.py`
2. Verify context is indexed: Dashboard should show items
3. Test manually:
```python
from src.search import RelevanceSearch
from src.storage import ContextStorage

storage = ContextStorage()
search = RelevanceSearch(storage)
results = search.search("test query")
print(f"Found {len(results)} results")
```

### Context not being used

Claude Code automatically uses context when it's relevant. But:
- Make sure you have indexed context (run `python setup.py`)
- Try searching for something very specific
- Increase `top_k` in config to get more results
- Decrease `similarity_threshold` to be less strict

## Advanced Configuration

### Multiple MCP Servers

You can have multiple MCP servers at once:

```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/path/to/codbot"
    },
    "other-server": {
      "command": "node",
      "args": ["other-server.js"]
    }
  }
}
```

### Environment Variables

If you need to pass config dynamically:

```json
{
  "mcpServers": {
    "team-context": {
      "command": "python",
      "args": ["-m", "src.mcp_server_runner"],
      "cwd": "/path/to/codbot",
      "env": {
        "CONFIG_PATH": "/custom/path/config.yaml"
      }
    }
  }
}
```

Then in `src/mcp_server_runner.py`:
```python
import os
config_path = os.environ.get("CONFIG_PATH", "config.yaml")
```

### Custom Similarity Threshold

To be more/less strict about what context is included, you can set a different threshold. Lower = more results:

1. Edit `config.yaml`:
```yaml
search:
  top_k: 15
  similarity_threshold: 0.3  # More lenient
```

2. Restart the dashboard: `python server.py`

## How to Debug

If something isn't working:

### 1. Check MCP Server Starts
```bash
cd /path/to/codbot
python -m src.mcp_server_runner
# Should start without errors
```

Press Ctrl+C to stop.

### 2. Test Manually
```bash
# Start MCP in background
python -m src.mcp_server_runner &

# Test with Python
python3 -c "
import json
import sys

# Simulate Claude Code calling the tool
request = {
    'method': 'tools/call',
    'params': {
        'name': 'get_team_context',
        'arguments': {'query': 'authentication'}
    },
    'id': 1
}

print(json.dumps(request))
" | python -m src.mcp_server_runner
```

### 3. Check Dashboard
Visit http://localhost:8000 and:
- See total items indexed
- Test search manually
- Verify context is being collected

## Performance Notes

- **First call is slowest** (loads embeddings model)
- **Subsequent calls are instant** (cached embeddings)
- **No network latency** (everything runs locally)

If it feels slow:
- Pre-warm the model: Run `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`
- Reduce `top_k` if you don't need many results
- Check dashboard logs for errors

## Examples

### Example 1: Implementing a Feature

```
You: "We need to add two-factor authentication. What did the team decide?"

[MCP server finds 4 Slack threads about auth strategy and 2 Notion docs]

Claude includes this context:
- Team decided: SMS OTP via Twilio
- Architecture: Send OTP after password validation
- Security decision: Rate limit to 3 attempts per 5 minutes

Claude implements exactly what the team decided.
```

### Example 2: API Design

```
You: "What's our naming convention for REST endpoints?"

[MCP server finds API guidelines doc and design discussions]

Claude sees:
- "Use /api/v1/resource-name format"
- "Nested resources: /resource/{id}/sub-resource"
- "HTTP methods: GET for read, POST for create, etc"

Claude follows these conventions in new endpoint design.
```

### Example 3: Debugging

```
You: "I'm getting intermittent database timeouts. Has this happened before?"

[MCP server finds relevant Slack thread from 6 months ago]

Claude finds:
- Previous incident: "Connection pool was too small"
- Solution: "Increased pool size from 10 to 50"
- Lesson: "Monitor pool exhaustion in metrics"

Claude suggests the same fix based on team's past experience.
```

## Next Steps

1. **Complete QUICKSTART.md** if you haven't already
2. **Run `python setup.py`** to collect initial context
3. **Start dashboard**: `python server.py`
4. **Test MCP integration** by asking Claude Code about your codebase
5. **Adjust config** if you want different search behavior

## Support

For issues:
1. Check troubleshooting section above
2. Review main README.md
3. Test manually with the dashboard
4. Check Python and module imports work

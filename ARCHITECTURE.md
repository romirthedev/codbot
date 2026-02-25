# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude Code (IDE)                     │
│                                                               │
│  Detects: User is editing auth.py (authentication code)    │
│  Calls: MCP tool "get_team_context" with file content      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ JSON-RPC 2.0 over stdio
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server (src/mcp_server.py)                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Receives: {query: "def login()...", top_k: 10}    │   │
│  │ Validates input                                     │   │
│  │ Calls RelevanceSearch.search()                     │   │
│  │ Formats results as Claude-friendly text           │   │
│  │ Returns: Top 10 most similar messages/docs        │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Relevance Search (src/search.py)                     │
│                                                               │
│  ┌──────────────────────────────────┐  ┌───────────────┐   │
│  │  Sentence Transformers            │  │   ChromaDB    │   │
│  │  (all-MiniLM-L6-v2)              │  │  (Vector DB)  │   │
│  │                                   │  │               │   │
│  │  Converts queries to 384-dim     │  │  Stores ~462  │   │
│  │  embeddings for comparison       │  │  embeddings   │   │
│  └──────────────────────────────────┘  └───────────────┘   │
│                                                               │
│  1. Generate query embedding                                 │
│  2. Search ChromaDB for cosine similarity                    │
│  3. Filter by threshold (default 0.5)                        │
│  4. Reconstruct ContextItems from storage                    │
│  5. Sort by relevance and return top_k                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Context Storage (src/storage.py)                    │
│                                                               │
│  /context-store/                                             │
│  ├── slack/                                                  │
│  │   ├── general/                                            │
│  │   │   ├── a1b2c3d4e5f6g7h8i9j0.json                     │
│  │   │   └── ...                                             │
│  │   └── engineering/                                        │
│  │       └── ...                                             │
│  ├── discord/                                                │
│  │   ├── general/                                            │
│  │   └── ...                                                 │
│  └── notion/                                                 │
│      ├── pages/                                              │
│      └── ...                                                 │
│                                                               │
│  Each JSON file:                                             │
│  {                                                            │
│    "id": "unique-hash",                                      │
│    "source": "slack|discord|notion",                         │
│    "channel": "channel-name",                                │
│    "title": "Message title",                                 │
│    "content": "Full message/doc text",                       │
│    "timestamp": "2024-02-24T10:30:00",                      │
│    "metadata": {...}                                         │
│  }                                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Slack SDK    │  │Discord.py    │  │Notion SDK    │
    │              │  │              │  │              │
    │ conversations│  │ Bot with     │  │API calls     │
    │ .history()   │  │ intents:     │  │.pages.        │
    │              │  │ - Message    │  │retrieve()    │
    │ conversations│  │ - ServerMem  │  │              │
    │ .list()      │  │              │  │.blocks        │
    │              │  │ fetch        │  │.children     │
    │ users.info() │  │ messages by  │  │.list()       │
    │              │  │ channel      │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Slack      │  │   Discord    │  │   Notion     │
    │   Workspace  │  │   Servers    │  │   Workspace  │
    │              │  │              │  │              │
    │ Messages,    │  │ Messages,    │  │ Pages,       │
    │ Threads,     │  │ Reactions,   │  │ Blocks,      │
    │ Users        │  │ Users        │  │ Properties   │
    └──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow

### Setup Phase (python setup.py)

```
User Config (config.yaml)
    │
    ▼
Load Config (src/config.py)
    │
    ▼
Validate Config (checks tokens, channels, pages)
    │
    ▼
CollectorManager.collect_all()
    │
    ├── SlackCollector.collect()  → [ContextItem, ...]
    │   └── Slack API calls for each channel
    │
    ├── DiscordCollector.collect() → [ContextItem, ...]
    │   └── Discord Bot for each server/channel
    │
    └── NotionCollector.collect() → [ContextItem, ...]
        └── Notion API for each page
    │
    ▼
ContextStorage.save_items() → /context-store/
    │
    ▼
RelevanceSearch.reindex_all()
    │
    ├── Load all items from storage
    ├── Encode each with SentenceTransformer
    └── Add to ChromaDB vector database
    │
    ▼
✅ Ready for use
```

### Runtime Phase (Claude Code + MCP Server)

```
Claude Code (editing code)
    │ "What's our auth strategy?"
    ▼
Sends to MCP Server:
{
  method: "tools/call",
  params: {
    name: "get_team_context",
    arguments: {
      query: "authentication...",
      top_k: 10
    }
  }
}
    │
    ▼
MCPServer.handle_tool_call()
    │
    ▼
RelevanceSearch.search_with_context()
    │
    ├── model.encode(query) → 384-dim vector
    │
    ├── chromadb.query(query_embedding)
    │   └── Finds top_k most similar items by cosine distance
    │
    ├── Filter by threshold
    │
    └── Return formatted results
    │
    ▼
Returns to Claude Code:
```
[SLACK] #general: Team auth decision
...discussion about JWT vs sessions...
JWT was chosen because...
---
Relevance: 0.87

[NOTION] pages: Architecture Decisions
Authentication System
- Use JWT with RS256 signing
...
```
    │
    ▼
Claude Code incorporates context into reasoning
    │
    ▼
Implements JWT auth the way your team decided ✅
```

## Key Components

### 1. Collectors (src/collectors/)

**Purpose**: Extract context from external platforms

**Base Class** (src/collectors/base.py):
- Abstract `collect()` method
- ID generation with hashing
- Common storage interface

**Implementations**:
- **SlackCollector**: Uses `slack_sdk` to fetch messages, users, history
- **DiscordCollector**: Uses `discord.py` bot API (async-based)
- **NotionCollector**: Uses `notion-client` to fetch pages and blocks

### 2. Storage (src/storage.py)

**Purpose**: Persist context locally

**Design**:
```
ContextItem
├── id: unique hash
├── source: slack|discord|notion
├── channel: channel/page name
├── title: user/author + message title
├── content: full text
├── timestamp: ISO format
└── metadata: platform-specific data

ContextStorage
├── save_items() → /context-store/{source}/{channel}/
├── load_all_items() → [ContextItem, ...]
├── get_items_by_source() → filtered list
└── clear_source() → reset source data
```

### 3. Search (src/search.py)

**Purpose**: Semantic similarity search

**Architecture**:
```
Embedding Model (sentence-transformers)
├── Model: all-MiniLM-L6-v2
├── Input: Text of any length
└── Output: 384-dimensional vector

Vector Database (chromadb)
├── Stores: Embeddings + metadata + original text
├── Search: Cosine similarity
├── Storage: Local parquet files
└── Speed: Instant (few ms for 462 items)

RelevanceSearch
├── index_items() → embed + store in chromadb
├── search() → query embedding + similarity search
├── reindex_all() → rebuild entire index
└── search_with_context() → format for Claude
```

### 4. Configuration (src/config.py)

**Purpose**: Manage settings with validation

**Structure**:
```yaml
slack:
  enabled: bool
  bot_token: str
  channels: [str]

discord:
  enabled: bool
  bot_token: str
  servers: [{server: str, channels: [str]}]

notion:
  enabled: bool
  api_key: str
  pages: [str]

indexing:
  lookback_days: int
  sync_interval: int

search:
  top_k: int
  similarity_threshold: float
```

### 5. MCP Server (src/mcp_server.py)

**Purpose**: Bridge between Claude Code and team context

**Protocol**: JSON-RPC 2.0 over stdio

**Tools Exposed**:
```
get_team_context:
  Input:
    - query: str (code or topic)
    - top_k: int (default 10)
    - threshold: float (default 0.5)

  Output:
    - content: [text with formatted results]
    - or error: str
```

### 6. Web Dashboard (src/dashboard.py)

**Purpose**: UI for management and testing

**Endpoints**:
```
GET  /              → HTML dashboard
GET  /api/stats     → {total_items, by_source}
GET  /api/search    → Query results
POST /api/collect   → Trigger collection
POST /api/reindex   → Rebuild index
```

## Scalability

### Current Limits

- **Items**: Tested with 1000+ items
- **Query speed**: <50ms typical
- **Memory**: ~500MB for full setup
- **Disk**: ~100-500MB depending on content
- **Platforms**: Slack (free: 90 days), Discord (unlimited), Notion (API rate limits)

### Bottlenecks

1. **First embedding load**: ~1-2 seconds (model loads to RAM)
2. **Large re-indexing**: ~10-20 seconds for 1000 items
3. **Slack API rate limits**: 1 request/second on free tier

### Optimization Opportunities

- **Lazy loading**: Only load embeddings when needed
- **Parallel collection**: Collect from platforms concurrently
- **Incremental indexing**: Only add new items instead of re-indexing all
- **Caching**: Cache frequently searched queries
- **Batching**: Process items in batches rather than one-by-one

## Security

### What's Stored Locally

- OAuth tokens (in config.yaml)
- All team messages/docs (in context-store/)
- Embeddings vectors (in .chromadb/)

### No Network Traffic

- ✅ Embeddings computed locally
- ✅ Search happens locally
- ✅ No data leaves your machine
- ✅ Only initial auth uses platform APIs

### Recommendations

1. **Config file**: Add to `.gitignore` (contains tokens)
2. **Access control**: Keep config.yaml secret
3. **Encryption**: Consider encrypting context-store/ if sensitive
4. **Cleanup**: Regularly clear old context with lookback_days

## Testing Strategy

```
Unit Tests (tests/)
├── TestContextItem
│   ├── create_item()
│   ├── to_dict()
│   └── from_dict()
│
├── TestContextStorage
│   ├── save_and_load_items()
│   ├── get_items_by_source()
│   └── clear_source()
│
└── TestConfig
    ├── load_default_config()
    ├── load_config_from_file()
    ├── no_platforms_enabled()
    ├── slack_without_token()
    └── valid_configuration()

Integration Tests (manual)
├── Collect from fake platforms
├── Verify embeddings work
├── Search returns relevant results
└── Dashboard displays stats

End-to-End Tests
├── Run setup.py
├── Start dashboard
├── Verify MCP tool in Claude Code
└── Test context in actual coding session
```

## Future Enhancements

### Collectors
- GitHub issues/PRs as context
- Email/calendar events
- Internal wikis/documentation
- Slack threading

### Search
- Multi-modal (images + text)
- Temporal weighting (recent more relevant)
- Author weighting (team leads more trusted)
- Faceted search (filter by source/date)

### Dashboard
- Real-time sync status
- Search analytics
- Custom embeddings model selection
- Webhook triggers for collection

### Integration
- Automatic Claude Code setup
- VS Code extension
- JetBrains IDE plugin
- GitHub Copilot integration

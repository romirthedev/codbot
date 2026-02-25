"""MCP (Model Context Protocol) server for Claude Code integration."""

import json
from pathlib import Path
from typing import Any, Optional

from src.config import load_config
from src.search import RelevanceSearch
from src.storage import ContextStorage


class MCPServer:
    """MCP server that exposes team context to Claude Code."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        self.storage = ContextStorage()
        self.search = RelevanceSearch(self.storage)

    def get_tools(self) -> list[dict]:
        """Return the list of tools this MCP server exposes."""
        return [
            {
                "name": "get_team_context",
                "description": "Search for relevant team context (Slack messages, Discord chats, Notion docs) based on the current code or topic.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The code snippet, file content, or topic to search for relevant context about.",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)",
                            "default": 10,
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Minimum similarity score (0-1, default: 0.5)",
                            "default": 0.5,
                        },
                    },
                    "required": ["query"],
                },
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        """Handle a tool call from Claude Code.

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool

        Returns:
            Result dictionary with content and metadata
        """
        if tool_name == "get_team_context":
            return self._handle_get_team_context(arguments)
        else:
            return {
                "error": f"Unknown tool: {tool_name}",
                "content": [],
            }

    def _handle_get_team_context(self, arguments: dict) -> dict[str, Any]:
        """Handle the get_team_context tool call."""
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 10)
        threshold = arguments.get("threshold", 0.5)

        if not query:
            return {
                "error": "Query parameter is required",
                "content": [],
            }

        try:
            results = self.search.search_with_context(query, top_k=top_k, threshold=threshold)

            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No relevant team context found for your query.",
                        }
                    ]
                }

            # Format results for Claude
            formatted_results = "\n\n".join(results)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Found {len(results)} relevant context items:\n\n{formatted_results}",
                    }
                ]
            }

        except Exception as e:
            return {
                "error": str(e),
                "content": [
                    {
                        "type": "text",
                        "text": f"Error searching for context: {e}",
                    }
                ],
            }

    def export_mcp_config(self, server_name: str = "team-context") -> dict:
        """Export MCP server configuration for Claude Code.

        This is what goes in the user's Claude Code configuration file.
        """
        return {
            "mcpServers": {
                server_name: {
                    "command": "python",
                    "args": ["-m", "src.mcp_server_runner"],
                    "cwd": str(Path.cwd()),
                }
            }
        }


def start_stdio_server() -> None:
    """Start the MCP server in stdio mode (for integration with Claude Code).

    This implements the JSON-RPC 2.0 protocol that MCP uses.
    """
    import sys

    server = MCPServer()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {
                            "name": "team-context",
                            "version": "0.1.0",
                        },
                    },
                }

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": server.get_tools(),
                    },
                }

            elif method == "tools/call":
                tool_result = server.handle_tool_call(
                    params.get("name"),
                    params.get("arguments", {}),
                )
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": tool_result,
                }

            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}",
                    },
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

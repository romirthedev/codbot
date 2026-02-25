"""Simple web dashboard for managing team context."""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

from src.config import load_config
from src.storage import ContextStorage
from src.search import RelevanceSearch
from src.collector_manager import CollectorManager


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    storage = None
    search = None
    config = None

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self.serve_html()
        elif self.path == "/api/stats":
            self.api_stats()
        elif self.path == "/api/search":
            self.api_search()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/reindex":
            self.api_reindex()
        elif self.path == "/api/collect":
            self.api_collect()
        else:
            self.send_error(404)

    def serve_html(self):
        """Serve the dashboard HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Context Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .results {
            background: #f9f9f9;
            border-radius: 6px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        .result-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        .result-source {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .result-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .result-content {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 100px;
            overflow: hidden;
        }
        .status {
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Team Context Dashboard</h1>
        <p class="subtitle">Manage your Slack, Discord, and Notion context</p>

        <div class="section">
            <div class="section-title">Statistics</div>
            <div id="stats" class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">Total Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">From Slack</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">From Discord</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">-</div>
                    <div class="stat-label">From Notion</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Management</div>
            <div class="button-group">
                <button onclick="collectData()">Collect from Platforms</button>
                <button onclick="reindexData()">Rebuild Index</button>
                <button onclick="loadStats()">Refresh Stats</button>
            </div>
            <div id="status"></div>
        </div>

        <div class="section">
            <div class="section-title">Search Test</div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Enter a search query...">
                <button onclick="performSearch()">Search</button>
            </div>
            <div id="results" class="results" style="display:none;"></div>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();

                const stats = document.querySelector('#stats');
                const bySource = data.by_source || {};
                stats.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${data.total_items}</div>
                        <div class="stat-label">Total Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${bySource.slack || 0}</div>
                        <div class="stat-label">From Slack</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${bySource.discord || 0}</div>
                        <div class="stat-label">From Discord</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${bySource.notion || 0}</div>
                        <div class="stat-label">From Notion</div>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function collectData() {
            showStatus('Collecting data from platforms...', 'info');
            try {
                const response = await fetch('/api/collect', { method: 'POST' });
                const data = await response.json();
                showStatus('Data collection complete!', 'success');
                loadStats();
            } catch (error) {
                showStatus('Error collecting data: ' + error, 'error');
            }
        }

        async function reindexData() {
            showStatus('Rebuilding search index...', 'info');
            try {
                const response = await fetch('/api/reindex', { method: 'POST' });
                const data = await response.json();
                showStatus('Index rebuild complete!', 'success');
            } catch (error) {
                showStatus('Error rebuilding index: ' + error, 'error');
            }
        }

        async function performSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                const resultsDiv = document.getElementById('results');
                if (data.results && data.results.length > 0) {
                    resultsDiv.innerHTML = data.results.map(r => `
                        <div class="result-item">
                            <div class="result-source">${r.source}</div>
                            <div class="result-title">${r.channel}: ${r.title}</div>
                            <div class="result-content">${r.content.substring(0, 200)}...</div>
                        </div>
                    `).join('');
                } else {
                    resultsDiv.innerHTML = '<p style="color: #999;">No results found.</p>';
                }
                resultsDiv.style.display = 'block';
            } catch (error) {
                console.error('Search error:', error);
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => { statusDiv.innerHTML = ''; }, 5000);
        }

        // Load stats on page load
        loadStats();
    </script>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def api_stats(self):
        """API endpoint for statistics."""
        items = self.storage.load_all_items()
        by_source = {}

        for item in items:
            if item.source not in by_source:
                by_source[item.source] = 0
            by_source[item.source] += 1

        response = {
            "total_items": len(items),
            "by_source": by_source,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def api_search(self):
        """API endpoint for searching."""
        query_params = parse_qs(self.path.split("?")[1] if "?" in self.path else "")
        query = query_params.get("q", [""])[0]

        if not query:
            self.send_error(400, "Query parameter 'q' is required")
            return

        try:
            results = self.search.search(query, top_k=5)
            formatted = [
                {
                    "source": r[0].source,
                    "channel": r[0].channel,
                    "title": r[0].title,
                    "content": r[0].content,
                    "similarity": r[1],
                }
                for r in results
            ]

            response = {"results": formatted}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def api_collect(self):
        """API endpoint to trigger collection."""
        try:
            manager = CollectorManager(self.config)
            results = manager.collect_all()
            manager.reindex()

            response = {"status": "success", "results": results}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def api_reindex(self):
        """API endpoint to rebuild the search index."""
        try:
            self.search.reindex_all()
            response = {"status": "success", "message": "Index rebuilt"}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default HTTP logging."""
        pass


def start_dashboard(port: int = 8000):
    """Start the web dashboard server."""
    DashboardHandler.storage = ContextStorage()
    DashboardHandler.search = RelevanceSearch(DashboardHandler.storage)
    DashboardHandler.config = load_config()

    server = HTTPServer(("localhost", port), DashboardHandler)
    print(f"Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped")
        server.server_close()

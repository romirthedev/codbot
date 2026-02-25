#!/usr/bin/env python3
"""
Demo mode for Team Context Collector dashboard.
Run locally without needing tokens or platform connections.

Usage: python demo.py
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import random


class DemoHandler(BaseHTTPRequestHandler):
    """Demo dashboard handler."""

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

    def serve_html(self):
        """Serve the demo dashboard HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Context Collector - Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f1e8 0%, #e8dcc8 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #faf8f4;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
            color: #f5f1e8;
            padding: 50px 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .header p {
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 30px;
        }

        .demo-badge {
            display: inline-block;
            background: #d4af37;
            color: #1a1a1a;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 50px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: #2c2c2c;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid #2c2c2c;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #fff;
            border: 2px solid #2c2c2c;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .stat-value {
            font-size: 48px;
            font-weight: 700;
            color: #2c2c2c;
            margin-bottom: 8px;
        }

        .stat-label {
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }

        .button-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        button {
            background: #2c2c2c;
            color: #f5f1e8;
            border: none;
            padding: 12px 28px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        button:hover {
            background: #1a1a1a;
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .search-box {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }

        input[type="text"] {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #2c2c2c;
            border-radius: 8px;
            font-size: 14px;
            background: #fff;
            transition: all 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #2c2c2c;
            box-shadow: 0 0 0 3px rgba(44,44,44,0.1);
        }

        .results {
            background: #fff;
            border: 2px solid #2c2c2c;
            border-radius: 12px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            display: none;
        }

        .results.active {
            display: block;
        }

        .result-item {
            background: #f5f1e8;
            padding: 18px;
            margin-bottom: 15px;
            border-left: 4px solid #2c2c2c;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .result-item:hover {
            background: #ede9df;
        }

        .result-item:last-child {
            margin-bottom: 0;
        }

        .result-source {
            display: inline-block;
            background: #2c2c2c;
            color: #f5f1e8;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .result-title {
            font-weight: 700;
            color: #2c2c2c;
            margin-bottom: 8px;
            font-size: 15px;
        }

        .result-content {
            color: #555;
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 8px;
        }

        .result-meta {
            font-size: 12px;
            color: #999;
        }

        .status {
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid;
        }

        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
            border-left-color: #2e7d32;
        }

        .status.info {
            background: #e3f2fd;
            color: #1565c0;
            border-left-color: #1565c0;
        }

        .status.demo {
            background: #fff3e0;
            color: #e65100;
            border-left-color: #e65100;
        }

        .demo-notice {
            background: #fff3e0;
            border: 2px solid #2c2c2c;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            color: #666;
        }

        .demo-notice strong {
            color: #2c2c2c;
        }

        .footer {
            background: #f0ede4;
            padding: 30px 40px;
            text-align: center;
            color: #666;
            font-size: 13px;
            border-top: 2px solid #2c2c2c;
        }

        .footer a {
            color: #2c2c2c;
            text-decoration: none;
            font-weight: 600;
        }

        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Team Context Collector</h1>
            <p>Demo Dashboard Preview</p>
            <span class="demo-badge">Demo Mode</span>
        </div>

        <div class="content">
            <div class="demo-notice">
                <strong>📌 This is a demo!</strong> You're seeing sample data to preview how the dashboard looks.
                To use with real Slack/Discord/Notion data, run: <code>python install.py</code>
            </div>

            <div class="section">
                <div class="section-title">📊 Statistics</div>
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
                <div class="section-title">🔍 Search Test</div>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Try searching for: authentication, database, api, design...">
                    <button onclick="performSearch()">Search</button>
                </div>
                <div id="status"></div>
                <div id="results" class="results"></div>
            </div>
        </div>

        <div class="footer">
            Ready to try with real data? Download <a href="https://raw.githubusercontent.com/romirthedev/codbot/main/install.py">install.py</a>
            and run <code>python install.py</code>
        </div>
    </div>

    <script>
        const sampleResults = {
            "authentication": [
                {
                    source: "SLACK",
                    channel: "#engineering",
                    title: "JWT Implementation Decision",
                    content: "Team decided to use RS256 with JWT tokens. 1-hour expiry time, refresh tokens stored securely. Rate limit login attempts to 3 per 5 minutes.",
                    similarity: 0.94
                },
                {
                    source: "NOTION",
                    channel: "Security Guidelines",
                    title: "Authentication Best Practices",
                    content: "All authentication flows must use HTTPS. Never store passwords in plaintext. Always hash with bcrypt (rounds: 12). Implement multi-factor authentication for admin accounts.",
                    similarity: 0.91
                },
                {
                    source: "SLACK",
                    channel: "#security",
                    title: "OAuth Implementation Notes",
                    content: "We use OAuth 2.0 with PKCE flow for mobile apps. State parameter required for all flows. Redirect URIs must be whitelisted.",
                    similarity: 0.87
                }
            ],
            "database": [
                {
                    source: "NOTION",
                    channel: "Architecture",
                    title: "Database Schema Design",
                    content: "PostgreSQL primary database. Read replicas for analytics queries. Redis cache layer for sessions and frequently accessed data.",
                    similarity: 0.92
                },
                {
                    source: "SLACK",
                    channel: "#backend",
                    title: "Connection Pool Timeout Issue",
                    content: "Increased connection pool from 10 to 50 connections. Was causing timeouts under load. Now monitoring with DataDog alerts.",
                    similarity: 0.89
                }
            ],
            "api": [
                {
                    source: "NOTION",
                    channel: "API Documentation",
                    title: "REST API Standards",
                    content: "Use REST conventions. Version endpoints with /api/v1/. All endpoints require authentication. Rate limit: 100 req/min per user.",
                    similarity: 0.93
                },
                {
                    source: "SLACK",
                    channel: "#engineering",
                    title: "GraphQL Migration Discussion",
                    content: "Considering GraphQL for new features. Current REST API working well. Would need 2-3 weeks to set up schema and migration plan.",
                    similarity: 0.85
                }
            ],
            "design": [
                {
                    source: "NOTION",
                    channel: "Design System",
                    title: "Color Palette & Typography",
                    content: "Primary: #2c2c2c, Secondary: #d4af37, Neutral: #f5f1e8. Font: Inter (UI), Georgia (body). Dark mode available.",
                    similarity: 0.88
                },
                {
                    source: "SLACK",
                    channel: "#design",
                    title: "Component Library Update",
                    content: "New button variants added. Accessibility audit complete (WCAG AA compliant). Documentation updated on Figma.",
                    similarity: 0.84
                }
            ],
            "default": [
                {
                    source: "SLACK",
                    channel: "#general",
                    title: "Team Context Tool Launch",
                    content: "We've launched a new tool that brings all our team decisions and documentation into Claude Code. This helps ensure consistency across the codebase.",
                    similarity: 0.76
                },
                {
                    source: "NOTION",
                    channel: "Engineering",
                    title: "Development Guidelines",
                    content: "Follow the coding standards in the wiki. PR reviews required. All code must be tested before merging to main.",
                    similarity: 0.72
                }
            ]
        };

        function loadStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    const stats = document.querySelector('#stats');
                    stats.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${data.total_items}</div>
                            <div class="stat-label">Total Items</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.by_source.slack || 0}</div>
                            <div class="stat-label">From Slack</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.by_source.discord || 0}</div>
                            <div class="stat-label">From Discord</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.by_source.notion || 0}</div>
                            <div class="stat-label">From Notion</div>
                        </div>
                    `;
                });
        }

        function performSearch() {
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            if (!query) return;

            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="status demo">🎯 Showing demo results for: <strong>' + query + '</strong></div>';

            const results = sampleResults[query] || sampleResults['default'];
            const resultsDiv = document.getElementById('results');

            resultsDiv.innerHTML = results.map(r => `
                <div class="result-item">
                    <div class="result-source">${r.source}</div>
                    <div class="result-title">${r.channel} • ${r.title}</div>
                    <div class="result-content">${r.content}</div>
                    <div class="result-meta">Relevance: ${(r.similarity * 100).toFixed(0)}%</div>
                </div>
            `).join('');

            resultsDiv.classList.add('active');
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });

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
        """Return demo statistics."""
        response = {
            "total_items": 487,
            "by_source": {
                "slack": 312,
                "discord": 89,
                "notion": 86
            }
        }
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def api_search(self):
        """API endpoint for searching."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:
        """Suppress HTTP logging."""
        pass


def main():
    """Start the demo dashboard."""
    print("\n" + "=" * 70)
    print("  Team Context Collector - Demo Dashboard")
    print("=" * 70)
    print("\n📺 Opening dashboard at: http://localhost:8000\n")
    print("Features:")
    print("  • Try searching: 'authentication', 'database', 'api', 'design'")
    print("  • See sample results from Slack, Discord, and Notion")
    print("  • Preview the UI design (creamy background, black accents)\n")
    print("Ready for real data?")
    print("  Download: https://raw.githubusercontent.com/romirthedev/codbot/main/install.py")
    print("  Run: python install.py\n")
    print("Press Ctrl+C to stop\n")

    try:
        server = HTTPServer(("localhost", 8000), DemoHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nDemo stopped. 👋")


if __name__ == "__main__":
    main()

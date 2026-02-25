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
            font-family: 'Comic Sans MS', 'Courier New', monospace;
            background: #F5E6D3;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #F9EFE3;
            border: 8px solid #1a1a1a;
            box-shadow: 12px 12px 0px #1a1a1a;
            overflow: hidden;
        }

        .header {
            background: #E8D4C0;
            color: #1a1a1a;
            padding: 40px 30px;
            text-align: center;
            border-bottom: 8px solid #1a1a1a;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image:
                repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px);
            pointer-events: none;
        }

        .header h1 {
            font-size: 48px;
            margin-bottom: 10px;
            font-weight: 900;
            text-shadow: 3px 3px 0px #1a1a1a;
            position: relative;
            z-index: 1;
            color: #1a1a1a;
        }

        .header p {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 0px rgba(0,0,0,0.2);
            color: #1a1a1a;
        }

        .demo-badge {
            display: inline-block;
            background: #D4A574;
            color: #1a1a1a;
            padding: 10px 20px;
            border: 4px solid #1a1a1a;
            font-weight: 900;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
            transform: rotate(-3deg);
            box-shadow: 4px 4px 0px #1a1a1a;
            position: relative;
            z-index: 1;
        }

        .content {
            padding: 30px;
            background: #F9EFE3;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 24px;
            font-weight: 900;
            color: #fff;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: #1a1a1a;
            border: 4px solid #1a1a1a;
            transform: rotate(-2deg);
            box-shadow: 6px 6px 0px #1a1a1a;
            display: inline-block;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #fff;
            border: 6px solid #1a1a1a;
            padding: 25px;
            text-align: center;
            box-shadow: 8px 8px 0px #1a1a1a;
            transform: rotate(1deg);
            transition: all 0.1s;
            cursor: pointer;
        }

        .stat-card:hover {
            transform: rotate(-1deg) scale(1.05);
            box-shadow: 10px 10px 0px #1a1a1a;
        }

        .stat-card:nth-child(2) {
            transform: rotate(-1deg);
        }

        .stat-card:nth-child(3) {
            transform: rotate(2deg);
        }

        .stat-card:nth-child(4) {
            transform: rotate(-2deg);
        }

        .stat-value {
            font-size: 54px;
            font-weight: 900;
            color: #D4A574;
            margin-bottom: 10px;
            text-shadow: 2px 2px 0px #1a1a1a;
        }

        .stat-label {
            color: #1a1a1a;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        button {
            background: #1a1a1a;
            color: #F9EFE3;
            border: 4px solid #1a1a1a;
            padding: 14px 28px;
            font-size: 14px;
            font-weight: 900;
            font-family: 'Comic Sans MS', monospace;
            cursor: pointer;
            box-shadow: 6px 6px 0px #1a1a1a;
            transform: rotate(-1deg);
            transition: all 0.1s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        button:hover {
            transform: rotate(-1deg) translateY(-3px);
            box-shadow: 8px 8px 0px #1a1a1a;
            background: #0d0d0d;
        }

        button:active {
            box-shadow: 2px 2px 0px #1a1a1a;
            transform: rotate(-1deg) translateY(2px);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .search-box {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }

        input[type="text"] {
            flex: 1;
            padding: 14px 18px;
            border: 4px solid #1a1a1a;
            font-size: 14px;
            background: #fff;
            font-family: 'Comic Sans MS', monospace;
            font-weight: 600;
            box-shadow: 4px 4px 0px #1a1a1a;
        }

        input[type="text"]:focus {
            outline: none;
            box-shadow: 6px 6px 0px #1a1a1a;
            background: #F9EFE3;
        }

        .results {
            background: #fff;
            border: 6px solid #1a1a1a;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            display: none;
            box-shadow: 8px 8px 0px #1a1a1a;
        }

        .results.active {
            display: block;
        }

        .result-item {
            background: #F5E6D3;
            padding: 18px;
            margin-bottom: 15px;
            border: 4px solid #1a1a1a;
            box-shadow: 4px 4px 0px #1a1a1a;
            transform: rotate(-1deg);
            transition: all 0.1s;
        }

        .result-item:hover {
            transform: rotate(1deg) scale(1.02);
            box-shadow: 6px 6px 0px #1a1a1a;
        }

        .result-item:nth-child(even) {
            background: #E8D4C0;
            transform: rotate(1deg);
        }

        .result-item:nth-child(even):hover {
            transform: rotate(-1deg) scale(1.02);
        }

        .result-item:last-child {
            margin-bottom: 0;
        }

        .result-source {
            display: inline-block;
            background: #D4A574;
            color: #1a1a1a;
            padding: 6px 14px;
            border: 3px solid #1a1a1a;
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            box-shadow: 3px 3px 0px #1a1a1a;
            transform: rotate(-2deg);
        }

        .result-title {
            font-weight: 900;
            color: #1a1a1a;
            margin-bottom: 8px;
            font-size: 15px;
            text-transform: uppercase;
        }

        .result-content {
            color: #333;
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .result-meta {
            font-size: 12px;
            color: #666;
            font-weight: 700;
        }

        .status {
            padding: 16px 20px;
            margin-bottom: 15px;
            border: 4px solid #1a1a1a;
            box-shadow: 6px 6px 0px #1a1a1a;
            font-weight: 700;
        }

        .status.demo {
            background: #F5E6D3;
            color: #1a1a1a;
        }

        .demo-notice {
            background: #E8D4C0;
            border: 6px solid #1a1a1a;
            padding: 25px;
            margin-bottom: 30px;
            color: #1a1a1a;
            box-shadow: 8px 8px 0px #1a1a1a;
            font-weight: 700;
            transform: rotate(-2deg);
        }

        .demo-notice strong {
            color: #1a1a1a;
            text-transform: uppercase;
        }

        .demo-notice code {
            background: #fff;
            padding: 4px 8px;
            border: 2px solid #1a1a1a;
            font-weight: 900;
        }

        .footer {
            background: #E8D4C0;
            padding: 30px 40px;
            text-align: center;
            color: #1a1a1a;
            font-size: 13px;
            font-weight: 700;
            border-top: 8px solid #1a1a1a;
        }

        .footer a {
            color: #1a1a1a;
            text-decoration: none;
            font-weight: 900;
            text-transform: uppercase;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        code {
            background: #F5E6D3;
            padding: 2px 6px;
            border: 2px solid #1a1a1a;
            font-weight: 900;
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

#!/usr/bin/env python3
"""
Start the web dashboard server.

Visit http://localhost:8000 to access the dashboard.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dashboard import start_dashboard


def main():
    """Start the dashboard server."""
    print("\n" + "="*60)
    print("  Team Context Dashboard")
    print("="*60 + "\n")

    port = 8000
    print(f"Starting dashboard on http://localhost:{port}...\n")

    try:
        start_dashboard(port=port)
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")


if __name__ == "__main__":
    main()

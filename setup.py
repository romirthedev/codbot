#!/usr/bin/env python3
"""
Setup script for Team Context Collector.

Run this to authenticate with your platforms and perform the initial index.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.collector_manager import run_collection_setup
from src.config import load_config, validate_config


def main():
    """Run the setup process."""
    print("\n" + "="*60)
    print("  Team Context Collector - Initial Setup")
    print("="*60 + "\n")

    config_path = "config.yaml"

    print("Step 1: Loading configuration...")
    config = load_config(config_path)
    print(f"  ✓ Configuration loaded from {config_path}\n")

    print("Step 2: Validating configuration...")
    warnings = validate_config(config)
    if warnings:
        print("  ⚠ Configuration warnings:")
        for warning in warnings:
            print(f"    - {warning}")
        print()
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != "y":
            print("Setup cancelled.")
            return
    else:
        print("  ✓ Configuration is valid\n")

    print("Step 3: Running collection setup...")
    try:
        run_collection_setup(config_path)
    except Exception as e:
        print(f"  ✗ Error during setup: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("  Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start the dashboard: python server.py")
    print("  2. View at: http://localhost:8000")
    print("  3. Add to Claude Code config (see README for instructions)")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
One-click installer for Team Context Collector.
Download this file and run: python install.py

This script will:
1. Clone the repo
2. Install dependencies
3. Guide you through getting tokens
4. Start the dashboard
"""

import os
import sys
import subprocess
import platform


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description=""):
    """Run a command and show progress."""
    if description:
        print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"✗ Error running: {cmd}")
            return False
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_python():
    """Check if Python 3.10+ is installed."""
    if sys.version_info < (3, 10):
        print("✗ Python 3.10+ required")
        print(f"  You have: Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def check_git():
    """Check if git is installed."""
    result = subprocess.run("git --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("✗ Git not found. Please install from: https://git-scm.com/")
        sys.exit(1)
    print("✓ Git installed")


def clone_repo():
    """Clone the repository."""
    if os.path.exists("codbot"):
        print("✓ Folder 'codbot' already exists, skipping clone")
        return True

    print("⏳ Downloading codbot (this takes ~10 seconds)...")
    return run_command(
        "git clone https://github.com/romirthedev/codbot.git",
        "Cloning repository"
    )


def install_dependencies():
    """Install Python dependencies."""
    os.chdir("codbot")
    return run_command(
        "pip install -r requirements.txt",
        "Installing dependencies (takes ~30 seconds)"
    )


def show_token_instructions():
    """Show instructions for getting tokens."""
    print_header("Get Your Tokens (Choose Which Ones You Need)")

    print("Pick which platforms you want to use. You don't need all of them!\n")

    slack_instructions = """
SLACK:
1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Team Context" → Pick workspace → Create
4. Left sidebar → Click "OAuth & Permissions"
5. Add these scopes:
   ☐ channels:history
   ☐ users:read
   ☐ groups:history
6. Click "Reinstall to Workspace" at top
7. Copy "Bot User OAuth Token" (starts with xoxb-)
8. Save this token, you'll need it next

Discord:
1. Go to: https://discord.com/developers/applications
2. Click "New Application" → Give it a name → Create
3. Click "Bot" on left → "Add Bot"
4. Under TOKEN, click "Copy" (starts with Mzk...)
5. Save this token, you'll need it next
6. Scroll to "Privileged Gateway Intents"
7. Turn ON: Message Content Intent, Server Members Intent

Notion:
1. Go to: https://www.notion.so/my-integrations
2. Click "New Integration" → Name: "Team Context" → Create
3. Click "Show" on "Internal Integration Token" → Copy
4. Save this token, you'll need it next
5. Go to your Notion pages → Share → Add your integration
"""
    print(slack_instructions)

    response = input("Press Enter when you have your tokens ready... ")


def edit_config():
    """Guide user to edit config."""
    print_header("Edit Your Config")

    print("Open this file in any text editor:")
    print("  codbot/config.yaml\n")

    print("Add your tokens. Example:\n")
    print("""slack:
  enabled: true
  bot_token: "PASTE_YOUR_TOKEN_HERE"
  channels: ["#general", "#engineering"]

discord:
  enabled: false

notion:
  enabled: false
""")

    print("\nChange 'enabled: false' to 'enabled: true' for platforms you use.")
    print("Save the file when done.\n")

    input("Press Enter when you've edited config.yaml... ")


def run_setup():
    """Run the setup script."""
    return run_command(
        "python setup.py",
        "Setting up (collecting and indexing context)"
    )


def start_dashboard():
    """Start the dashboard."""
    print_header("Done! Starting Dashboard")

    print("Opening http://localhost:8000 in your browser...\n")
    print("The dashboard will show:")
    print("  • How many messages were indexed")
    print("  • A search box to test")
    print("  • Buttons to re-collect or rebuild index\n")

    # Open browser
    webbrowser_cmd = {
        "Darwin": "open",
        "Linux": "xdg-open",
        "Windows": "start"
    }.get(platform.system(), "open")

    subprocess.run(f"{webbrowser_cmd} http://localhost:8000", shell=True)

    # Start server
    print("Starting server (Press Ctrl+C to stop)...\n")
    run_command(
        "python server.py",
        "Starting dashboard"
    )


def main():
    """Main installation flow."""
    print_header("Team Context Collector - One-Click Installer")

    print("This will:\n")
    print("  1. Download the codbot project")
    print("  2. Install all dependencies")
    print("  3. Guide you through getting tokens")
    print("  4. Set everything up")
    print("  5. Start the dashboard\n")

    # Checks
    print("Checking requirements...\n")
    check_python()
    check_git()

    # Download
    print_header("Step 1: Download")
    if not clone_repo():
        sys.exit(1)

    # Install
    print_header("Step 2: Install Dependencies")
    if not install_dependencies():
        sys.exit(1)

    # Tokens
    print_header("Step 3: Get Your Tokens")
    show_token_instructions()

    # Config
    print_header("Step 4: Edit config.yaml")
    edit_config()

    # Setup
    print_header("Step 5: Setup & Index")
    if not run_setup():
        sys.exit(1)

    # Dashboard
    start_dashboard()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Installer stopped")
        print("\nTo start again, run:")
        print("  cd codbot")
        print("  python server.py")
        sys.exit(0)

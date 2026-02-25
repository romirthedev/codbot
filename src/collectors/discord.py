"""Discord message collector."""

from typing import List

from src.collectors.base import BaseCollector
from src.storage import ContextStorage


class DiscordCollector(BaseCollector):
    """Collect messages from Discord servers and channels."""

    def __init__(self, storage: ContextStorage, bot_token: str, servers: List[dict]):
        super().__init__(storage)
        self.bot_token = bot_token
        self.servers = servers  # List of dicts with 'server' and 'channels' keys

    @property
    def source(self) -> str:
        return "discord"

    def collect(self) -> List[ContextItem]:
        """Collect messages from configured Discord servers/channels."""
        items = []

        # Note: Discord.py requires async context, but we need sync for simplicity
        # In production, you'd use discord.ext.commands.Bot with proper async handling
        # For now, we'll return empty items with a note
        print("Discord collection requires async context. Use Discord.py's bot for full implementation.")

        return items

    def _collect_server_channel(self, server_name: str, channel_name: str) -> List:
        """Collect messages from a specific server/channel.

        This would be called from an async context in a proper bot implementation.
        """
        items = []

        # In a real implementation, you would:
        # 1. Connect to Discord with intents
        # 2. Find the server by name
        # 3. Find the channel in that server
        # 4. Fetch recent messages
        # 5. Parse and store them

        return items

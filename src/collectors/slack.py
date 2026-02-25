"""Slack message collector."""

from datetime import datetime, timedelta
from typing import List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.collectors.base import BaseCollector
from src.storage import ContextItem, ContextStorage


class SlackCollector(BaseCollector):
    """Collect messages from Slack channels."""

    def __init__(self, storage: ContextStorage, bot_token: str, channels: List[str]):
        super().__init__(storage)
        self.client = WebClient(token=bot_token)
        self.channels = [c.lstrip("#") for c in channels]  # Remove # prefix if present

    @property
    def source(self) -> str:
        return "slack"

    def collect(self) -> List[ContextItem]:
        """Collect messages from configured channels."""
        items = []

        for channel in self.channels:
            try:
                items.extend(self._collect_channel(channel))
            except SlackApiError as e:
                print(f"Error collecting from channel {channel}: {e.response['error']}")

        return items

    def _collect_channel(self, channel: str) -> List[ContextItem]:
        """Collect messages from a single channel."""
        items = []

        # Get past 30 days of messages (Slack free tier is limited to 90 days total)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        timestamp = int(thirty_days_ago.timestamp())

        try:
            # Fetch conversations (threads)
            response = self.client.conversations_list(types="public_channel,private_channel")
            channel_id = None

            for conv in response["channels"]:
                if conv["name"] == channel:
                    channel_id = conv["id"]
                    break

            if not channel_id:
                print(f"Channel {channel} not found")
                return items

            # Get messages from the channel
            messages_response = self.client.conversations_history(
                channel=channel_id,
                oldest=str(timestamp),
                limit=100,  # Get up to 100 messages
            )

            for msg in messages_response.get("messages", []):
                # Skip bot messages and threads
                if msg.get("bot_id") or msg.get("thread_ts"):
                    continue

                user_id = msg.get("user", "unknown")
                try:
                    user_info = self.client.users_info(user=user_id)
                    username = user_info["user"]["real_name"]
                except SlackApiError:
                    username = user_id

                item_id = self._generate_id("slack", channel, msg.get("ts", ""))
                content = msg.get("text", "")

                items.append(
                    ContextItem(
                        id=item_id,
                        source="slack",
                        channel=channel,
                        title=f"Message from {username}",
                        content=content,
                        timestamp=datetime.fromtimestamp(float(msg.get("ts", 0))),
                        metadata={
                            "username": username,
                            "thread_ts": msg.get("thread_ts"),
                        },
                    )
                )

        except SlackApiError as e:
            print(f"Error fetching messages from {channel}: {e.response['error']}")

        return items

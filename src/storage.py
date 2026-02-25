"""Context storage and management."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List
import json


@dataclass
class ContextItem:
    """A single piece of context (message, doc, etc)."""
    id: str
    source: str  # "slack", "discord", "notion"
    channel: str
    title: str
    content: str
    timestamp: datetime
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "channel": self.channel,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContextItem":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            source=data["source"],
            channel=data["channel"],
            title=data["title"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class ContextStorage:
    """Manages storage of context items in local files."""

    def __init__(self, storage_path: Path = Path("context-store")):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_items(self, items: List[ContextItem], source: str) -> None:
        """Save context items for a source (Slack, Discord, etc)."""
        source_path = self.storage_path / source
        source_path.mkdir(parents=True, exist_ok=True)

        for item in items:
            # Save as JSON for structured data
            item_file = source_path / f"{item.channel}" / f"{item.id}.json"
            item_file.parent.mkdir(parents=True, exist_ok=True)

            with open(item_file, "w") as f:
                json.dump(item.to_dict(), f, indent=2)

    def load_all_items(self) -> List[ContextItem]:
        """Load all stored context items."""
        items = []

        if not self.storage_path.exists():
            return items

        for source_dir in self.storage_path.iterdir():
            if not source_dir.is_dir():
                continue

            for channel_dir in source_dir.iterdir():
                if not channel_dir.is_dir():
                    continue

                for item_file in channel_dir.glob("*.json"):
                    with open(item_file, "r") as f:
                        data = json.load(f)
                        items.append(ContextItem.from_dict(data))

        return items

    def get_items_by_source(self, source: str) -> List[ContextItem]:
        """Get items from a specific source."""
        items = []
        source_path = self.storage_path / source

        if not source_path.exists():
            return items

        for channel_dir in source_path.iterdir():
            if not channel_dir.is_dir():
                continue

            for item_file in channel_dir.glob("*.json"):
                with open(item_file, "r") as f:
                    data = json.load(f)
                    items.append(ContextItem.from_dict(data))

        return items

    def clear_source(self, source: str) -> None:
        """Clear all items from a source (useful for re-syncing)."""
        source_path = self.storage_path / source
        if source_path.exists():
            import shutil
            shutil.rmtree(source_path)

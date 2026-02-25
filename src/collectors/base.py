"""Base collector interface and utilities."""

from abc import ABC, abstractmethod
from typing import List
import hashlib

from src.storage import ContextItem, ContextStorage


class BaseCollector(ABC):
    """Base class for all platform collectors."""

    def __init__(self, storage: ContextStorage):
        self.storage = storage

    @abstractmethod
    def collect(self) -> List[ContextItem]:
        """Collect items from the platform.

        Should be implemented by subclasses.
        """
        pass

    def _generate_id(self, source: str, channel: str, unique_identifier: str) -> str:
        """Generate a unique ID for an item."""
        combined = f"{source}:{channel}:{unique_identifier}"
        return hashlib.md5(combined.encode()).hexdigest()

    def save_items(self, items: List[ContextItem]) -> None:
        """Save collected items to storage."""
        self.storage.save_items(items, self.source)

    @property
    @abstractmethod
    def source(self) -> str:
        """Return the source name (slack, discord, notion)."""
        pass

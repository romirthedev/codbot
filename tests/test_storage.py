"""Tests for context storage."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.storage import ContextItem, ContextStorage


class TestContextItem:
    """Test ContextItem class."""

    def test_create_item(self):
        """Test creating a context item."""
        item = ContextItem(
            id="test-1",
            source="slack",
            channel="general",
            title="Test Message",
            content="This is a test message",
            timestamp=datetime.now(),
        )
        assert item.id == "test-1"
        assert item.source == "slack"
        assert item.channel == "general"

    def test_item_to_dict(self):
        """Test converting item to dictionary."""
        now = datetime.now()
        item = ContextItem(
            id="test-1",
            source="slack",
            channel="general",
            title="Test",
            content="Content",
            timestamp=now,
        )
        data = item.to_dict()
        assert data["id"] == "test-1"
        assert data["source"] == "slack"

    def test_item_from_dict(self):
        """Test creating item from dictionary."""
        now = datetime.now()
        data = {
            "id": "test-1",
            "source": "slack",
            "channel": "general",
            "title": "Test",
            "content": "Content",
            "timestamp": now.isoformat(),
            "metadata": {},
        }
        item = ContextItem.from_dict(data)
        assert item.id == "test-1"
        assert item.source == "slack"


class TestContextStorage:
    """Test ContextStorage class."""

    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        storage = ContextStorage(Path(temp_dir))
        yield storage
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_save_and_load_items(self, temp_storage):
        """Test saving and loading items."""
        items = [
            ContextItem(
                id="item-1",
                source="slack",
                channel="general",
                title="Message 1",
                content="Content 1",
                timestamp=datetime.now(),
            ),
            ContextItem(
                id="item-2",
                source="slack",
                channel="general",
                title="Message 2",
                content="Content 2",
                timestamp=datetime.now(),
            ),
        ]

        temp_storage.save_items(items, "slack")
        loaded = temp_storage.load_all_items()

        assert len(loaded) == 2
        assert loaded[0].id == "item-1"
        assert loaded[1].id == "item-2"

    def test_get_items_by_source(self, temp_storage):
        """Test getting items by source."""
        slack_items = [
            ContextItem(
                id="slack-1",
                source="slack",
                channel="general",
                title="Slack Message",
                content="Content",
                timestamp=datetime.now(),
            )
        ]
        notion_items = [
            ContextItem(
                id="notion-1",
                source="notion",
                channel="pages",
                title="Notion Page",
                content="Content",
                timestamp=datetime.now(),
            )
        ]

        temp_storage.save_items(slack_items, "slack")
        temp_storage.save_items(notion_items, "notion")

        slack_loaded = temp_storage.get_items_by_source("slack")
        notion_loaded = temp_storage.get_items_by_source("notion")

        assert len(slack_loaded) == 1
        assert slack_loaded[0].id == "slack-1"
        assert len(notion_loaded) == 1
        assert notion_loaded[0].id == "notion-1"

    def test_clear_source(self, temp_storage):
        """Test clearing a source."""
        items = [
            ContextItem(
                id="item-1",
                source="slack",
                channel="general",
                title="Message",
                content="Content",
                timestamp=datetime.now(),
            )
        ]

        temp_storage.save_items(items, "slack")
        assert len(temp_storage.load_all_items()) == 1

        temp_storage.clear_source("slack")
        assert len(temp_storage.load_all_items()) == 0

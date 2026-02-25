"""Manage collection from multiple platforms."""

import logging

from src.config import Config, load_config
from src.storage import ContextStorage
from src.collectors.slack import SlackCollector
from src.collectors.discord import DiscordCollector
from src.collectors.notion import NotionCollector
from src.search import RelevanceSearch


logger = logging.getLogger(__name__)


class CollectorManager:
    """Orchestrate collection from all configured platforms."""

    def __init__(self, config: Config):
        self.config = config
        self.storage = ContextStorage()
        self.search = RelevanceSearch(self.storage)

    def collect_all(self) -> dict:
        """Collect from all enabled platforms.

        Returns:
            Dictionary with results for each platform
        """
        results = {"slack": {}, "discord": {}, "notion": {}}

        if self.config.slack.enabled:
            try:
                logger.info("Collecting from Slack...")
                collector = SlackCollector(
                    self.storage,
                    self.config.slack.bot_token,
                    self.config.slack.channels,
                )
                items = collector.collect()
                collector.save_items(items)
                results["slack"] = {
                    "status": "success",
                    "items_collected": len(items),
                }
                logger.info(f"Collected {len(items)} items from Slack")
            except Exception as e:
                results["slack"] = {
                    "status": "error",
                    "error": str(e),
                }
                logger.error(f"Error collecting from Slack: {e}")

        if self.config.discord.enabled:
            try:
                logger.info("Collecting from Discord...")
                collector = DiscordCollector(
                    self.storage,
                    self.config.discord.bot_token,
                    self.config.discord.servers,
                )
                items = collector.collect()
                collector.save_items(items)
                results["discord"] = {
                    "status": "success",
                    "items_collected": len(items),
                }
                logger.info(f"Collected {len(items)} items from Discord")
            except Exception as e:
                results["discord"] = {
                    "status": "error",
                    "error": str(e),
                }
                logger.error(f"Error collecting from Discord: {e}")

        if self.config.notion.enabled:
            try:
                logger.info("Collecting from Notion...")
                collector = NotionCollector(
                    self.storage,
                    self.config.notion.api_key,
                    self.config.notion.pages,
                )
                items = collector.collect()
                collector.save_items(items)
                results["notion"] = {
                    "status": "success",
                    "items_collected": len(items),
                }
                logger.info(f"Collected {len(items)} items from Notion")
            except Exception as e:
                results["notion"] = {
                    "status": "error",
                    "error": str(e),
                }
                logger.error(f"Error collecting from Notion: {e}")

        return results

    def reindex(self) -> None:
        """Rebuild the search index with all stored items."""
        logger.info("Reindexing all context items...")
        self.search.reindex_all()
        logger.info("Reindexing complete")

    def get_stats(self) -> dict:
        """Get statistics about collected context."""
        items = self.storage.load_all_items()
        by_source = {}

        for item in items:
            if item.source not in by_source:
                by_source[item.source] = 0
            by_source[item.source] += 1

        return {
            "total_items": len(items),
            "by_source": by_source,
        }


def run_collection_setup(config_path: str = "config.yaml") -> None:
    """Run the full collection setup process."""
    print("Team Context Collector Setup")
    print("=" * 50)

    config = load_config(config_path)

    # Validate configuration
    from src.config import validate_config
    warnings = validate_config(config)
    if warnings:
        print("\nConfiguration warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    # Run collection
    manager = CollectorManager(config)
    print("\nCollecting from enabled platforms...")
    results = manager.collect_all()

    print("\nCollection Results:")
    for platform, result in results.items():
        if result.get("status") == "success":
            print(f"  {platform}: {result['items_collected']} items collected")
        else:
            print(f"  {platform}: {result.get('error', 'skipped')}")

    # Reindex
    print("\nBuilding search index...")
    manager.reindex()

    # Stats
    stats = manager.get_stats()
    print(f"\nTotal items indexed: {stats['total_items']}")
    print("Setup complete!")

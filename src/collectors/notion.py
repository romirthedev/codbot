"""Notion page collector."""

from datetime import datetime
from typing import List

from notion_client import Client

from src.collectors.base import BaseCollector
from src.storage import ContextItem, ContextStorage


class NotionCollector(BaseCollector):
    """Collect pages and content from Notion."""

    def __init__(self, storage: ContextStorage, api_key: str, page_titles: List[str]):
        super().__init__(storage)
        self.client = Client(auth=api_key)
        self.page_titles = page_titles

    @property
    def source(self) -> str:
        return "notion"

    def collect(self) -> List[ContextItem]:
        """Collect pages from Notion."""
        items = []

        for page_title in self.page_titles:
            try:
                items.extend(self._collect_page(page_title))
            except Exception as e:
                print(f"Error collecting Notion page {page_title}: {e}")

        return items

    def _collect_page(self, page_title: str) -> List[ContextItem]:
        """Collect a single Notion page and its content."""
        items = []

        try:
            # Search for the page by title
            response = self.client.search(
                query=page_title,
                filter={"value": "page", "property": "object"},
            )

            if not response.get("results"):
                print(f"Page '{page_title}' not found in Notion")
                return items

            page = response["results"][0]
            page_id = page["id"]

            # Retrieve page content
            page_content = self.client.pages.retrieve(page_id)

            # Extract page title from properties
            title = page_title
            if "properties" in page_content:
                for prop_value in page_content["properties"].values():
                    if prop_value.get("type") == "title":
                        if prop_value.get("title"):
                            title = "".join([t["plain_text"] for t in prop_value["title"]])

            # Retrieve page blocks (content)
            content = self._extract_page_content(page_id)

            created_time = page_content.get("created_time", datetime.now().isoformat())
            if isinstance(created_time, str):
                created_time = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            elif not isinstance(created_time, datetime):
                created_time = datetime.now()

            item_id = self._generate_id("notion", "pages", page_id)

            items.append(
                ContextItem(
                    id=item_id,
                    source="notion",
                    channel="pages",
                    title=title,
                    content=content,
                    timestamp=created_time,
                    metadata={"page_id": page_id},
                )
            )

        except Exception as e:
            print(f"Error retrieving Notion page '{page_title}': {e}")

        return items

    def _extract_page_content(self, page_id: str) -> str:
        """Extract text content from a Notion page's blocks."""
        content_parts = []

        try:
            blocks = self.client.blocks.children.list(page_id)

            for block in blocks.get("results", []):
                text = self._extract_block_text(block)
                if text:
                    content_parts.append(text)

        except Exception as e:
            print(f"Error extracting content from page {page_id}: {e}")

        return "\n".join(content_parts)

    def _extract_block_text(self, block: dict) -> str:
        """Extract text from a single Notion block."""
        block_type = block.get("type")

        if block_type == "paragraph":
            texts = block.get("paragraph", {}).get("rich_text", [])
            return "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "heading_1":
            texts = block.get("heading_1", {}).get("rich_text", [])
            return "# " + "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "heading_2":
            texts = block.get("heading_2", {}).get("rich_text", [])
            return "## " + "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "heading_3":
            texts = block.get("heading_3", {}).get("rich_text", [])
            return "### " + "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "bulleted_list_item":
            texts = block.get("bulleted_list_item", {}).get("rich_text", [])
            return "- " + "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "numbered_list_item":
            texts = block.get("numbered_list_item", {}).get("rich_text", [])
            return "1. " + "".join([t.get("plain_text", "") for t in texts])

        elif block_type == "code":
            texts = block.get("code", {}).get("rich_text", [])
            language = block.get("code", {}).get("language", "")
            code_text = "".join([t.get("plain_text", "") for t in texts])
            return f"```{language}\n{code_text}\n```"

        return ""

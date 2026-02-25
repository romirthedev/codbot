"""Semantic search and relevance ranking for context items."""

from pathlib import Path
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
import chromadb

from src.storage import ContextItem, ContextStorage


class RelevanceSearch:
    """Semantic search over stored context using embeddings."""

    def __init__(self, storage: ContextStorage, db_path: Path = Path(".chromadb")):
        self.storage = storage
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize embedding model and vector DB
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(
            name="team_context",
            metadata={"hnsw:space": "cosine"},
        )

    def index_items(self, items: List[ContextItem]) -> None:
        """Add items to the search index."""
        if not items:
            return

        # Prepare documents and embeddings
        documents = []
        metadatas = []
        ids = []

        for item in items:
            # Combine title and content for embedding
            text = f"{item.title}\n{item.content}"
            documents.append(text)

            metadata = {
                "source": item.source,
                "channel": item.channel,
                "timestamp": item.timestamp.isoformat(),
            }
            metadata.update(item.metadata)
            metadatas.append(metadata)
            ids.append(item.id)

        # Generate embeddings and add to collection
        embeddings = self.model.encode(documents).tolist()
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def reindex_all(self) -> None:
        """Clear and rebuild the entire index."""
        # Clear existing collection
        self.client.delete_collection(name="team_context")
        self.collection = self.client.get_or_create_collection(
            name="team_context",
            metadata={"hnsw:space": "cosine"},
        )

        # Re-index all stored items
        all_items = self.storage.load_all_items()
        self.index_items(all_items)

    def search(self, query: str, top_k: int = 10, threshold: float = 0.5) -> List[Tuple[ContextItem, float]]:
        """Search for relevant context items.

        Args:
            query: Search query (can be code snippet, topic, etc)
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (ContextItem, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Search in chromadb
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        if not results.get("ids") or not results["ids"][0]:
            return []

        # Reconstruct ContextItems from results
        items_with_scores = []
        result_ids_list = results.get("ids", [[]])
        result_distances_list = results.get("distances", [[]])

        result_ids = result_ids_list[0] if result_ids_list else []
        result_distances = result_distances_list[0] if result_distances_list else []

        for idx, item_id in enumerate(result_ids):
            distance = result_distances[idx]
            # Convert distance to similarity (cosine distance to similarity)
            similarity = 1 - distance

            if similarity >= threshold:
                # Get full item from storage
                all_items = self.storage.load_all_items()
                for item in all_items:
                    if item.id == item_id:
                        items_with_scores.append((item, similarity))
                        break

        # Sort by similarity descending
        items_with_scores.sort(key=lambda x: x[1], reverse=True)
        return items_with_scores

    def search_with_context(self, code_content: str, top_k: int = 10, threshold: float = 0.5) -> List[str]:
        """Search based on code content being edited.

        Args:
            code_content: The code or file content being worked on
            top_k: Number of results to return
            threshold: Minimum similarity score

        Returns:
            List of formatted context strings
        """
        results = self.search(code_content, top_k=top_k, threshold=threshold)

        formatted = []
        for item, score in results:
            text = f"[{item.source.upper()}] {item.channel}: {item.title}\n{item.content}\n---\nRelevance: {score:.2f}"
            formatted.append(text)

        return formatted

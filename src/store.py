from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            try:
                self._client = chromadb.Client()
                self._collection = self._client.get_or_create_collection(name=collection_name)
                self._use_chroma = True
            except Exception:
                self._use_chroma = False
                self._collection = None
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": dict(doc.metadata or {}),
            "embedding": self._embedding_fn(doc.content),
            "doc_id": doc.id,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)
        scored_records: list[dict[str, Any]] = []

        for record in records:
            item_embedding = record.get("embedding", [])
            score = _dot(query_embedding, item_embedding) if item_embedding else 0.0
            scored_records.append({
                **record,
                "score": score,
                "content": record.get("content", ""),
                "metadata": record.get("metadata", {}),
            })

        scored_records.sort(key=lambda item: item["score"], reverse=True)
        return scored_records[: max(0, top_k)]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if self._use_chroma and self._collection is not None:
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            for doc in docs:
                record = self._make_record(doc)
                ids.append(doc.id)
                documents.append(doc.content)
                embeddings.append(record["embedding"])
                metadatas.append({**record["metadata"], "doc_id": doc.id})
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            return

        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            results = self._collection.query(query_texts=[query], n_results=top_k)
            output: list[dict[str, Any]] = []
            for i in range(len(results.get("documents", [[]])[0])):
                content = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                score = results.get("distances", [[0.0]])[0][i] if "distances" in results else 0.0
                output.append({
                    "id": results["ids"][0][i],
                    "content": content,
                    "metadata": metadata,
                    "score": float(score),
                })
            return output

        return [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": record["score"],
            }
            for record in self._search_records(query, self._store, top_k)
        ]

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            try:
                return self._collection.count()
            except Exception:
                return len(self._store)
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if metadata_filter is None:
            filtered_records = list(self._store)
        else:
            filtered_records = [
                record for record in self._store
                if all(record.get("metadata", {}).get(key) == value for key, value in metadata_filter.items())
            ]

        results = self._search_records(query, filtered_records, top_k)
        return [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": record["score"],
            }
            for record in results
        ]

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(where={"doc_id": doc_id})
                return True
            except Exception:
                pass

        original_count = len(self._store)
        self._store = [record for record in self._store if record.get("doc_id") != doc_id]
        return len(self._store) != original_count

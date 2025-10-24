"""Retriever module: Query Pinecone and return context for RAG."""

import os
import logging
from typing import List, Dict, Optional

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

logger = logging.getLogger(__name__)


class PineconeRetriever:
    """Retrieve documents from Pinecone index using semantic search."""

    def __init__(
        self,
        index_name: str,
        api_key: Optional[str] = None,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """Initialize retriever with Pinecone index and embedding model.

        Args:
            index_name: Name of the Pinecone index to query.
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var).
            model_name: SentenceTransformer model for embeddings.
        """
        self.index_name = index_name
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("Pinecone API key is required (PINECONE_API_KEY or api_key arg).")

        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_model = SentenceTransformer(model_name)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        include_metadata: bool = True,
    ) -> List[Dict]:
        """Retrieve top-k most similar documents for a query.

        Args:
            query: User query string.
            top_k: Number of top results to return.
            include_metadata: Whether to include metadata in results.

        Returns:
            List of dicts: {'text': str, 'metadata': {...}, 'score': float, 'id': str}
        """
        # Embed the query
        query_vector = self.embedding_model.encode(query, show_progress_bar=False).tolist()

        # Query Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=include_metadata,
        )

        # Format results
        retrieved = []
        for match in results.get("matches", []):
            item = {
                "id": match.get("id"),
                "score": match.get("score"),
                "text": match.get("metadata", {}).get("text", ""),
                "metadata": match.get("metadata", {}),
            }
            retrieved.append(item)

        return retrieved

    def retrieve_as_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve documents and format as context string for LLM.

        Args:
            query: User query string.
            top_k: Number of documents to retrieve.

        Returns:
            Formatted context string with retrieved chunks.
        """
        docs = self.retrieve(query, top_k=top_k)
        context_parts = []
        for i, doc in enumerate(docs, 1):
            text = doc.get("text", "").strip()
            source = doc.get("metadata", {}).get("source", "unknown")
            score = doc.get("score", 0)
            context_parts.append(f"[Chunk {i}] (source: {source}, similarity: {score:.2f})\n{text}")

        return "\n\n".join(context_parts)

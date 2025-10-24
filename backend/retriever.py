"""Retriever module: Query Pinecone and return context for RAG."""

import os
import logging
from typing import List, Dict, Optional

from huggingface_hub import InferenceClient
from pinecone import Pinecone

logger = logging.getLogger(__name__)


class PineconeRetriever:
    """Retrieve documents from Pinecone index using semantic search via HF API."""

    def __init__(
        self,
        index_name: str,
        api_key: Optional[str] = None,
        hf_token: Optional[str] = None,
    ):
        """Initialize retriever with Pinecone index and HF embedding API.

        Args:
            index_name: Name of the Pinecone index to query.
            api_key: Pinecone API key (defaults to PINECONE_API_KEY env var).
            hf_token: HF API token (defaults to HF_API_TOKEN env var).
        """
        self.index_name = index_name
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.hf_token = hf_token or os.getenv("HF_API_TOKEN")

        if not self.api_key:
            raise ValueError("Pinecone API key is required (PINECONE_API_KEY or api_key arg).")
        if not self.hf_token:
            raise ValueError("HF API token is required (HF_API_TOKEN or hf_token arg).")

        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(index_name)
        self.hf_client = InferenceClient(api_key=self.hf_token)

    def _embed_query(self, query: str) -> List[float]:
        """Embed query using HF Inference API via huggingface_hub library."""
        try:
            # Use the InferenceClient for feature extraction
            embedding = self.hf_client.feature_extraction(
                text=query,
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            # Convert numpy array to list if needed
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
            return embedding
        except Exception as e:
            logger.error("HF embedding error: %s", e)
            raise

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
        query_vector = self._embed_query(query)

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

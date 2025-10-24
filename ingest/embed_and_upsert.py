import os
import logging
from typing import List, Dict, Optional
from uuid import uuid4

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from .parse_docs import load_documents
from .chunker import chunk_documents

logger = logging.getLogger(__name__)


def embed_texts(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
	"""Embed a list of texts using a local SentenceTransformer model.

	Returns a list of float vectors.
	"""
	model = SentenceTransformer(model_name)
	vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
	# Ensure lists (python native) rather than numpy arrays -- Pinecone accepts lists
	return [v.tolist() for v in vectors]


def upsert_vectors(
	index_name: str,
	ids: List[str],
	vectors: List[List[float]],
	metadatas: Optional[List[Dict]] = None,
	api_key: Optional[str] = None,
	environment: Optional[str] = None,
	batch_size: int = 100,
	create_index_if_not_exists: bool = True,
):
	api_key = api_key or os.getenv("PINECONE_API_KEY")
	environment = environment or os.getenv("PINECONE_ENV")
	if not api_key:
		raise ValueError("Pinecone API key is required (env PINECONE_API_KEY or args).")

	pc = Pinecone(api_key=api_key)

	dim = len(vectors[0])
	existing_indexes = pc.list_indexes().names()
	if index_name not in existing_indexes:
		if create_index_if_not_exists:
			logger.info("Creating Pinecone index '%s' with dim=%d", index_name, dim)
			pc.create_index(
				name=index_name,
				dimension=dim,
				metric="cosine",
				spec=ServerlessSpec(
					cloud="aws",
					region=environment or "us-east-1"
				)
			)
		else:
			raise RuntimeError(f"Index {index_name} does not exist and create_index_if_not_exists=False")

	index = pc.Index(index_name)

	# Upsert in batches
	metadatas = metadatas or [None] * len(ids)
	for i in range(0, len(ids), batch_size):
		chunk_ids = ids[i : i + batch_size]
		chunk_vecs = vectors[i : i + batch_size]
		chunk_metas = metadatas[i : i + batch_size]
		to_upsert = [(cid, vec, meta) for cid, vec, meta in zip(chunk_ids, chunk_vecs, chunk_metas)]
		index.upsert(vectors=to_upsert)


def process_and_upsert(
	source: str,
	index_name: str,
	pinecone_api_key: Optional[str] = None,
	pinecone_env: Optional[str] = None,
	model_name: str = "all-MiniLM-L6-v2",
	chunk_size: int = 1000,
	chunk_overlap: int = 200,
):
	"""Load documents, chunk, embed locally, and upsert into Pinecone.

	Returns the number of chunks upserted.
	"""
	docs = load_documents(source)
	logger.info("Loaded %d documents from %s", len(docs), source)

	chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
	logger.info("Created %d chunks", len(chunks))

	if not chunks:
		return 0

	texts = [c["text"] for c in chunks]
	vectors = embed_texts(texts, model_name=model_name)

	ids = [c.get("id") or str(uuid4()) for c in chunks]
	metadatas = [c.get("metadata", {}) for c in chunks]

	upsert_vectors(index_name, ids, vectors, metadatas, pinecone_api_key, pinecone_env)
	return len(ids)


if __name__ == "__main__":
	import argparse
	from dotenv import load_dotenv

	load_dotenv()  # read .env if present
	logging.basicConfig(level=logging.INFO)

	ap = argparse.ArgumentParser(description="Embed local documents and upsert to Pinecone")
	ap.add_argument("source", help="file or directory to ingest")
	ap.add_argument("--index", required=True, help="Pinecone index name")
	ap.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
	ap.add_argument("--pinecone-key", default=None, help="Pinecone API key (or set PINECONE_API_KEY)")
	ap.add_argument("--pinecone-env", default=None, help="Pinecone environment (or set PINECONE_ENV)")
	ap.add_argument("--chunk-size", type=int, default=1000)
	ap.add_argument("--chunk-overlap", type=int, default=200)
	args = ap.parse_args()

	count = process_and_upsert(
		args.source,
		args.index,
		pinecone_api_key=args.pinecone_key,
		pinecone_env=args.pinecone_env,
		model_name=args.model,
		chunk_size=args.chunk_size,
		chunk_overlap=args.chunk_overlap,
	)
	print(f"Upserted {count} vectors into Pinecone index '{args.index}'")

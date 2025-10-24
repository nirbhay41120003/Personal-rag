from typing import List, Dict
import logging
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


def chunk_documents(docs: List[Dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
	"""Accepts list of {'text':..., 'metadata':{...}} and returns list of chunks.

	Each returned chunk is a dict: {'id': <str>, 'text': <str>, 'metadata': {...}}
	Uses LangChain's RecursiveCharacterTextSplitter for robust splitting.
	"""
	if not docs:
		return []

	text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size, chunk_overlap=chunk_overlap
	)

	lc_docs = [Document(page_content=d["text"], metadata=d.get("metadata", {})) for d in docs]
	split_docs = text_splitter.split_documents(lc_docs)

	out = []
	for i, sd in enumerate(split_docs):
		meta = dict(sd.metadata or {})
		meta.setdefault("chunk", i)
		out.append({"id": f"chunk-{i}", "text": sd.page_content, "metadata": meta})

	return out


if __name__ == '__main__':
	import argparse
	import logging as _logging

	_logging.basicConfig(level=_logging.INFO)
	ap = argparse.ArgumentParser()
	ap.add_argument("source", help="path to file containing text to chunk (for testing)")
	ap.add_argument("--size", type=int, default=1000)
	ap.add_argument("--overlap", type=int, default=200)
	args = ap.parse_args()
	p = Path(args.source)
	text = p.read_text(encoding="utf-8")
	docs = chunk_documents([{"text": text, "metadata": {"source": str(p)}}], args.size, args.overlap)
	print(f"Produced {len(docs)} chunks")

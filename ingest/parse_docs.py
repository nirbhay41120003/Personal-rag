# Simple document loaders for .txt, .md and .pdf
import logging
from pathlib import Path
from typing import List, Dict

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def _load_text_file(path: Path) -> str:
	return path.read_text(encoding="utf-8", errors="ignore")


def _load_pdf_file(path: Path) -> str:
	text_chunks = []
	try:
		reader = PdfReader(str(path))
		for page in reader.pages:
			text = page.extract_text() or ""
			text_chunks.append(text)
	except Exception as e:
		logger.exception("Failed to read PDF %s: %s", path, e)
	return "\n".join(text_chunks)


def load_documents(source: str) -> List[Dict]:
	"""Load documents from a file or directory.

	Returns a list of dicts: {'text': str, 'metadata': {'source': <path>, 'filename': <name>}}
	Supports: .txt, .md, .pdf (basic).
	"""
	p = Path(source)
	results = []

	if p.is_file():
		files = [p]
	elif p.is_dir():
		files = sorted([x for x in p.rglob("*") if x.is_file()])
	else:
		raise ValueError(f"source path not found: {source}")

	for f in files:
		suffix = f.suffix.lower()
		try:
			if suffix in {".txt", ".md"}:
				text = _load_text_file(f)
			elif suffix == ".pdf":
				text = _load_pdf_file(f)
			else:
				logger.debug("Skipping unsupported file type: %s", f)
				continue

			if not text or not text.strip():
				logger.debug("No text extracted from %s; skipping", f)
				continue

			results.append({
				"text": text,
				"metadata": {"source": str(f), "filename": f.name},
			})
		except Exception:
			logger.exception("Failed to load %s", f)

	return results


if __name__ == "__main__":
	import argparse

	logging.basicConfig(level=logging.INFO)
	ap = argparse.ArgumentParser()
	ap.add_argument("source", help="File or directory to load")
	args = ap.parse_args()
	docs = load_documents(args.source)
	print(f"Loaded {len(docs)} documents")

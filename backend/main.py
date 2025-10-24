"""FastAPI backend for RAG system with Perplexity Sonar LLM."""

import os
import logging
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.retriever import PineconeRetriever
from backend.prompts import build_rag_prompt, format_context_for_prompt, build_simple_prompt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Personal RAG", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Perplexity API config
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"  # or "sonar-pro" for better quality

# Pinecone config
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "personal-rag")

# Global retriever instance (lazy-loaded)
retriever = None


def get_retriever() -> PineconeRetriever:
    """Get or initialize the Pinecone retriever."""
    global retriever
    if retriever is None:
        retriever = PineconeRetriever(index_name=PINECONE_INDEX)
        logger.info("Initialized Pinecone retriever with index: %s", PINECONE_INDEX)
    return retriever


def call_perplexity(system_prompt: str, user_message: str) -> str:
    """Call Perplexity Sonar API.

    Args:
        system_prompt: System prompt/instructions.
        user_message: User's message.

    Returns:
        Response text from Perplexity.

    Raises:
        HTTPException if API call fails.
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error("Perplexity API error: %s", e)
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {str(e)}")


# Request/Response models
class ChatRequest(BaseModel):
    query: str
    use_rag: bool = True
    top_k: int = 5


class ChatResponse(BaseModel):
    query: str
    response: str
    context_used: Optional[list] = None
    model: str = PERPLEXITY_MODEL


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "model": PERPLEXITY_MODEL}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint: retrieve context from Pinecone and call Perplexity Sonar.

    Args:
        request: ChatRequest with query, use_rag flag, and top_k.

    Returns:
        ChatResponse with response text and optional context used.
    """
    try:
        context_used = []

        if request.use_rag:
            # Retrieve context from Pinecone
            retriever_instance = get_retriever()
            docs = retriever_instance.retrieve(request.query, top_k=request.top_k)
            context_str = format_context_for_prompt(docs)
            context_used = docs

            # Build RAG prompt
            system_prompt, user_message = build_rag_prompt(request.query, context_str)
        else:
            # Simple chat without RAG
            system_prompt, user_message = build_simple_prompt(request.query)

        # Call Perplexity Sonar
        response_text = call_perplexity(system_prompt, user_message)

        return ChatResponse(
            query=request.query,
            response=response_text,
            context_used=context_used,
            model=PERPLEXITY_MODEL,
        )

    except Exception as e:
        logger.exception("Error in /chat endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve")
async def retrieve(request: ChatRequest):
    """Retrieve endpoint: only return context without calling LLM."""
    try:
        retriever_instance = get_retriever()
        docs = retriever_instance.retrieve(request.query, top_k=request.top_k)
        return {
            "query": request.query,
            "documents": docs,
            "count": len(docs),
        }
    except Exception as e:
        logger.exception("Error in /retrieve endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query-without-rag")
async def query_without_rag(request: ChatRequest):
    """Query Perplexity without RAG context."""
    try:
        system_prompt, user_message = build_simple_prompt(request.query)
        response_text = call_perplexity(system_prompt, user_message)
        return ChatResponse(
            query=request.query,
            response=response_text,
            model=PERPLEXITY_MODEL,
        )
    except Exception as e:
        logger.exception("Error in /query-without-rag endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

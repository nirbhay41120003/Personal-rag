"""Prompt templates and utilities for RAG with Perplexity Sonar."""

RAG_SYSTEM_PROMPT = """You are a helpful, knowledgeable assistant that answers questions based on provided context.

Guidelines:
- Use the provided context to answer questions accurately.
- If the context doesn't contain relevant information, say so clearly.
- Be concise but thorough.
- Cite sources when referencing specific information from the context.
- If unsure, ask for clarification or suggest related topics."""

RAG_USER_PROMPT_TEMPLATE = """Based on the following context, answer this question:

Question: {query}

Context:
{context}

Answer:"""

SIMPLE_SYSTEM_PROMPT = """You are a helpful assistant. Answer questions clearly and concisely."""


def build_rag_prompt(query: str, context: str) -> tuple:
    """Build system and user prompts for RAG query.

    Args:
        query: User's question.
        context: Retrieved context from Pinecone.

    Returns:
        Tuple of (system_prompt, user_message).
    """
    user_message = RAG_USER_PROMPT_TEMPLATE.format(query=query, context=context)
    return RAG_SYSTEM_PROMPT, user_message


def build_simple_prompt(query: str) -> tuple:
    """Build system and user prompts for simple chat (no RAG).

    Args:
        query: User's question.

    Returns:
        Tuple of (system_prompt, user_message).
    """
    return SIMPLE_SYSTEM_PROMPT, query


def format_context_for_prompt(retrieved_docs: list) -> str:
    """Format retrieved documents for inclusion in prompt.

    Args:
        retrieved_docs: List of dicts from retriever with 'text', 'metadata', etc.

    Returns:
        Formatted context string.
    """
    if not retrieved_docs:
        return "No relevant context found."

    parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        text = doc.get("text", "").strip()
        source = doc.get("metadata", {}).get("source", "unknown")
        filename = doc.get("metadata", {}).get("filename", "unknown")
        score = doc.get("score", 0)
        parts.append(f"[Source {i}] {filename} (similarity: {score:.2f})\n{text}")

    return "\n\n---\n\n".join(parts)

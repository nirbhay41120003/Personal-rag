import axios from 'axios';

// API base URL - adjust if your backend is on a different host/port
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Chat with the RAG system
 * @param {string} query - User query
 * @param {boolean} useRag - Whether to use RAG context (default: true)
 * @param {number} topK - Number of context chunks to retrieve (default: 5)
 * @returns {Promise<Object>} Response with answer and context
 */
export const chatWithRAG = async (query, useRag = true, topK = 5) => {
  try {
    const response = await api.post('/chat', {
      query,
      use_rag: useRag,
      top_k: topK,
    });
    return response.data;
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
};

/**
 * Retrieve context documents for a query (without calling LLM)
 * @param {string} query - User query
 * @param {number} topK - Number of documents to retrieve
 * @returns {Promise<Object>} Retrieved documents
 */
export const retrieveContext = async (query, topK = 5) => {
  try {
    const response = await api.post('/retrieve', {
      query,
      use_rag: true,
      top_k: topK,
    });
    return response.data;
  } catch (error) {
    console.error('Retrieve API error:', error);
    throw error;
  }
};

/**
 * Query without RAG (direct Perplexity call)
 * @param {string} query - User query
 * @returns {Promise<Object>} Response from Perplexity
 */
export const queryWithoutRAG = async (query) => {
  try {
    const response = await api.post('/query-without-rag', {
      query,
    });
    return response.data;
  } catch (error) {
    console.error('Query without RAG error:', error);
    throw error;
  }
};

/**
 * Health check
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

export default api;

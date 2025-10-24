# Migration to Hugging Face Inference API

## What Changed?

✅ **Old**: Local SentenceTransformer model (~500MB download, slow embedding)  
✅ **New**: Hugging Face Inference API (cloud-based, fast, no local model needed)

## Benefits

1. **Smaller deployment** (~100MB instead of 600MB+)
2. **Faster deployment** (no model download)
3. **No GPU needed** (API handles it)
4. **Easier scaling** (use HF API tier system)
5. **Consistent embeddings** (HF maintains the model)

## What You Need

Get a free Hugging Face API token:
1. Go to https://huggingface.co/settings/tokens
2. Create new token (read-only is fine)
3. Copy the token

## Update Your Local Setup

### 1. Update .env
```bash
# Copy the new .env.example
cp .env.example .env

# Edit .env and add:
HF_API_TOKEN=hf_xxxxxxxxxxxxx  # Your HF token
```

### 2. Re-embed Your Documents

Since embeddings changed slightly (we're using the same model but via API), you may want to re-embed:

```bash
# This will create NEW embeddings in Pinecone (using HF API)
python -m ingest.embed_and_upsert /path/to/docs --index personal-rag
```

**Option**: Keep old embeddings if they're working. HF's all-MiniLM-L6-v2 produces the same 384-dim vectors.

### 3. Test Locally
```bash
# Start backend
python -m backend.main

# In another terminal, test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is in the documents?", "use_rag": true, "top_k": 5}'
```

## Deploy to Railway

1. Add these environment variables in Railway:
   ```
   PINECONE_API_KEY=...
   PINECONE_ENV=us-east-1
   PINECONE_INDEX=personal-rag
   PERPLEXITY_API_KEY=...
   HF_API_TOKEN=...
   ```

2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Migrate to HF Inference API for embeddings"
   git push
   ```

3. Railway auto-redeploys

## Rollback (if needed)

If you want to go back to local embeddings:

```bash
git revert HEAD~1  # Undo the last commit
git push
```

## Cost Impact

- **HF API**: FREE tier (up to 30k requests/month)
  - ~0.0001 tokens per 1000 chars
  - ~$1-5/month if you exceed free tier
- **Pinecone**: No change
- **Perplexity**: No change
- **Railway**: No change

## Support

- HF API docs: https://huggingface.co/docs/hub/models-inference
- Check rate limits: https://huggingface.co/settings/billing
- Add payment method if needed: https://huggingface.co/settings/billing/subscription

Done! Your system is now lighter and easier to deploy. 🚀

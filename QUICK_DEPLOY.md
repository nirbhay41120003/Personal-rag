# 🚀 Quick Deploy Guide (5 Minutes)

## Fastest Way to Deploy on Vercel

### Step 1: Prepare GitHub
```bash
cd /Users/nirbhay/Desktop/personalrag

# Initialize Git (if not already)
git init
git add .
git commit -m "Personal RAG system"

# Push to GitHub
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/personalrag.git
git push -u origin main
```

### Step 2: Deploy Frontend on Vercel (2 mins)

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. **Root Directory**: Change to `frontend`
4. Click "Deploy"
5. Wait ~2 mins...
6. Copy the deployed URL: `https://your-app.vercel.app`

### Step 3: Deploy Backend on Railway (2 mins)

1. Go to https://railway.app (sign up)
2. New Project → Deploy from GitHub
3. Select your repo
4. Add these environment variables:
   ```
   PINECONE_API_KEY=your_key
   PINECONE_ENV=us-east-1
   PINECONE_INDEX=personal-rag
   PERPLEXITY_API_KEY=your_key
   PORT=8000
   ```
5. Wait for deploy...
6. Copy the backend URL: `https://your-backend.railway.app`

### Step 4: Connect Them (1 min)

1. Go back to Vercel Dashboard
2. Project Settings → Environment Variables
3. Add/Update `VITE_API_URL`:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```
4. Redeploy (git push any change or click "Redeploy")

### Done! ✅

Your app is live at: `https://your-app.vercel.app`

---

## Troubleshooting

### Backend deploy fails
- Check all 4 env vars are set
- Make sure `gunicorn` is in requirements.txt
- Check logs in Railway dashboard

### Frontend can't reach backend
- Verify backend URL in Vercel env vars
- Test: Open DevTools Console, run:
  ```javascript
  fetch('https://your-backend.railway.app/health').then(r => r.json()).then(console.log)
  ```

### Pinecone connection error
- Verify API key is correct
- Check env name: `PINECONE_ENV=us-east-1` (not `PINECONE_ENVIRONMENT`)
- Verify index exists: `PINECONE_INDEX=personal-rag`

---

## Cost

- **Vercel Frontend**: FREE (up to 100GB/month)
- **Railway Backend**: $5/month (first $5 free credit)
- **Total**: ~$5/month or FREE with credits

---

## Next Steps

1. Embed frontend in your website
2. Add database for chat history
3. Monitor with Sentry or similar
4. Scale as needed

See `DEPLOYMENT.md` for advanced options (Render, Fly.io, Heroku, etc.)

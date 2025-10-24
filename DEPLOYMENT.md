# 🚀 Personal RAG Deployment Guide

This guide covers deploying your Personal RAG system (Frontend + Backend) on Vercel and other platforms.

## Architecture

- **Frontend**: React + Vite (Vercel)
- **Backend**: FastAPI (External hosting required - Vercel doesn't support long-running FastAPI servers)
- **Data**: Pinecone (Managed, already cloud-hosted)

---

## Part 1: Deploy Frontend on Vercel ✅ Easy

### Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub account with your repo
- Backend already deployed or accessible

### Step 1: Push Code to GitHub

```bash
cd /Users/nirbhay/Desktop/personalrag
git init
git add .
git commit -m "Initial commit: Personal RAG system"
git remote add origin https://github.com/YOUR_USERNAME/personalrag.git
git branch -M main
git push -u origin main
```

### Step 2: Create Vercel Project

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `personalrag` repo
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Set Environment Variables

In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add this variable:
   ```
   Name: VITE_API_URL
   Value: https://your-backend-url.com  (or your backend hosting URL)
   ```

### Step 4: Deploy

Click "Deploy" and wait for it to complete!

Your frontend will be live at: `https://your-project-name.vercel.app`

---

## Part 2: Deploy Backend ⚠️ More Complex

### Option A: Railway (Recommended for FastAPI) 🚂

Railway is ideal for FastAPI apps.

#### Setup:

1. **Create Railway Account**: https://railway.app
2. **Connect GitHub**: Link your repository
3. **Create New Project**:
   - Select "Deploy from GitHub"
   - Select your repo
   - Set root directory: `/backend` (or root if backend in root)

4. **Add Environment Variables** in Railway:
   ```
   PINECONE_API_KEY=your_key_here
   PINECONE_ENV=us-east-1
   PINECONE_INDEX=personal-rag
   PERPLEXITY_API_KEY=your_key_here
   PORT=8000
   ```

5. **Create Procfile** in backend root:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
   ```
   Install gunicorn: `pip install gunicorn`

6. **Deploy**: Railway auto-deploys on git push

Your backend will be at: `https://your-railway-app.up.railway.app`

---

### Option B: Render (Easy Alternative) 🎨

1. **Sign up**: https://render.com
2. **Create New Service** → Web Service
3. **Connect GitHub repo**
4. **Configure**:
   - **Name**: personal-rag-backend
   - **Environment**: Python 3.9
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - **Region**: Choose closest to you

5. **Add Environment Variables**:
   ```
   PINECONE_API_KEY=your_key_here
   PINECONE_ENV=us-east-1
   PINECONE_INDEX=personal-rag
   PERPLEXITY_API_KEY=your_key_here
   ```

6. **Deploy**: Click "Create Web Service"

Your backend will be at: `https://your-render-app.onrender.com`

---

### Option C: Fly.io (Scalable) ✈️

```bash
# Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/

# Login
flyctl auth login

# Create app in backend directory
cd /Users/nirbhay/Desktop/personalrag/backend
flyctl launch

# Follow prompts, then:
# Set environment variables
flyctl secrets set PINECONE_API_KEY=your_key_here
flyctl secrets set PINECONE_ENV=us-east-1
flyctl secrets set PINECONE_INDEX=personal-rag
flyctl secrets set PERPLEXITY_API_KEY=your_key_here

# Deploy
flyctl deploy
```

---

## Part 3: Connect Frontend to Backend

### After Backend is Deployed

1. **Get your backend URL** (e.g., `https://your-backend.railway.app`)
2. **Update Vercel environment variable**:
   - Dashboard → Project Settings → Environment Variables
   - Update `VITE_API_URL` to your backend URL
   - Redeploy frontend (git push or manual trigger)

---

## Recommended Setup

For best results:

| Component | Platform | Why |
|-----------|----------|-----|
| Frontend (React) | **Vercel** | Free, fast, optimized for static sites |
| Backend (FastAPI) | **Railway** or **Render** | Good FastAPI support, affordable |
| Data (Pinecone) | **Pinecone Cloud** | Already hosted, serverless |

---

## Deployment Checklist

### Frontend (Vercel)
- [ ] Code pushed to GitHub
- [ ] Vercel project created
- [ ] `VITE_API_URL` environment variable set
- [ ] Frontend deployed and working

### Backend (Railway/Render/Fly)
- [ ] All 4 environment variables set:
  - `PINECONE_API_KEY`
  - `PINECONE_ENV`
  - `PINECONE_INDEX`
  - `PERPLEXITY_API_KEY`
- [ ] Backend deployed and responding to `/health` endpoint
- [ ] CORS enabled (already in code)

### Integration
- [ ] Frontend can reach backend API
- [ ] Chat endpoint `/chat` works
- [ ] Retrieve endpoint `/retrieve` works
- [ ] Error messages appear if API unreachable

---

## Troubleshooting

### "Cannot connect to backend" error

**Check:**
1. Backend URL is correct in `VITE_API_URL`
2. Backend is running and deployed
3. Backend `/health` endpoint responds
4. CORS is enabled (check `main.py` has CORSMiddleware)

**Debug in browser console:**
```javascript
fetch('https://your-backend-url.com/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

### Backend times out

- Railway/Render may cold-start (delay on first request)
- Consider paid tier for always-on servers
- Or use Fly.io which has better cold-start performance

### Pinecone connection fails

- Verify API key and environment in backend secrets
- Check Pinecone index exists
- Ensure region matches: `PINECONE_ENV=us-east-1`

---

## Production Optimization

### Frontend
```bash
# Generate production build
npm run build

# Test locally
npm run preview
```

### Backend
- Add logging and monitoring (Sentry, etc.)
- Use database for chat history (PostgreSQL)
- Add rate limiting
- Enable request caching where possible

---

## Cost Estimate (Monthly)

- **Vercel**: Free tier (up to 100GB bandwidth)
- **Railway**: $5-20 depending on usage
- **Render**: Free tier available, $7+ for always-on
- **Pinecone**: Free tier (1M vectors), $1+ per M vectors
- **Perplexity API**: Pay-as-you-go (~$0.002/request)

**Total**: ~$10-50/month for production

---

## Next Steps

1. Deploy frontend first (easier, Vercel)
2. Deploy backend second (pick Railway or Render)
3. Connect them together
4. Test end-to-end
5. Monitor logs for errors

Questions? Check platform docs:
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs

# Personal RAG Frontend

React + Vite frontend for the Personal RAG chatbot system.

## Setup

```bash
cd /Users/nirbhay/Desktop/personalrag/frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

## Features

- **Chat Interface**: Real-time messaging with the RAG system
- **RAG Toggle**: Switch between RAG-enhanced and direct Perplexity queries
- **Context Display**: View retrieved document chunks with similarity scores
- **Top-K Control**: Adjust number of context documents to retrieve
- **Responsive Design**: Works on desktop and mobile
- **Auto-scroll**: Messages auto-scroll to bottom
- **Loading State**: Visual feedback while waiting for responses

## Environment

If your backend is not on localhost:8000, set the API URL:

```bash
# Create a .env file in the frontend directory
echo "VITE_API_URL=http://your-backend-url:8000" > .env
```

## Build for Production

```bash
npm run build
npm run preview
```

Built files will be in `dist/` folder.

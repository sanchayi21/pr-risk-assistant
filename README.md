# PR Risk Assistant

An AI-powered pull request review tool that automatically analyzes GitHub PR diffs, generates structured code reviews, and displays risk scores on a dashboard.

## What it does

- Listens for GitHub pull request events via webhook
- Fetches the code diff from GitHub API
- Sends the diff to Groq LLM with a structured prompt
- Returns a review with: summary, bugs, security issues, test gaps, and risk score (1-10)
- Saves everything to PostgreSQL
- Displays results on a React dashboard

## Tech Stack

**Backend:** FastAPI, Python, SQLAlchemy, PostgreSQL (Neon), Groq LLM, GitHub Webhooks

**Frontend:** React, TypeScript, Tailwind CSS, Vite

**DevOps:** Docker, Render (backend), Vercel (frontend)

## Architecture


GitHub PR Opened
      ↓
Webhook → FastAPI Backend (Render)
      ↓
Fetch diff via GitHub API
      ↓
Send diff to Groq LLM
      ↓
Parse structured review (JSON)
      ↓
Save to PostgreSQL (Neon)
      ↓
React Dashboard (Vercel)


## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file in `/backend`:

```
DATABASE_URL=your_neon_postgres_url
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
```

Initialize the database:

```bash
python init_db.py
```

Start the server:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Webhook Setup

1. Use [ngrok](https://ngrok.com) to expose your local backend:
```bash
ngrok http 8000
```

2. Go to your GitHub repo → Settings → Webhooks → Add webhook
3. Set Payload URL to: `https://your-ngrok-url/webhook`
4. Content type: `application/json`
5. Select: Pull requests only

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/webhook` | GitHub webhook receiver |
| GET | `/prs` | List all pull requests |
| GET | `/prs/{id}` | Get PR with full AI review |

## Deployment

- **Backend:** Render (free tier) — auto-deploys from GitHub
- **Frontend:** Vercel — auto-deploys from GitHub
- **Database:** Neon (serverless PostgreSQL)

## Live Demo

- Frontend: [pr-risk-assistant.vercel.app](https://pr-risk-assistant.vercel.app)
- Backend API: [pr-risk-assistant.onrender.com](https://pr-risk-assistant.onrender.com)



## Author

Sanchayi Sharma — [GitHub](https://github.com/sanchayi21) · [LinkedIn](https://www.linkedin.com/in/sanchayi21/)


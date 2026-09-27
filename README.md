# Vera Bot — Deployment Package (SoloSpark)

This folder contains the complete, self-contained standalone application ready for immediate deployment to any cloud hosting provider or via a tunneling service (like ngrok).

---

## 📁 Package Contents

| File | Purpose |
|---|---|
| `bot.py` | FastAPI application exposing all 5 mandatory endpoints (`/v1/healthz`, `/v1/metadata`, `/v1/context`, `/v1/tick`, `/v1/reply`, plus `/v1/teardown`) |
| `composer.py` | 4-context LLM engagement composer adhering to the scoring rubric |
| `context_store.py` | In-memory versioned context store with deduplication and fast retrieval |
| `conversation_manager.py` | Multi-turn state tracker, auto-reply counter, and suppression registry |
| `reply_handler.py` | Multi-turn dialogue generator for replies and edge cases |
| `prompt_templates.py` | Clinical/domain voice prompts, trigger variants, and compulsion levers |
| `llm_client.py` | OpenRouter API client supporting free model routing |
| `requirements.txt` | Python dependencies list |
| `Dockerfile` | Container configuration for Docker-based platforms (Render, Railway, Fly.io, Cloud Run) |
| `Procfile` | Process file for PaaS platforms |
| `start.sh` | Shell script to start uvicorn with dynamic `$PORT` support |

---

## 🌐 Where to Deploy (Comparison & Recommendations)

For this challenge, your bot needs a **public HTTPS URL** reachable by the magicpin judge.

| Platform | Difficulty | Cost | Free Tier? | Sleep when idle? | Recommended For |
|---|---|---|---|---|---|
| **Render** | Very Easy | Free | Yes | Sleeps after 15 min idle (wakes on ping) | ⭐ Best overall free PaaS |
| **Railway** | Very Easy | $5 free credit | Yes (trial) | No sleep | ⭐ Fast, reliable, no cold start |
| **ngrok** (Local) | Easiest | Free | Yes | Never (runs on your Mac) | ⭐ Ideal for instant testing & evaluation |
| **Fly.io** | Moderate | Free tier | Yes | Low latency | Good for global low-latency |
| **Koyeb** | Easy | Free | Yes | Fast deployments | Solid free container host |

---

## 🚀 Option 1: Render (Recommended Free PaaS)

1. Push this folder or your repository to **GitHub**.
2. Go to [render.com](https://render.com) and create an account.
3. Click **New +** -> **Web Service**.
4. Select your GitHub repository.
5. Configure the service:
   - **Name**: `solospark-vera-bot`
   - **Root Directory**: `deployment` (or leave empty if deploying a standalone repo)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn bot:app --host 0.0.0.0 --port $PORT`
6. Under **Environment Variables**, add:
   - `OPENROUTER_API_KEY`: `your_openrouter_api_key`
   - `OPENROUTER_MODEL`: `openrouter/free`
7. Click **Create Web Service**.
8. Once deployed, Render gives you a public URL like:
   `https://solospark-vera-bot.onrender.com`

---

## 🚀 Option 2: Railway (Zero Cold-Start)

1. Go to [railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. If deploying from a subfolder, in settings set **Root Directory** to `deployment`.
5. Under **Variables**, add:
   - `OPENROUTER_API_KEY`: `your_openrouter_api_key`
   - `OPENROUTER_MODEL`: `openrouter/free`
6. Go to **Settings** -> **Networking** -> click **Generate Domain**.
7. Railway will generate a public URL like:
   `https://solospark-vera-bot.up.railway.app`

---

## 🚀 Option 3: ngrok (Instant Public HTTPS for Local Testing)

If your bot is already running locally on your laptop:

1. Install ngrok (if not already installed):
   ```bash
   brew install ngrok
   ```
2. Start your local bot server:
   ```bash
   python3 -m src.bot
   ```
3. In another terminal, open an HTTPS tunnel:
   ```bash
   ngrok http 8000
   ```
4. ngrok will display a forwarding URL like:
   `https://a1b2-c3d4.ngrok-free.app`
5. This HTTPS URL is live and immediately reachable by the magicpin judge!

---

## 🧪 Testing Your Deployed Bot

Once deployed, you can verify your remote bot with the judge simulator:

1. In `.env` or in your terminal:
   ```bash
   export BOT_URL="https://your-deployed-bot-url.com"
   ```
2. Run the judge:
   ```bash
   python3 judge_simulator.py
   ```
3. Check the endpoints directly in your browser or with curl:
   - `curl https://your-deployed-bot-url.com/v1/healthz`
     -> `{"status": "ok", "contexts_loaded": {...}}`
   - `curl https://your-deployed-bot-url.com/v1/metadata`
     -> `{"team_name": "solospark", ...}`

---

## 📋 Endpoints Implemented

- `GET /v1/healthz` — Liveness check and context counts
- `GET /v1/metadata` — Team info and model details
- `POST /v1/context` — Idempotent versioned context ingestion
- `POST /v1/tick` — Proactive trigger composition
- `POST /v1/reply` — Multi-turn conversation handling (intent transition, auto-reply detection, polite opt-outs)
- `POST /v1/teardown` — In-memory state cleanup

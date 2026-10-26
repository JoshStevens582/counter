# Counter

Customer website chat for **Custom Chat and Automation**. Visitors ask without logging in. Answers come from approved pages (prices, hours, services). If the pages do not say it, Counter says it does not know. Counter does not book or send mail.

**Live (after deploy):** `https://counter.customchatandautomation.co.za`

## Demo script (2 minutes)

1. Open the sample physio site. Click **What does a session cost?** — answer **R650** with **Session fees** in **Pages used**.
2. **What time do you close?** — **5:00 PM**, **Opening hours** cited.
3. **Do you treat sports injuries?** — from **What we offer**.
4. **Book me Tuesday at 2** — may quote the fee if asked, then refuses to book; tells them to contact reception.

## Stack

| Layer | Choice |
| :--- | :--- |
| API | FastAPI, public `POST /api/chat/stream` (SSE) |
| Vector DB | ChromaDB + OpenAI embeddings |
| Retrieve | Vectors + BM25, RRF |
| Limits | Redis per-IP + global daily caps (fail closed in production) |
| UI | React sample site + floating chat widget |
| Ship | Docker Compose — web (Caddy), api, redis |

## Run locally

Python 3.12+, Node 22+. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. For local dev without Redis:

```env
RATE_LIMIT_ENABLED=false
```

```powershell
cd C:\Users\Joshua\Desktop\Counter
uv sync --group dev
uv run uvicorn counter.main:app --reload --host 127.0.0.1 --port 8788 --app-dir src
```

Second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:5174](http://localhost:5174). API is proxied to port 8788.

Re-index after editing `pages/` (stop the API first):

```powershell
uv run python -m counter.reset_pages
```

## Docker (local smoke test)

```powershell
docker compose up -d --build
```

Site on [http://localhost:8080](http://localhost:8080). Production: set `SITE_ADDRESS` in `.env` — see [docs/deploy.md](docs/deploy.md).

## Quality checks

```powershell
uv run ruff check .
uv run mypy .
uv run pytest --cov=counter --cov-branch
```

## Vault

[[Counter — What it is]] · [[Counter — Session Mon 2026-10-26]] in Dev Log.

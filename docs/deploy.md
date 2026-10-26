# Deploy Counter

Production shape matches Atlas: **web** (Caddy + React) → **api** (FastAPI) → **redis**.

## Server (same VPS as Atlas)

Counter shares **one HTTPS front door** with Atlas. Full steps: [deploy/with-atlas-edge.md](../deploy/with-atlas-edge.md).

Summary:

1. DNS: `counter.customchatandautomation.co.za` → VPS IP.
2. `docker network create cca-edge` (once).
3. Clone to `/opt/counter`, `.env` with `OPENAI_API_KEY`, `CORS_ORIGINS` empty.
4. `docker compose -f docker-compose.yml -f deploy/compose.edge.yml up -d --build`
5. Pull Atlas (Caddy already includes the Counter site block) and redeploy Atlas `web` on `cca-edge`.
6. Open `https://counter.customchatandautomation.co.za`.

## After page edits

Stop the API, re-index, restart:

```bash
docker compose stop api
docker compose run --rm api python -m counter.reset_pages
docker compose up -d api
```

Data lives in the `counter-data` volume.

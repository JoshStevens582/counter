# Counter behind Atlas Caddy (one VPS, one :443)

Atlas already owns ports 80 and 443. Counter runs **without** publishing those ports and joins a shared Docker network.

## One-time on the server

```bash
docker network create cca-edge
```

## Counter (`/opt/counter`)

```bash
git clone https://github.com/JoshStevens582/counter.git /opt/counter
cd /opt/counter
cp .env.example .env
# Set OPENAI_API_KEY. Leave CORS_ORIGINS empty for production.
docker compose up -d --build
```

Containers `counter-api` and `counter-web` must be on `cca-edge` (defined in this repo's `docker-compose.yml`).

## Atlas (`/opt/atlas`)

Merge the Counter site block into `deploy/Caddyfile` (see `deploy/caddy-atlas-counter.caddy` in this repo), then attach the Atlas **web** container to `cca-edge`:

Redeploy Atlas **web** with the edge overlay (see `deploy/compose.counter-edge.yml` in the Atlas repo):

```bash
cd /opt/atlas && git pull && docker compose -f docker-compose.yml -f deploy/compose.counter-edge.yml up -d --build web
```

## DNS

`counter.customchatandautomation.co.za` A record → same IP as Atlas. Caddy in Atlas web obtains the certificate for the Counter host name.

## Verify

```bash
curl -fsS https://counter.customchatandautomation.co.za/api/health
curl -fsS https://counter.customchatandautomation.co.za/ | grep -q 'id="root"'
```

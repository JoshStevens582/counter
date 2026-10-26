# Counter — Production steps

Checklist for a public Counter demo (Custom Chat and Automation).

1. [x] Code on GitHub; CI green (backend, frontend, docker build; optional full stack smoke when `OPENAI_API_KEY` repo secret is set).
2. [x] DNS `counter.customchatandautomation.co.za` → `102.203.81.249` (domains.co.za).
3. [x] `/opt/counter` on the server: clone, `.env` with `OPENAI_API_KEY`, no CORS origins (same-origin via Caddy).
4. [x] Docker network `cca-edge` created; Counter stack up (`container_name` `counter-api`, `counter-web`).
5. [x] Atlas Caddy serves the Counter host (see [deploy/with-atlas-edge.md](../deploy/with-atlas-edge.md)); Atlas `web` on `cca-edge`.
6. [x] `https://counter.customchatandautomation.co.za` loads the demo site; chat returns cited answers.
7. [ ] OpenAI dashboard hard spend cap set for the deploy key (operator check).
8. [ ] Vault session note + January Launch List §2 ticked (after step 6).

**Server verified 2026-10-26:** From `atlas-web-1`, `http://counter-api:8788/api/health` and `http://counter-web/api/health` return OK (3 pages indexed). Caddy block for `counter.customchatandautomation.co.za` is in Atlas `deploy/Caddyfile`.

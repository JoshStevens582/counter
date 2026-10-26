# Counter — Production steps

Checklist for a public Counter demo (Custom Chat and Automation).

1. [ ] Code on GitHub; CI green (backend, frontend, docker).
2. [ ] DNS `counter.customchatandautomation.co.za` → VPS IP (same as Atlas).
3. [ ] `/opt/counter` on the server: clone, `.env` with `OPENAI_API_KEY`, no CORS origins (same-origin via Caddy).
4. [ ] Docker network `cca-edge` created; Counter stack up (`container_name` `counter-api`, `counter-web`).
5. [ ] Atlas Caddy serves the Counter host (see [deploy/with-atlas-edge.md](with-atlas-edge.md)); Atlas `web` container on `cca-edge`.
6. [ ] `https://counter.customchatandautomation.co.za` loads the demo site; chat returns cited answers.
7. [ ] OpenAI dashboard hard spend cap set for the deploy key.
8. [ ] Vault session note + January Launch List §2 ticked.

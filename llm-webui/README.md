# Open WebUI → CSIC / Qwen 3.8 (OpenAI-compatible)

Dockerized [Open WebUI](https://docs.openwebui.com/) wired to the default OpenAI-compatible LLM that OpenCode already uses (David: “Qwen 3.8”).

This package is **separate** from `elabftw-mcp/` so it does not conflict with that PR’s Docker work.

## Connection settings (no secrets in git)

| Setting | Env var | Notes |
| --- | --- | --- |
| Base URL | `OPENAI_API_BASE_URL` | OpenAI-compatible root, usually `…/v1` |
| API key | `OPENAI_API_KEY` | From OpenCode `/connect` — never commit |
| Model id | `OPENAI_API_MODEL` | Exact `id` from `GET {base}/models` (display name ≠ id) |
| UI port | `WEBUI_PORT` | Host port (default `3000`) |

Copy the template and fill from OpenCode:

```bash
cd llm-webui
cp .env.example .env
./scripts/import-opencode-env.sh   # optional helper if OpenCode is on this machine
# edit .env — paste key only into .env
docker compose up -d
```

Open: **http://localhost:3000** (or `http://<host>:$WEBUI_PORT`).

### Where OpenCode keeps the values

| Path | What |
| --- | --- |
| `~/.config/opencode/` (`opencode.json` / config) | `provider.*.options.baseURL`, model ids |
| `~/.local/share/opencode/auth.json` | Legacy `/connect` keys |
| `~/.local/share/opencode/opencode.db` | V2 credentials table |
| Project `opencode.json` | Per-repo provider + default model |

### Public Qwen 3.8 reference (SIU CS AI gateway)

If OpenCode is pointed at SIU’s LiteLLM gateway (documented for **Qwen 3.8 27B** + OpenCode):

- Base URL: `https://api.cs.siu.edu/v1`
- Key: individually assigned SIU AI key (OpenCode `/connect` → provider `siu`)
- Model: **do not guess** — copy `id` from `GET https://api.cs.siu.edu/v1/models`

Guide: https://soc.siu.edu/resources/ai-api-gateway.php

If CSIC IIM uses a different gateway, put that URL/model in `.env` instead; the compose file is gateway-agnostic.

### Smoke-test the upstream (after `.env` has a real key)

```bash
set -a && source .env && set +a
curl -sS -H "Authorization: Bearer $OPENAI_API_KEY" "$OPENAI_API_BASE_URL/models" | head
```

Then chat in Open WebUI; pick the Qwen model from the model list (Admin → Connections if it does not appear).

## What David must provide if import fails

1. `OPENAI_API_BASE_URL` from OpenCode provider `options.baseURL`
2. `OPENAI_API_KEY` (paste into local `.env` only)
3. Exact model `id` string for Qwen 3.8 from `/v1/models`

Network note: some institutional gateways only answer from campus VPN; the WebUI host must be on that network path.

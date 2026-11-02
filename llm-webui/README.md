# Open WebUI → IIIA default LLM (CSIC)

Dockerized [Open WebUI](https://docs.openwebui.com/) wired to the **IIIA** OpenAI-compatible gateway that OpenCode already uses as the default (`iiia` / `iiia/default/llm`).

This package is **separate** from `elabftw-mcp/` so it does not conflict with that PR’s Docker work.

## Defaults (from OpenCode on David’s machine)

| Setting | Value |
| --- | --- |
| Provider id | `iiia` (OpenCode model ref `iiia/default/llm`) |
| Base URL | `https://llm.iiia.es/v1` |
| Model id | `default/llm` — **CSIC-hosted IIIA default** (not a pinned Qwen model string) |
| API key | From OpenCode `/connect` — **never commit** |

Other ids on the same gateway (`Qwen/Qwen3.8-Flash-Next`, `Qwen/Qwen3.8-27B`, …) are optional; this stack defaults to `default/llm`.

## Connection env vars

| Setting | Env var | Notes |
| --- | --- | --- |
| Base URL | `OPENAI_API_BASE_URL` | Default `https://llm.iiia.es/v1` |
| API key | `OPENAI_API_KEY` | OpenCode provider `iiia` — local `.env` only |
| Model id | `OPENAI_API_MODEL` | Default `default/llm` |
| UI port | `WEBUI_PORT` | Host port (default `3000`) |

```bash
cd llm-webui
cp .env.example .env
./scripts/import-opencode-env.sh   # optional if OpenCode is on this machine
# edit .env — paste OPENAI_API_KEY only into .env
docker compose up -d
```

Open: **http://localhost:3000** (or `http://<host>:$WEBUI_PORT`).

### Where OpenCode keeps the values

| Path | What |
| --- | --- |
| `~/.config/opencode/` (`opencode.json` / config) | `provider.iiia.options.baseURL`, default model `iiia/default/llm` |
| `~/.local/share/opencode/auth.json` | Legacy `/connect` keys |
| `~/.local/share/opencode/opencode.db` | V2 credentials table |
| Project `opencode.json` | Per-repo provider + default model |

### Smoke-test the upstream (after `.env` has a real key)

```bash
set -a && source .env && set +a
curl -sS -H "Authorization: Bearer $OPENAI_API_KEY" "$OPENAI_API_BASE_URL/models" | head
```

Then chat in Open WebUI; select **`default/llm`** (Admin → Connections if it does not appear).

## What you still need locally

1. `OPENAI_API_KEY` for provider `iiia` (paste into `.env` only)
2. Network path to `https://llm.iiia.es` from the Docker host

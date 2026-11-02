# elabFTW MCP server

MCP (Model Context Protocol) server that talks to an [elabFTW](https://www.elabftw.net/) instance over the official **REST API v2**, focused on a usable **upload path** for WebUI / agent workflows: create or update experiments/items and attach files.

This package lives under `elabftw-mcp/` in the academic `projeto` repo as a focused scaffold — it does not change the zebrafish analysis content.

**Default for WebUI / containers:** Streamable HTTP on port `8080` (`POST/GET/DELETE /mcp`).  
**Also supported:** stdio (local Cursor, or `docker run -i`).

## Requirements

- Node.js 18+ **or** Docker / Docker Compose
- An elabFTW API key (Settings → API keys)
- Network access from the MCP process to your elabFTW base URL

## Configuration (environment)

| Variable | Required | Description |
| --- | --- | --- |
| `ELABFTW_BASE_URL` | yes | Instance root, e.g. `https://eln.example.org` (trailing slash and `/api/v2` suffix are normalized) |
| `ELABFTW_API_KEY` | yes | API key sent as the `Authorization` header |
| `ELABFTW_VERIFY_TLS` | no | Default `true`. Set `false` only for local self-signed setups |
| `ELABFTW_TIMEOUT_MS` | no | HTTP timeout in ms (default `60000`) |
| `MCP_HOST` | no | HTTP bind address (default `0.0.0.0`) |
| `MCP_PORT` | no | HTTP listen port (default `8080`) |
| `MCP_PATH` | no | MCP endpoint path (default `/mcp`) |
| `MCP_STATELESS` | no | `true` for one-shot transports; default `false` (stateful sessions) |
| `MCP_ALLOWED_HOSTS` | no | Comma-separated Host allow-list when binding `0.0.0.0` |
| `MCP_PUBLISH_PORT` | no | Host port for Compose publish (default `8080`) |

```bash
cd elabftw-mcp
cp .env.example .env
# edit .env — set ELABFTW_BASE_URL and ELABFTW_API_KEY
```

**Do not commit `.env` or secrets.**

## Run with Docker (recommended for WebUI)

Streamable HTTP is the container default so a browser/WebUI or remote MCP client can call `http://localhost:8080/mcp`.

```bash
cd elabftw-mcp
cp .env.example .env   # then fill ELABFTW_* values
docker compose up --build -d
curl -s http://localhost:8080/health
docker compose logs -f elabftw-mcp
```

Stop:

```bash
docker compose down
```

### Point a WebUI / MCP client at the container

Use the Streamable HTTP URL:

```text
http://localhost:8080/mcp
```

(or `http://<host>:${MCP_PUBLISH_PORT}/mcp` if you changed the publish port).

`GET /health` returns a small JSON status (not part of the MCP protocol).

### Stdio via Docker (interactive)

For clients that spawn a stdio MCP process:

```bash
docker build -t elabftw-mcp:local .
docker run --rm -i --env-file .env elabftw-mcp:local node dist/index.js
```

Cursor-style config example:

```json
{
  "mcpServers": {
    "elabftw": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/elabftw-mcp/.env",
        "elabftw-mcp:local",
        "node",
        "dist/index.js"
      ]
    }
  }
}
```

## Run locally (without Docker)

```bash
cd elabftw-mcp
npm install
npm run build
export ELABFTW_BASE_URL=https://eln.example.org
export ELABFTW_API_KEY=your-api-key

# Streamable HTTP (WebUI)
npm run start:http

# or stdio
npm start
```

Development:

```bash
npm run dev:http   # Streamable HTTP via tsx
npm run dev        # stdio via tsx
npm test           # mocked smoke tests (no live instance)
```

### Connect from Cursor (local stdio)

```json
{
  "mcpServers": {
    "elabftw": {
      "command": "node",
      "args": ["/absolute/path/to/projeto/elabftw-mcp/dist/index.js"],
      "env": {
        "ELABFTW_BASE_URL": "https://eln.example.org",
        "ELABFTW_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Tools (upload-oriented)

| Tool | Purpose |
| --- | --- |
| `elabftw_ping` | `GET /info` — credentials / reachability |
| `list_experiments` / `get_experiment` | Read experiments |
| `create_experiment` / `update_experiment` | Create / PATCH experiments |
| `list_item_types` | Categories needed before creating items |
| `list_items` / `get_item` | Read database items |
| `create_item` / `update_item` | Create / PATCH items (`category` required on create) |
| `list_uploads` | List attachments on an experiment or item |
| `upload_file` | Attach a file via `file_path` **or** `content_base64` + `filename` |
| `create_experiment_with_upload` | One-shot: create experiment then upload |

### Typical agent / WebUI upload flow

1. `elabftw_ping` — confirm config.
2. Either:
   - `create_experiment` then `upload_file`, or
   - `create_experiment_with_upload` with base64 content from the UI.
3. For resources: `list_item_types` → `create_item` → `upload_file` with `entity_type: "items"`.

API reference: [elabFTW API v2](https://doc.elabftw.net/api/v2/).

## Design notes

- Secrets only via environment variables / Compose `env_file`.
- Container default transport is **Streamable HTTP** (MCP sessions enabled unless `MCP_STATELESS=true`).
- Uploads use `multipart/form-data` field `file` (optional `comment`), matching the official API.
- `content_base64` supports agents that cannot share a host filesystem with the MCP process.
- Live verification against a real instance needs `ELABFTW_BASE_URL` + `ELABFTW_API_KEY`; CI uses mocks in `tests/`.

## License

MIT

# elabFTW MCP server

MCP (Model Context Protocol) server that talks to an [elabFTW](https://www.elabftw.net/) instance over the official **REST API v2**, focused on a usable **upload path** for WebUI / agent workflows: create or update experiments/items and attach files.

This package lives under `elabftw-mcp/` in the academic `projeto` repo as a focused scaffold — it does not change the zebrafish analysis content.

## Requirements

- Node.js 18+
- An elabFTW API key (Settings → API keys)
- Network access to your elabFTW base URL

## Configuration (environment)

| Variable | Required | Description |
| --- | --- | --- |
| `ELABFTW_BASE_URL` | yes | Instance root, e.g. `https://eln.example.org` (trailing slash and `/api/v2` suffix are normalized) |
| `ELABFTW_API_KEY` | yes | API key sent as the `Authorization` header |
| `ELABFTW_VERIFY_TLS` | no | Default `true`. Set `false` only for local self-signed setups (ops still often use `NODE_TLS_REJECT_UNAUTHORIZED=0` with Node fetch) |
| `ELABFTW_TIMEOUT_MS` | no | HTTP timeout in ms (default `60000`) |

Copy `.env.example` for a template. **Do not commit secrets.**

## Install & run

```bash
cd elabftw-mcp
npm install
npm run build
export ELABFTW_BASE_URL=https://eln.example.org
export ELABFTW_API_KEY=your-api-key
npm start
```

Development (TypeScript via `tsx`):

```bash
npm run dev
```

Smoke tests (mocked HTTP, no live instance):

```bash
npm test
```

## Connect from an MCP client (Cursor example)

Add a stdio server entry that points at the built entrypoint and injects env:

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

Or run without building:

```json
{
  "mcpServers": {
    "elabftw": {
      "command": "npx",
      "args": ["tsx", "/absolute/path/to/projeto/elabftw-mcp/src/index.ts"],
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

- Secrets only via environment variables.
- Uploads use `multipart/form-data` field `file` (optional `comment`), matching the official API.
- `content_base64` supports agents that cannot share a host filesystem with the MCP process.
- Live verification against a real instance needs `ELABFTW_BASE_URL` + `ELABFTW_API_KEY`; CI uses mocks in `tests/`.

## License

MIT

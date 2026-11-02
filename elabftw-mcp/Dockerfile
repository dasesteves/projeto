# Multi-stage build for the elabFTW MCP Streamable HTTP server.
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src
RUN npm run build \
  && npm prune --omit=dev

FROM node:22-bookworm-slim AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080 \
    MCP_PATH=/mcp \
    MCP_STATELESS=false

RUN useradd --create-home --uid 10001 mcp \
  && chown -R mcp:mcp /app

COPY --from=build --chown=mcp:mcp /app/package.json /app/package-lock.json ./
COPY --from=build --chown=mcp:mcp /app/node_modules ./node_modules
COPY --from=build --chown=mcp:mcp /app/dist ./dist

USER mcp
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.MCP_PORT||8080)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

# Default: Streamable HTTP for WebUI / remote MCP clients.
# For stdio: docker run -i --env-file .env elabftw-mcp node dist/index.js
CMD ["node", "dist/http.js"]

#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadConfig } from "./config.js";
import { createElabMcpServer } from "./server.js";

async function main(): Promise<void> {
  const config = loadConfig();
  const { server } = createElabMcpServer(config);

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(
    `elabftw-mcp listening on stdio → ${config.apiBase} (TLS verify=${config.verifyTls})`
  );
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});

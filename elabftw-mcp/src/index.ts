#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadConfig } from "./config.js";
import { ElabFtwClient } from "./elabftw-client.js";
import { registerTools } from "./tools.js";

async function main(): Promise<void> {
  const config = loadConfig();
  const client = new ElabFtwClient(config);

  const server = new McpServer({
    name: "elabftw-mcp",
    version: "0.1.0",
  });

  registerTools(server, client);

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

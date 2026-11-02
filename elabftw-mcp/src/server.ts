import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ElabConfig } from "./config.js";
import { ElabFtwClient } from "./elabftw-client.js";
import { registerTools } from "./tools.js";

export const SERVER_NAME = "elabftw-mcp";
export const SERVER_VERSION = "0.1.0";

export function createElabMcpServer(config: ElabConfig): {
  server: McpServer;
  client: ElabFtwClient;
} {
  const client = new ElabFtwClient(config);
  const server = new McpServer({
    name: SERVER_NAME,
    version: SERVER_VERSION,
  });
  registerTools(server, client);
  return { server, client };
}

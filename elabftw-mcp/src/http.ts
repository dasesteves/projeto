#!/usr/bin/env node
/**
 * Streamable HTTP transport — default for Docker / WebUI clients.
 * Bind 0.0.0.0 and expose /mcp (POST/GET/DELETE) plus GET /health.
 */
import { randomUUID } from "node:crypto";
import type { Request, Response } from "express";
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { loadConfig, loadHttpConfig } from "./config.js";
import { createElabMcpServer, SERVER_NAME, SERVER_VERSION } from "./server.js";

type Session = {
  transport: StreamableHTTPServerTransport;
  serverClose: () => Promise<void>;
};

async function main(): Promise<void> {
  const elabConfig = loadConfig();
  const http = loadHttpConfig();

  const app = createMcpExpressApp({
    host: http.host,
    allowedHosts: http.allowedHosts,
  });

  app.get("/health", (_req, res) => {
    res.json({
      ok: true,
      name: SERVER_NAME,
      version: SERVER_VERSION,
      transport: "streamable-http",
      path: http.path,
      elabApiBase: elabConfig.apiBase,
      stateless: http.stateless,
    });
  });

  if (http.stateless) {
    mountStateless(app, http.path, elabConfig);
  } else {
    mountStateful(app, http.path, elabConfig);
  }

  app.listen(http.port, http.host, () => {
    console.error(
      `${SERVER_NAME} Streamable HTTP on http://${http.host}:${http.port}${http.path} → ${elabConfig.apiBase} (stateless=${http.stateless})`
    );
  });
}

function mountStateless(
  app: ReturnType<typeof createMcpExpressApp>,
  path: string,
  elabConfig: ReturnType<typeof loadConfig>
): void {
  app.post(path, async (req: Request, res: Response) => {
    const { server } = createElabMcpServer(elabConfig);
    try {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
      });
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
      res.on("close", () => {
        void transport.close();
        void server.close();
      });
    } catch (error) {
      console.error("MCP POST error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null,
        });
      }
    }
  });

  app.get(path, (_req, res) => {
    res.status(405).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Method not allowed in stateless mode." },
      id: null,
    });
  });

  app.delete(path, (_req, res) => {
    res.status(405).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Method not allowed in stateless mode." },
      id: null,
    });
  });
}

function mountStateful(
  app: ReturnType<typeof createMcpExpressApp>,
  path: string,
  elabConfig: ReturnType<typeof loadConfig>
): void {
  const sessions = new Map<string, Session>();

  app.post(path, async (req: Request, res: Response) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    try {
      const existing = sessionId ? sessions.get(sessionId) : undefined;
      if (existing) {
        await existing.transport.handleRequest(req, res, req.body);
        return;
      }

      if (!sessionId && isInitializeRequest(req.body)) {
        const { server } = createElabMcpServer(elabConfig);
        const transport = new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (id) => {
            sessions.set(id, {
              transport,
              serverClose: () => server.close(),
            });
          },
        });
        transport.onclose = () => {
          const sid = transport.sessionId;
          if (sid) {
            const session = sessions.get(sid);
            sessions.delete(sid);
            void session?.serverClose();
          }
        };
        await server.connect(transport);
        await transport.handleRequest(req, res, req.body);
        return;
      }

      if (sessionId) {
        res.status(404).json({
          jsonrpc: "2.0",
          error: { code: -32001, message: "Session not found" },
          id: null,
        });
        return;
      }

      res.status(400).json({
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Bad Request: No valid session ID provided",
        },
        id: null,
      });
    } catch (error) {
      console.error("MCP POST error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null,
        });
      }
    }
  });

  app.get(path, async (req: Request, res: Response) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId) {
      res.status(400).send("Missing session ID");
      return;
    }
    const session = sessions.get(sessionId);
    if (!session) {
      res.status(404).send("Session not found");
      return;
    }
    await session.transport.handleRequest(req, res);
  });

  app.delete(path, async (req: Request, res: Response) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId) {
      res.status(400).send("Missing session ID");
      return;
    }
    const session = sessions.get(sessionId);
    if (!session) {
      res.status(404).send("Session not found");
      return;
    }
    await session.transport.handleRequest(req, res);
  });
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});

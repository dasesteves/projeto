export type ElabConfig = {
  baseUrl: string;
  apiBase: string;
  apiKey: string;
  verifyTls: boolean;
  timeoutMs: number;
};

export type HttpConfig = {
  host: string;
  port: number;
  path: string;
  /** When true, use one-shot transports (no MCP session IDs). Default false. */
  stateless: boolean;
  /** Optional Host header allow-list when binding 0.0.0.0 */
  allowedHosts?: string[];
};

function requireEnv(env: NodeJS.ProcessEnv, name: string): string {
  const value = env[name]?.trim();
  if (!value) {
    throw new Error(
      `Missing required environment variable ${name}. See elabftw-mcp/.env.example.`
    );
  }
  return value;
}

function normalizeBaseUrl(raw: string): string {
  let url = raw.trim().replace(/\/+$/, "");
  // Accept either instance root or already-pointing /api/v2
  if (url.endsWith("/api/v2")) {
    url = url.slice(0, -"/api/v2".length);
  }
  return url;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): ElabConfig {
  const baseUrl = normalizeBaseUrl(requireEnv(env, "ELABFTW_BASE_URL"));
  const apiKey = requireEnv(env, "ELABFTW_API_KEY");
  const verifyTls = (env.ELABFTW_VERIFY_TLS ?? "true").toLowerCase() !== "false";
  const timeoutRaw = env.ELABFTW_TIMEOUT_MS;
  const timeoutMs = timeoutRaw ? Number(timeoutRaw) : 60_000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error("ELABFTW_TIMEOUT_MS must be a positive number");
  }

  return {
    baseUrl,
    apiBase: `${baseUrl}/api/v2`,
    apiKey,
    verifyTls,
    timeoutMs,
  };
}

function normalizePath(raw: string): string {
  const trimmed = raw.trim() || "/mcp";
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

export function loadHttpConfig(env: NodeJS.ProcessEnv = process.env): HttpConfig {
  const host = (env.MCP_HOST ?? "0.0.0.0").trim() || "0.0.0.0";
  const portRaw = env.MCP_PORT ?? "8080";
  const port = Number(portRaw);
  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    throw new Error("MCP_PORT must be an integer between 1 and 65535");
  }
  const path = normalizePath(env.MCP_PATH ?? "/mcp");
  const stateless = (env.MCP_STATELESS ?? "false").toLowerCase() === "true";
  const allowed = env.MCP_ALLOWED_HOSTS?.split(",")
    .map((h) => h.trim())
    .filter(Boolean);

  return {
    host,
    port,
    path,
    stateless,
    allowedHosts: allowed?.length ? allowed : undefined,
  };
}

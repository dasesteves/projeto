import { describe, expect, it } from "vitest";
import { loadConfig, loadHttpConfig } from "../src/config.js";

describe("loadConfig", () => {
  it("requires base URL and API key", () => {
    expect(() => loadConfig({})).toThrow(/ELABFTW_BASE_URL/);
    expect(() =>
      loadConfig({ ELABFTW_BASE_URL: "https://eln.example.org" })
    ).toThrow(/ELABFTW_API_KEY/);
  });

  it("normalizes trailing slash and optional /api/v2 suffix", () => {
    const a = loadConfig({
      ELABFTW_BASE_URL: "https://eln.example.org/",
      ELABFTW_API_KEY: "secret",
    });
    expect(a.apiBase).toBe("https://eln.example.org/api/v2");

    const b = loadConfig({
      ELABFTW_BASE_URL: "https://eln.example.org/api/v2",
      ELABFTW_API_KEY: "secret",
    });
    expect(b.apiBase).toBe("https://eln.example.org/api/v2");
  });

  it("parses TLS and timeout options", () => {
    const cfg = loadConfig({
      ELABFTW_BASE_URL: "https://eln.example.org",
      ELABFTW_API_KEY: "secret",
      ELABFTW_VERIFY_TLS: "false",
      ELABFTW_TIMEOUT_MS: "15000",
    });
    expect(cfg.verifyTls).toBe(false);
    expect(cfg.timeoutMs).toBe(15000);
  });
});

describe("loadHttpConfig", () => {
  it("defaults to Docker-friendly Streamable HTTP settings", () => {
    const cfg = loadHttpConfig({});
    expect(cfg).toEqual({
      host: "0.0.0.0",
      port: 8080,
      path: "/mcp",
      stateless: false,
      allowedHosts: undefined,
    });
  });

  it("parses overrides", () => {
    const cfg = loadHttpConfig({
      MCP_HOST: "127.0.0.1",
      MCP_PORT: "3000",
      MCP_PATH: "mcp",
      MCP_STATELESS: "true",
      MCP_ALLOWED_HOSTS: "localhost, app.local",
    });
    expect(cfg.host).toBe("127.0.0.1");
    expect(cfg.port).toBe(3000);
    expect(cfg.path).toBe("/mcp");
    expect(cfg.stateless).toBe(true);
    expect(cfg.allowedHosts).toEqual(["localhost", "app.local"]);
  });
});

import { describe, expect, it } from "vitest";
import { loadConfig } from "../src/config.js";

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

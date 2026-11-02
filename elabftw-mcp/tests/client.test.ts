import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it, vi } from "vitest";
import { loadConfig } from "../src/config.js";
import { ElabApiError, ElabFtwClient } from "../src/elabftw-client.js";

const fixtureDir = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "fixtures"
);

function mockResponse(init: {
  status?: number;
  body?: unknown;
  headers?: Record<string, string>;
  text?: string;
}): Response {
  const status = init.status ?? 200;
  const headers = new Headers(init.headers);
  const text =
    init.text ??
    (init.body === undefined ? "" : JSON.stringify(init.body));
  return new Response(text, { status, headers });
}

describe("ElabFtwClient upload path", () => {
  const config = loadConfig({
    ELABFTW_BASE_URL: "https://eln.example.org",
    ELABFTW_API_KEY: "test-key",
  });

  it("creates an experiment and parses Location id", async () => {
    const fetchMock = vi.fn(async () =>
      mockResponse({
        status: 201,
        headers: {
          location: "https://eln.example.org/api/v2/experiments/321",
        },
      })
    );
    const client = new ElabFtwClient(config, fetchMock as unknown as typeof fetch);
    const result = await client.createExperiment({ title: "MCP upload test" });
    expect(result.id).toBe(321);
    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(String(url)).toBe("https://eln.example.org/api/v2/experiments");
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).headers).toBeInstanceOf(Headers);
    const headers = (init as RequestInit).headers as Headers;
    expect(headers.get("Authorization")).toBe("test-key");
  });

  it("uploads from a local file path as multipart", async () => {
    await mkdir(fixtureDir, { recursive: true });
    const filePath = path.join(fixtureDir, "sample.txt");
    await writeFile(filePath, "hello elabftw", "utf8");

    const fetchMock = vi.fn(async (_url: RequestInfo | URL, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(init?.body).toBeInstanceOf(FormData);
      const form = init!.body as FormData;
      const file = form.get("file");
      expect(file).toBeInstanceOf(Blob);
      expect(form.get("comment")).toBe("fixture upload");
      return mockResponse({
        status: 201,
        headers: {
          location: "https://eln.example.org/api/v2/experiments/321/uploads/9",
        },
      });
    });

    const client = new ElabFtwClient(config, fetchMock as unknown as typeof fetch);
    const result = await client.uploadFile("experiments", 321, {
      kind: "path",
      filePath,
      comment: "fixture upload",
    });
    expect(result.id).toBe(9);
    expect(String(fetchMock.mock.calls[0]![0])).toBe(
      "https://eln.example.org/api/v2/experiments/321/uploads"
    );
  });

  it("uploads from base64 content for WebUI/agent flows", async () => {
    const content = Buffer.from("webui payload").toString("base64");
    const fetchMock = vi.fn(async (_url: RequestInfo | URL, init?: RequestInit) => {
      const form = init!.body as FormData;
      const file = form.get("file") as Blob;
      const bytes = Buffer.from(await file.arrayBuffer());
      expect(bytes.toString("utf8")).toBe("webui payload");
      return mockResponse({
        status: 201,
        headers: {
          location: "https://eln.example.org/api/v2/items/44/uploads/12",
        },
      });
    });

    const client = new ElabFtwClient(config, fetchMock as unknown as typeof fetch);
    const result = await client.uploadFile("items", 44, {
      kind: "base64",
      filename: "note.txt",
      contentBase64: content,
      mimeType: "text/plain",
    });
    expect(result.id).toBe(12);
  });

  it("surfaces API errors with status and body", async () => {
    const fetchMock = vi.fn(async () =>
      mockResponse({ status: 401, text: "Unauthorized" })
    );
    const client = new ElabFtwClient(config, fetchMock as unknown as typeof fetch);
    await expect(client.getInfo()).rejects.toBeInstanceOf(ElabApiError);
  });

  it("runs create → upload sequence used by create_experiment_with_upload", async () => {
    await mkdir(fixtureDir, { recursive: true });
    const filePath = path.join(fixtureDir, "one-shot.bin");
    await writeFile(filePath, Buffer.from([1, 2, 3, 4]));

    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        mockResponse({
          status: 201,
          headers: {
            location: "https://eln.example.org/api/v2/experiments/100",
          },
        })
      )
      .mockResolvedValueOnce(
        mockResponse({
          status: 201,
          headers: {
            location:
              "https://eln.example.org/api/v2/experiments/100/uploads/1",
          },
        })
      );

    const client = new ElabFtwClient(config, fetchMock as unknown as typeof fetch);
    const created = await client.createExperiment({ title: "one-shot" });
    expect(created.id).toBe(100);
    const upload = await client.uploadFile("experiments", created.id!, {
      kind: "path",
      filePath,
    });
    expect(upload.id).toBe(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    // fixture still readable after upload
    expect((await readFile(filePath)).length).toBe(4);
  });
});

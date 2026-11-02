import { readFile } from "node:fs/promises";
import path from "node:path";
import type { ElabConfig } from "./config.js";

export type EntityType = "experiments" | "items";

export type ElabEntityWritable = {
  title?: string;
  body?: string;
  category?: number;
  status?: number;
  template?: number;
  tags?: string[];
  content_type?: 1 | 2;
  metadata?: unknown;
  [key: string]: unknown;
};

export type UploadSource =
  | { kind: "path"; filePath: string; comment?: string }
  | {
      kind: "base64";
      filename: string;
      contentBase64: string;
      comment?: string;
      mimeType?: string;
    };

export class ElabApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly body: string
  ) {
    super(message);
    this.name = "ElabApiError";
  }
}

export type FetchLike = typeof fetch;

function idFromLocation(location: string | null): number | null {
  if (!location) return null;
  const parts = location.split("/").filter(Boolean);
  const last = parts[parts.length - 1];
  const id = Number(last);
  return Number.isInteger(id) ? id : null;
}

export class ElabFtwClient {
  constructor(
    private readonly config: ElabConfig,
    private readonly fetchImpl: FetchLike = fetch
  ) {}

  private headers(extra?: HeadersInit): Headers {
    const headers = new Headers(extra);
    headers.set("Authorization", this.config.apiKey);
    headers.set("Accept", "application/json");
    return headers;
  }

  private async request(
    method: string,
    apiPath: string,
    init?: {
      body?: BodyInit | null;
      headers?: HeadersInit;
      query?: Record<string, string | number | boolean | undefined>;
    }
  ): Promise<{ status: number; headers: Headers; text: string; json: unknown }> {
    const url = new URL(
      apiPath.startsWith("http")
        ? apiPath
        : `${this.config.apiBase}${apiPath.startsWith("/") ? apiPath : `/${apiPath}`}`
    );
    if (init?.query) {
      for (const [k, v] of Object.entries(init.query)) {
        if (v !== undefined && v !== null && v !== "") {
          url.searchParams.set(k, String(v));
        }
      }
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.config.timeoutMs);
    try {
      const response = await this.fetchImpl(url, {
        method,
        headers: this.headers(init?.headers),
        body: init?.body,
        signal: controller.signal,
        // Node fetch respects this via undici dispatcher; kept for documentation.
        // Callers with self-signed certs can set NODE_TLS_REJECT_UNAUTHORIZED=0
        // or use a custom fetchImpl. verifyTls is surfaced in config for ops.
      });
      const text = await response.text();
      let json: unknown = null;
      if (text) {
        try {
          json = JSON.parse(text);
        } catch {
          json = null;
        }
      }
      if (!response.ok) {
        throw new ElabApiError(
          `elabFTW ${method} ${url.pathname} failed (${response.status})`,
          response.status,
          text.slice(0, 2000)
        );
      }
      return { status: response.status, headers: response.headers, text, json };
    } finally {
      clearTimeout(timer);
    }
  }

  async getInfo(): Promise<unknown> {
    const { json } = await this.request("GET", "/info");
    return json;
  }

  async listExperiments(query?: {
    limit?: number;
    offset?: number;
    q?: string;
  }): Promise<unknown> {
    const { json } = await this.request("GET", "/experiments", { query });
    return json;
  }

  async getExperiment(id: number): Promise<unknown> {
    const { json } = await this.request("GET", `/experiments/${id}`);
    return json;
  }

  async createExperiment(payload: ElabEntityWritable = {}): Promise<{
    id: number | null;
    location: string | null;
    body: unknown;
  }> {
    const { headers, json, status } = await this.request("POST", "/experiments", {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const location = headers.get("location");
    return { id: idFromLocation(location), location, body: json ?? { status } };
  }

  async updateExperiment(
    id: number,
    payload: ElabEntityWritable
  ): Promise<unknown> {
    const { json } = await this.request("PATCH", `/experiments/${id}`, {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return json;
  }

  async listItems(query?: {
    limit?: number;
    offset?: number;
    q?: string;
  }): Promise<unknown> {
    const { json } = await this.request("GET", "/items", { query });
    return json;
  }

  async getItem(id: number): Promise<unknown> {
    const { json } = await this.request("GET", `/items/${id}`);
    return json;
  }

  async createItem(payload: ElabEntityWritable): Promise<{
    id: number | null;
    location: string | null;
    body: unknown;
  }> {
    const { headers, json, status } = await this.request("POST", "/items", {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const location = headers.get("location");
    return { id: idFromLocation(location), location, body: json ?? { status } };
  }

  async updateItem(id: number, payload: ElabEntityWritable): Promise<unknown> {
    const { json } = await this.request("PATCH", `/items/${id}`, {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return json;
  }

  async listItemTypes(): Promise<unknown> {
    const { json } = await this.request("GET", "/items_types");
    return json;
  }

  async listUploads(entityType: EntityType, id: number): Promise<unknown> {
    const { json } = await this.request(
      "GET",
      `/${entityType}/${id}/uploads`
    );
    return json;
  }

  async uploadFile(
    entityType: EntityType,
    id: number,
    source: UploadSource
  ): Promise<{ id: number | null; location: string | null }> {
    const form = new FormData();
    let comment: string | undefined;

    if (source.kind === "path") {
      comment = source.comment;
      const absolute = path.resolve(source.filePath);
      const bytes = await readFile(absolute);
      const blob = new Blob([bytes]);
      form.append("file", blob, path.basename(absolute));
    } else {
      comment = source.comment;
      const bytes = Buffer.from(source.contentBase64, "base64");
      const blob = new Blob([bytes], {
        type: source.mimeType ?? "application/octet-stream",
      });
      form.append("file", blob, source.filename);
    }

    if (comment) {
      form.append("comment", comment);
    }

    const { headers } = await this.request(
      "POST",
      `/${entityType}/${id}/uploads`,
      { body: form }
    );
    const location = headers.get("location");
    return { id: idFromLocation(location), location };
  }
}

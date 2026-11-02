import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { ElabFtwClient, EntityType } from "./elabftw-client.js";
import { ElabApiError } from "./elabftw-client.js";

function jsonResult(data: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: typeof data === "string" ? data : JSON.stringify(data, null, 2),
      },
    ],
  };
}

function errorResult(err: unknown) {
  if (err instanceof ElabApiError) {
    return {
      isError: true as const,
      content: [
        {
          type: "text" as const,
          text: `${err.message}\n${err.body}`,
        },
      ],
    };
  }
  const message = err instanceof Error ? err.message : String(err);
  return {
    isError: true as const,
    content: [{ type: "text" as const, text: message }],
  };
}

const entityTypeSchema = z.enum(["experiments", "items"]);

const writableFields = {
  title: z.string().optional().describe("Entry title"),
  body: z
    .string()
    .optional()
    .describe("Main text (HTML or Markdown depending on content_type)"),
  category: z
    .number()
    .int()
    .optional()
    .describe("Category / item type ID (required for many item creates)"),
  status: z.number().int().optional().describe("Status ID"),
  template: z
    .number()
    .int()
    .optional()
    .describe("Template ID for experiments (-1 empty, 0 team default)"),
  content_type: z
    .union([z.literal(1), z.literal(2)])
    .optional()
    .describe("1 = HTML (default), 2 = Markdown"),
  tags: z.array(z.string()).optional().describe("Tags to set on the entry"),
};

export function registerTools(server: McpServer, client: ElabFtwClient): void {
  server.registerTool(
    "elabftw_ping",
    {
      title: "Ping elabFTW",
      description:
        "Check connectivity and credentials against the configured elabFTW instance (GET /api/v2/info).",
      inputSchema: {},
    },
    async () => {
      try {
        const info = await client.getInfo();
        return jsonResult({ ok: true, info });
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "list_experiments",
    {
      title: "List experiments",
      description: "List experiments accessible to the API key.",
      inputSchema: {
        limit: z.number().int().positive().max(100).optional(),
        offset: z.number().int().nonnegative().optional(),
        q: z.string().optional().describe("Optional search query"),
      },
    },
    async (args) => {
      try {
        return jsonResult(await client.listExperiments(args));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "get_experiment",
    {
      title: "Get experiment",
      description: "Read a single experiment by ID.",
      inputSchema: {
        id: z.number().int().positive().describe("Experiment ID"),
      },
    },
    async ({ id }) => {
      try {
        return jsonResult(await client.getExperiment(id));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "create_experiment",
    {
      title: "Create experiment",
      description:
        "Create an experiment. Returns the new ID from the Location header when available.",
      inputSchema: { ...writableFields },
    },
    async (args) => {
      try {
        return jsonResult(await client.createExperiment(args));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "update_experiment",
    {
      title: "Update experiment",
      description: "PATCH an existing experiment.",
      inputSchema: {
        id: z.number().int().positive(),
        ...writableFields,
      },
    },
    async ({ id, ...payload }) => {
      try {
        return jsonResult(await client.updateExperiment(id, payload));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "list_item_types",
    {
      title: "List item types",
      description:
        "List resource/item types (categories). Needed before create_item when a category ID is required.",
      inputSchema: {},
    },
    async () => {
      try {
        return jsonResult(await client.listItemTypes());
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "list_items",
    {
      title: "List items",
      description: "List database items (resources) accessible to the API key.",
      inputSchema: {
        limit: z.number().int().positive().max(100).optional(),
        offset: z.number().int().nonnegative().optional(),
        q: z.string().optional(),
      },
    },
    async (args) => {
      try {
        return jsonResult(await client.listItems(args));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "get_item",
    {
      title: "Get item",
      description: "Read a single database item by ID.",
      inputSchema: {
        id: z.number().int().positive(),
      },
    },
    async ({ id }) => {
      try {
        return jsonResult(await client.getItem(id));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "create_item",
    {
      title: "Create item",
      description:
        "Create a database item/resource. Pass category (item type ID) from list_item_types when required by the instance.",
      inputSchema: {
        ...writableFields,
        category: z
          .number()
          .int()
          .positive()
          .describe("Item type / category ID (from list_item_types)"),
      },
    },
    async (args) => {
      try {
        return jsonResult(await client.createItem(args));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "update_item",
    {
      title: "Update item",
      description: "PATCH an existing database item.",
      inputSchema: {
        id: z.number().int().positive(),
        ...writableFields,
      },
    },
    async ({ id, ...payload }) => {
      try {
        return jsonResult(await client.updateItem(id, payload));
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "list_uploads",
    {
      title: "List uploads",
      description: "List attachments on an experiment or item.",
      inputSchema: {
        entity_type: entityTypeSchema.describe(
          "Target entity: experiments or items"
        ),
        id: z.number().int().positive().describe("Entity ID"),
      },
    },
    async ({ entity_type, id }) => {
      try {
        return jsonResult(
          await client.listUploads(entity_type as EntityType, id)
        );
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "upload_file",
    {
      title: "Upload file attachment",
      description:
        "Upload a file to an experiment or item. Provide either file_path (local path visible to the MCP process) or content_base64 + filename (for WebUI/agent payloads).",
      inputSchema: {
        entity_type: entityTypeSchema,
        id: z.number().int().positive().describe("Experiment or item ID"),
        file_path: z
          .string()
          .optional()
          .describe("Absolute or relative path on the MCP host"),
        content_base64: z
          .string()
          .optional()
          .describe("Base64-encoded file bytes (alternative to file_path)"),
        filename: z
          .string()
          .optional()
          .describe("Required when using content_base64"),
        mime_type: z.string().optional().describe("Optional MIME type"),
        comment: z.string().optional().describe("Optional upload comment"),
      },
    },
    async (args) => {
      try {
        const hasPath = Boolean(args.file_path);
        const hasB64 = Boolean(args.content_base64);
        if (hasPath === hasB64) {
          return errorResult(
            new Error(
              "Provide exactly one of file_path or content_base64 (+ filename)."
            )
          );
        }
        if (hasB64 && !args.filename) {
          return errorResult(
            new Error("filename is required when using content_base64.")
          );
        }

        const result = args.file_path
          ? await client.uploadFile(args.entity_type, args.id, {
              kind: "path",
              filePath: args.file_path,
              comment: args.comment,
            })
          : await client.uploadFile(args.entity_type, args.id, {
              kind: "base64",
              filename: args.filename!,
              contentBase64: args.content_base64!,
              comment: args.comment,
              mimeType: args.mime_type,
            });

        return jsonResult({
          ok: true,
          entity_type: args.entity_type,
          entity_id: args.id,
          upload_id: result.id,
          location: result.location,
        });
      } catch (err) {
        return errorResult(err);
      }
    }
  );

  server.registerTool(
    "create_experiment_with_upload",
    {
      title: "Create experiment and upload",
      description:
        "Convenience upload path: create an experiment, then attach one file (path or base64). Useful for WebUI/agent one-shot uploads.",
      inputSchema: {
        title: z.string().optional(),
        body: z.string().optional(),
        template: z.number().int().optional(),
        content_type: z.union([z.literal(1), z.literal(2)]).optional(),
        tags: z.array(z.string()).optional(),
        file_path: z.string().optional(),
        content_base64: z.string().optional(),
        filename: z.string().optional(),
        mime_type: z.string().optional(),
        comment: z.string().optional(),
      },
    },
    async (args) => {
      try {
        const hasPath = Boolean(args.file_path);
        const hasB64 = Boolean(args.content_base64);
        if (hasPath === hasB64) {
          return errorResult(
            new Error(
              "Provide exactly one of file_path or content_base64 (+ filename)."
            )
          );
        }
        if (hasB64 && !args.filename) {
          return errorResult(
            new Error("filename is required when using content_base64.")
          );
        }

        const created = await client.createExperiment({
          title: args.title,
          body: args.body,
          template: args.template,
          content_type: args.content_type,
          tags: args.tags,
        });

        if (created.id == null) {
          return errorResult(
            new Error(
              `Experiment created but Location header missing ID: ${created.location}`
            )
          );
        }

        const upload = args.file_path
          ? await client.uploadFile("experiments", created.id, {
              kind: "path",
              filePath: args.file_path,
              comment: args.comment,
            })
          : await client.uploadFile("experiments", created.id, {
              kind: "base64",
              filename: args.filename!,
              contentBase64: args.content_base64!,
              comment: args.comment,
              mimeType: args.mime_type,
            });

        return jsonResult({
          ok: true,
          experiment_id: created.id,
          experiment_location: created.location,
          upload_id: upload.id,
          upload_location: upload.location,
        });
      } catch (err) {
        return errorResult(err);
      }
    }
  );
}

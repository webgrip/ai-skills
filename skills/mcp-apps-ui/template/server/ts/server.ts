import { randomUUID } from "node:crypto";
import { McpServer, fromJsonSchema, type CallToolResult } from "@modelcontextprotocol/server";
import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";
import statusSchema from "../../contract/service-status.schema.json" with { type: "json" };
import {
  CONFIRM_TOKEN_META_KEY,
  STATUS_RESOURCE_URI,
  TOOL_NAMES,
  describeStatus,
  type RestartPreview,
  type RestartReceipt,
  type ServiceStatus,
} from "../../src/contract.ts";

export interface ServerOptions {
  loadAppHtml: () => Promise<string>;
  inventory: ReadonlyMap<string, ServiceStatus>;
  principal: () => string;
  mayRestart: (principal: string, serviceId: string) => boolean;
  now?: () => Date;
  confirmWindowMs?: number;
}

interface PendingConfirmation {
  principal: string;
  serviceId: string;
  expiresAt: number;
}

const serviceIdInput = z.string().regex(/^[a-z0-9][a-z0-9-]{0,62}$/).describe("Service id, for example checkout-api");

function failure(text: string): CallToolResult {
  return { isError: true, content: [{ type: "text", text }] };
}

export function createServer(options: ServerOptions): McpServer {
  const now = options.now ?? (() => new Date());
  const confirmWindowMs = options.confirmWindowMs ?? 120_000;
  const pending = new Map<string, PendingConfirmation>();
  const receipts = new Map<string, RestartReceipt>();
  const server = new McpServer({ name: "service-status", version: "1.0.0" });

  const statusFor = (serviceId: string): ServiceStatus | undefined => {
    const status = options.inventory.get(serviceId);
    if (!status) return undefined;
    const allowed = options.mayRestart(options.principal(), serviceId);
    return { ...status, actions: { restart: { allowed } } };
  };

  registerAppTool(
    server,
    TOOL_NAMES.show,
    {
      title: "Show service status",
      description:
        "Shows the current health, release and replica count of one service as a status card. Use it when the user asks how a service is doing. Read-only; restarting happens from the card after the user confirms.",
      inputSchema: z.object({ serviceId: serviceIdInput }),
      outputSchema: fromJsonSchema<ServiceStatus>(statusSchema as Parameters<typeof fromJsonSchema>[0]),
      annotations: { title: "Show service status", readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true },
      _meta: { ui: { resourceUri: STATUS_RESOURCE_URI, visibility: ["model", "app"] } },
    },
    async ({ serviceId }): Promise<CallToolResult> => {
      const status = statusFor(serviceId);
      if (!status) return failure(`Service ${serviceId} not found. Ask the user for the exact service id.`);
      return {
        content: [{ type: "text", text: describeStatus(status) }],
        structuredContent: { ...status },
      };
    },
  );

  registerAppTool(
    server,
    TOOL_NAMES.prepareRestart,
    {
      title: "Prepare a service restart",
      description: "Step one of a restart from the status card: checks permission and returns what will happen plus a short-lived confirmation.",
      inputSchema: z.object({ serviceId: serviceIdInput }),
      annotations: { title: "Prepare a service restart", readOnlyHint: true, destructiveHint: false, openWorldHint: false },
      _meta: { ui: { resourceUri: STATUS_RESOURCE_URI, visibility: ["app"] } },
    },
    async ({ serviceId }): Promise<CallToolResult> => {
      const principal = options.principal();
      const status = options.inventory.get(serviceId);
      if (!status) return failure(`Service ${serviceId} not found.`);
      if (!options.mayRestart(principal, serviceId)) return failure(`You are not allowed to restart ${status.service.name}.`);
      const token = randomUUID();
      const expiresAt = now().getTime() + confirmWindowMs;
      pending.set(token, { principal, serviceId, expiresAt });
      const preview: RestartPreview = {
        serviceId,
        summary: `Restart all ${status.replicas.desired} replicas of ${status.service.name} (${status.release}) one at a time.`,
        expiresAt: new Date(expiresAt).toISOString(),
      };
      return {
        content: [{ type: "text", text: preview.summary }],
        structuredContent: { ...preview },
        _meta: { [CONFIRM_TOKEN_META_KEY]: token },
      };
    },
  );

  registerAppTool(
    server,
    TOOL_NAMES.confirmRestart,
    {
      title: "Confirm a service restart",
      description: "Step two of a restart from the status card. Requires the confirmation from step one and an idempotency key; repeating a key returns the first receipt.",
      inputSchema: z.object({
        serviceId: serviceIdInput,
        confirmToken: z.string().uuid(),
        idempotencyKey: z.string().min(8).max(64),
      }),
      annotations: { title: "Confirm a service restart", readOnlyHint: false, destructiveHint: true, openWorldHint: false, idempotentHint: true },
      _meta: { ui: { resourceUri: STATUS_RESOURCE_URI, visibility: ["app"] } },
    },
    async ({ serviceId, confirmToken, idempotencyKey }): Promise<CallToolResult> => {
      const principal = options.principal();
      const earlier = receipts.get(`${principal}:${idempotencyKey}`);
      if (earlier) {
        const duplicate: RestartReceipt = { ...earlier, outcome: "duplicate" };
        return { content: [{ type: "text", text: `Restart ${earlier.operationId} was already accepted.` }], structuredContent: { ...duplicate } };
      }
      const confirmation = pending.get(confirmToken);
      pending.delete(confirmToken);
      if (!confirmation || confirmation.principal !== principal || confirmation.serviceId !== serviceId) {
        return failure("This confirmation is not valid. Start the restart again from the status card.");
      }
      if (confirmation.expiresAt < now().getTime()) return failure("This confirmation expired. Start the restart again from the status card.");
      if (!options.mayRestart(principal, serviceId)) return failure("You are no longer allowed to restart this service.");
      const receipt: RestartReceipt = { serviceId, operationId: randomUUID(), outcome: "accepted" };
      receipts.set(`${principal}:${idempotencyKey}`, receipt);
      console.error(JSON.stringify({ audit: "service.restart", principal, serviceId, operationId: receipt.operationId, at: now().toISOString() }));
      return { content: [{ type: "text", text: `Restart ${receipt.operationId} accepted for ${serviceId}.` }], structuredContent: { ...receipt } };
    },
  );

  registerAppResource(
    server,
    "Service status card",
    STATUS_RESOURCE_URI,
    { mimeType: RESOURCE_MIME_TYPE, description: "Interactive status card for one service" },
    async () => ({
      contents: [
        {
          uri: STATUS_RESOURCE_URI,
          mimeType: RESOURCE_MIME_TYPE,
          text: await options.loadAppHtml(),
          _meta: { ui: { prefersBorder: true } },
        },
      ],
    }),
  );

  return server;
}

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { expect, test } from "@playwright/test";
import { CONFIRM_TOKEN_META_KEY, STATUS_RESOURCE_URI, TOOL_NAMES } from "../src/contract.ts";
import { validateServiceStatus } from "./contract.ts";

const UI_CAPABILITIES = { extensions: { "io.modelcontextprotocol/ui": { mimeTypes: ["text/html;profile=mcp-app"] } } };

function startStdlibServer() {
  const child = spawn("python3", ["-I", "server/python/stdlib_server.py"], { stdio: ["pipe", "pipe", "inherit"] });
  const replies = new Map<number, (value: Record<string, any>) => void>();
  createInterface({ input: child.stdout }).on("line", (line) => {
    const message = JSON.parse(line);
    replies.get(message.id)?.(message);
  });
  let nextId = 1;
  const request = (method: string, params: object = {}) =>
    new Promise<Record<string, any>>((resolve) => {
      const id = nextId++;
      replies.set(id, resolve);
      child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
    });
  return { request, stop: () => child.kill() };
}

test("the stdlib Python server honours the same contract", async () => {
  const server = startStdlibServer();
  try {
    await server.request("initialize", { protocolVersion: "2025-11-25", capabilities: UI_CAPABILITIES, clientInfo: { name: "contract-test", version: "1.0.0" } });
    const { result: list } = await server.request("tools/list");
    const byName = Object.fromEntries(list.tools.map((tool: { name: string }) => [tool.name, tool]));
    expect(byName[TOOL_NAMES.show]._meta.ui).toEqual({ resourceUri: STATUS_RESOURCE_URI, visibility: ["model", "app"] });
    expect(byName[TOOL_NAMES.confirmRestart]._meta.ui.visibility).toEqual(["app"]);

    const { result: resource } = await server.request("resources/read", { uri: STATUS_RESOURCE_URI });
    expect(resource.contents[0].mimeType).toBe("text/html;profile=mcp-app");

    const { result: shown } = await server.request("tools/call", { name: TOOL_NAMES.show, arguments: { serviceId: "checkout-api" } });
    expect(validateServiceStatus(shown.structuredContent), JSON.stringify(validateServiceStatus.errors)).toBe(true);
    expect(shown.content[0].text).toContain("Checkout API is healthy");

    const { result: prepared } = await server.request("tools/call", { name: TOOL_NAMES.prepareRestart, arguments: { serviceId: "checkout-api" } });
    const confirmToken = prepared._meta[CONFIRM_TOKEN_META_KEY];
    const args = { serviceId: "checkout-api", confirmToken, idempotencyKey: "key-00000001" };
    const { result: first } = await server.request("tools/call", { name: TOOL_NAMES.confirmRestart, arguments: args });
    const { result: replay } = await server.request("tools/call", { name: TOOL_NAMES.confirmRestart, arguments: args });
    expect(first.structuredContent.outcome).toBe("accepted");
    expect(replay.structuredContent).toMatchObject({ outcome: "duplicate", operationId: first.structuredContent.operationId });
  } finally {
    server.stop();
  }
});

test("the stdlib Python server tells a text-only client what it cannot do", async () => {
  const server = startStdlibServer();
  try {
    await server.request("initialize", { protocolVersion: "2025-11-25", capabilities: {}, clientInfo: { name: "text-client", version: "1.0.0" } });
    const { result } = await server.request("tools/call", { name: TOOL_NAMES.show, arguments: { serviceId: "checkout-api" } });
    expect(result.content[0].text).toContain("this client shows text only");
  } finally {
    server.stop();
  }
});

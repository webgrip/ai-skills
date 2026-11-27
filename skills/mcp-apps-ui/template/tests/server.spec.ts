import { expect, test } from "@playwright/test";
import { Client, InMemoryTransport } from "@modelcontextprotocol/client";
import healthy from "../contract/fixtures/healthy.json" with { type: "json" };
import { createServer, type ServerOptions } from "../server/ts/server.ts";
import { CONFIRM_TOKEN_META_KEY, STATUS_RESOURCE_URI, TOOL_NAMES, describeStatus, type ServiceStatus } from "../src/contract.ts";
import { compileSchema, validateServiceStatus } from "./contract.ts";

const APP_MIME = "text/html;profile=mcp-app";

async function connect(overrides: Partial<ServerOptions> = {}) {
  let principal = "operator";
  let clock = new Date("2026-11-20T10:15:00Z");
  const server = createServer({
    loadAppHtml: async () => "<!doctype html><title>card</title>",
    inventory: new Map([[healthy.service.id, healthy as ServiceStatus]]),
    principal: () => principal,
    mayRestart: (who) => who === "operator",
    now: () => clock,
    ...overrides,
  });
  const [clientSide, serverSide] = InMemoryTransport.createLinkedPair();
  await server.connect(serverSide);
  const client = new Client({ name: "contract-test", version: "1.0.0" });
  await client.connect(clientSide);
  return {
    client,
    actAs: (who: string) => (principal = who),
    advance: (ms: number) => (clock = new Date(clock.getTime() + ms)),
  };
}

test("the model-facing tool links its UI resource and stays read-only", async () => {
  const { client } = await connect();
  const { tools } = await client.listTools();
  const show = tools.find((tool) => tool.name === TOOL_NAMES.show);
  expect(show?._meta?.ui).toMatchObject({ resourceUri: STATUS_RESOURCE_URI, visibility: ["model", "app"] });
  expect(show?.annotations).toMatchObject({ readOnlyHint: true, destructiveHint: false, openWorldHint: false });
  expect(compileSchema(show!.outputSchema!)(healthy)).toBe(true);
});

test("action tools are app-only and the write is marked destructive", async () => {
  const { client } = await connect();
  const { tools } = await client.listTools();
  for (const name of [TOOL_NAMES.prepareRestart, TOOL_NAMES.confirmRestart]) {
    expect(tools.find((tool) => tool.name === name)?._meta?.ui).toMatchObject({ visibility: ["app"] });
  }
  expect(tools.find((tool) => tool.name === TOOL_NAMES.confirmRestart)?.annotations?.destructiveHint).toBe(true);
});

test("the UI resource is served with the MCP App MIME type", async () => {
  const { client } = await connect();
  const { contents } = await client.readResource({ uri: STATUS_RESOURCE_URI });
  expect(contents[0]).toMatchObject({ uri: STATUS_RESOURCE_URI, mimeType: APP_MIME });
  expect("text" in contents[0] && contents[0].text).toContain("<!doctype html>");
});

test("the result carries a text fallback and contract-valid structured content", async () => {
  const { client } = await connect();
  const result = await client.callTool({ name: TOOL_NAMES.show, arguments: { serviceId: "checkout-api" } });
  expect(result.content).toEqual([{ type: "text", text: describeStatus(healthy as ServiceStatus) }]);
  expect(validateServiceStatus(result.structuredContent), JSON.stringify(validateServiceStatus.errors)).toBe(true);
});

test("the restart permission reflects the caller, not the fixture", async () => {
  const { client, actAs } = await connect();
  actAs("visitor");
  const result = await client.callTool({ name: TOOL_NAMES.show, arguments: { serviceId: "checkout-api" } });
  expect((result.structuredContent as ServiceStatus).actions.restart.allowed).toBe(false);
});

test("a restart needs a fresh confirmation and replays by idempotency key", async () => {
  const { client } = await connect();
  const prepared = await client.callTool({ name: TOOL_NAMES.prepareRestart, arguments: { serviceId: "checkout-api" } });
  const token = prepared._meta?.[CONFIRM_TOKEN_META_KEY];
  expect(typeof token).toBe("string");
  expect(JSON.stringify(prepared.structuredContent)).not.toContain(String(token));
  const args = { serviceId: "checkout-api", confirmToken: token, idempotencyKey: "key-00000001" };
  const first = await client.callTool({ name: TOOL_NAMES.confirmRestart, arguments: args });
  const replay = await client.callTool({ name: TOOL_NAMES.confirmRestart, arguments: args });
  expect(first.structuredContent).toMatchObject({ outcome: "accepted" });
  expect(replay.structuredContent).toMatchObject({ outcome: "duplicate", operationId: (first.structuredContent as { operationId: string }).operationId });
  const reused = await client.callTool({ name: TOOL_NAMES.confirmRestart, arguments: { ...args, idempotencyKey: "key-00000002" } });
  expect(reused.isError).toBe(true);
});

test("the server refuses writes the caller may not make, whatever the UI showed", async () => {
  const { client, actAs } = await connect();
  const prepared = await client.callTool({ name: TOOL_NAMES.prepareRestart, arguments: { serviceId: "checkout-api" } });
  actAs("visitor");
  const confirmed = await client.callTool({
    name: TOOL_NAMES.confirmRestart,
    arguments: { serviceId: "checkout-api", confirmToken: prepared._meta?.[CONFIRM_TOKEN_META_KEY], idempotencyKey: "key-00000003" },
  });
  expect(confirmed.isError).toBe(true);
  const denied = await client.callTool({ name: TOOL_NAMES.prepareRestart, arguments: { serviceId: "checkout-api" } });
  expect(denied.isError).toBe(true);
});

test("an expired confirmation is refused", async () => {
  const { client, advance } = await connect();
  const prepared = await client.callTool({ name: TOOL_NAMES.prepareRestart, arguments: { serviceId: "checkout-api" } });
  advance(10 * 60_000);
  const confirmed = await client.callTool({
    name: TOOL_NAMES.confirmRestart,
    arguments: { serviceId: "checkout-api", confirmToken: prepared._meta?.[CONFIRM_TOKEN_META_KEY], idempotencyKey: "key-00000004" },
  });
  expect(confirmed.isError).toBe(true);
});

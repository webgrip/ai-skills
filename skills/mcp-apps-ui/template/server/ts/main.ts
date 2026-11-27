import { readFile } from "node:fs/promises";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import healthy from "../../contract/fixtures/healthy.json" with { type: "json" };
import degraded from "../../contract/fixtures/degraded.json" with { type: "json" };
import type { ServiceStatus } from "../../src/contract.ts";
import { createServer } from "./server.ts";

const appHtmlPath = new URL("../../dist/app/app.html", import.meta.url);
const inventory = new Map(
  [healthy, degraded].map((status) => [status.service.id, status as ServiceStatus]),
);
const restartersByService = new Map([["checkout-api", new Set(["local-operator"])]]);

const server = createServer({
  loadAppHtml: () => readFile(appHtmlPath, "utf8"),
  inventory,
  principal: () => process.env.MCP_PRINCIPAL ?? "local-operator",
  mayRestart: (principal, serviceId) => restartersByService.get(serviceId)?.has(principal) ?? false,
});

await server.connect(new StdioServerTransport());

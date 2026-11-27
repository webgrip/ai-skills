import { AppBridge, PostMessageTransport, type McpUiHostCapabilities, type McpUiHostContext, type McpUiStyles } from "@modelcontextprotocol/ext-apps/app-bridge";
import type { CallToolResult } from "@modelcontextprotocol/client";
import appHtml from "../dist/app/app.html?raw";
import healthy from "../contract/fixtures/healthy.json";
import degraded from "../contract/fixtures/degraded.json";
import { CONFIRM_TOKEN_META_KEY, TOOL_NAMES, describeStatus, type ServiceStatus } from "../src/contract.ts";
import { hostPalette } from "./palette.ts";

interface HostProfile {
  sandbox: string;
  capabilities: McpUiHostCapabilities;
  context: (theme: "light" | "dark", locale: string) => McpUiHostContext;
}

export interface HostLogEntry {
  method: string;
  params: unknown;
}

declare global {
  interface Window {
    hostLog: HostLogEntry[];
    hostState: { initialized: boolean; resultSent: boolean; height: number | null };
  }
}

const profiles: Record<string, HostProfile> = {
  full: {
    sandbox: "allow-scripts allow-same-origin",
    capabilities: { openLinks: {}, serverTools: {}, serverResources: {}, logging: {}, updateModelContext: { text: {} }, message: { text: {} } },
    context: (theme, locale) => ({
      theme,
      locale,
      timeZone: "Europe/Berlin",
      platform: "web",
      displayMode: "inline",
      availableDisplayModes: ["inline", "fullscreen"],
      styles: { variables: hostPalette as McpUiStyles },
      safeAreaInsets: { top: 0, right: 0, bottom: 0, left: 0 },
    }),
  },
  minimal: {
    sandbox: "allow-scripts",
    capabilities: {},
    context: (theme) => ({ theme, displayMode: "inline", availableDisplayModes: ["inline"] }),
  },
};

const fixtures: Record<string, ServiceStatus> = {
  healthy: healthy as ServiceStatus,
  degraded: degraded as ServiceStatus,
};

const params = new URLSearchParams(location.search);
const profile = profiles[params.get("profile") ?? "full"] ?? profiles.full;
const theme = params.get("theme") === "dark" ? "dark" : "light";
const locale = params.get("locale") ?? "en-US";
const status = fixtures[params.get("fixture") ?? "healthy"] ?? fixtures.healthy;
const resultMode = params.get("result") ?? "structured";
const width = Number(params.get("width") ?? "560");

window.hostLog = [];
window.hostState = { initialized: false, resultSent: false, height: null };
document.documentElement.style.colorScheme = theme;
document.body.style.background = theme === "dark" ? "#0b0b0c" : "#f7f7f8";

const issuedTokens = new Set<string>();
const receipts = new Map<string, string>();

function fakeServerTool(name: string, args: Record<string, unknown>): CallToolResult {
  if (name === TOOL_NAMES.prepareRestart) {
    const token = crypto.randomUUID();
    issuedTokens.add(token);
    return {
      content: [{ type: "text", text: `Restart all replicas of ${status.service.name}.` }],
      structuredContent: { serviceId: args.serviceId, summary: `Restart all ${status.replicas.desired} replicas of ${status.service.name}.`, expiresAt: "2026-11-20T10:17:00Z" },
      _meta: { [CONFIRM_TOKEN_META_KEY]: token },
    };
  }
  if (name === TOOL_NAMES.confirmRestart) {
    const key = String(args.idempotencyKey);
    const earlier = receipts.get(key);
    if (earlier) return { content: [{ type: "text", text: "Duplicate" }], structuredContent: { serviceId: args.serviceId, operationId: earlier, outcome: "duplicate" } };
    if (!issuedTokens.delete(String(args.confirmToken))) return { isError: true, content: [{ type: "text", text: "This confirmation is not valid." }] };
    const operationId = "op-0001";
    receipts.set(key, operationId);
    return { content: [{ type: "text", text: "Accepted" }], structuredContent: { serviceId: args.serviceId, operationId, outcome: "accepted" } };
  }
  return { isError: true, content: [{ type: "text", text: `Unknown tool ${name}` }] };
}

function toolResult(): CallToolResult {
  if (resultMode === "text-only") return { content: [{ type: "text", text: describeStatus(status) }] };
  if (resultMode === "malformed") return { content: [{ type: "text", text: describeStatus(status) }], structuredContent: { version: 99 } };
  return { content: [{ type: "text", text: describeStatus(status) }], structuredContent: { ...status } };
}

const iframe = document.getElementById("view") as HTMLIFrameElement;
iframe.setAttribute("sandbox", profile.sandbox);
iframe.style.width = `${width}px`;
iframe.style.maxWidth = "100%";
iframe.style.border = "0";
iframe.style.display = "block";
iframe.style.height = "0px";

const bridge = new AppBridge(null, { name: "fake-host", version: "1.0.0" }, profile.capabilities, {
  hostContext: { ...profile.context(theme, locale), containerDimensions: { width, maxHeight: 2000 } },
});

bridge.oncalltool = async ({ name, arguments: args }) => {
  window.hostLog.push({ method: "tools/call", params: { name, arguments: args } });
  return fakeServerTool(name, args ?? {});
};
bridge.onupdatemodelcontext = async (update) => {
  window.hostLog.push({ method: "ui/update-model-context", params: update });
  return {};
};
bridge.onmessage = async (message) => {
  window.hostLog.push({ method: "ui/message", params: message });
  return {};
};
bridge.onopenlink = async (link) => {
  window.hostLog.push({ method: "ui/open-link", params: link });
  return {};
};
bridge.onsizechange = ({ height }) => {
  if (height === undefined) return;
  iframe.style.height = `${height}px`;
  window.hostState.height = height;
};
bridge.oninitialized = () => {
  window.hostState.initialized = true;
  bridge.sendToolInput({ arguments: { serviceId: status.service.id } });
  if (resultMode === "none") return;
  bridge.sendToolResult(toolResult());
  window.hostState.resultSent = true;
};

await bridge.connect(new PostMessageTransport(iframe.contentWindow!, iframe.contentWindow!));
iframe.srcdoc = appHtml;

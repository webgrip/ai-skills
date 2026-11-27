import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
  type McpUiHostCapabilities,
  type McpUiHostContext,
} from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/client";

export interface BridgeEvents {
  onInput: () => void;
  onResult: (result: CallToolResult) => void;
  onCancelled: () => void;
  onContext: (context: McpUiHostContext) => void;
}

export interface HostFeatures {
  serverTools: boolean;
  updateModelContext: boolean;
}

export function applyHostContext(context: McpUiHostContext): void {
  if (context.theme) applyDocumentTheme(context.theme);
  if (context.styles?.variables) applyHostStyleVariables(context.styles.variables);
  if (context.styles?.css?.fonts) applyHostFonts(context.styles.css.fonts);
}

export function readHostFeatures(capabilities: McpUiHostCapabilities | undefined): HostFeatures {
  return {
    serverTools: capabilities?.serverTools !== undefined,
    updateModelContext: capabilities?.updateModelContext !== undefined,
  };
}

export async function connectToHost(events: BridgeEvents): Promise<App> {
  const app = new App({ name: "service-status-card", version: "1.0.0" }, { availableDisplayModes: ["inline"] });
  let context: McpUiHostContext = {};
  app.ontoolinput = () => events.onInput();
  app.ontoolresult = (result) => events.onResult(result);
  app.ontoolcancelled = () => events.onCancelled();
  app.onhostcontextchanged = (change) => {
    context = { ...context, ...change };
    applyHostContext(context);
    events.onContext(context);
  };
  app.onerror = (error) => console.error(error);
  await app.connect();
  context = app.getHostContext() ?? {};
  applyHostContext(context);
  events.onContext(context);
  return app;
}

export function newIdempotencyKey(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

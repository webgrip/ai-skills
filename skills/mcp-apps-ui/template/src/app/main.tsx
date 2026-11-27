import { render } from "preact";
import { useEffect, useMemo, useRef, useState } from "preact/hooks";
import type { App, McpUiHostContext } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/client";
import {
  CONFIRM_TOKEN_META_KEY,
  TOOL_NAMES,
  readRestartPreview,
  readRestartReceipt,
  readServiceStatus,
  type RestartPreview,
  type ServiceStatus,
} from "../contract.ts";
import { connectToHost, newIdempotencyKey, readHostFeatures, type HostFeatures } from "./bridge.ts";
import { resolveLocale, type Locale } from "./i18n.ts";
import "./tokens.css";
import "./app.css";

type View =
  | { kind: "waiting" }
  | { kind: "ready"; status: ServiceStatus }
  | { kind: "unreadable" };

type Action =
  | { kind: "idle" }
  | { kind: "preparing" }
  | { kind: "confirming"; preview: RestartPreview; token: string; idempotencyKey: string }
  | { kind: "submitting" }
  | { kind: "accepted"; operationId: string }
  | { kind: "failed"; message: string };

function textOf(result: CallToolResult): string | undefined {
  const block = result.content?.find((item) => item.type === "text");
  return block && "text" in block ? block.text : undefined;
}

function Skeleton({ locale }: { locale: Locale }) {
  return (
    <div class="card" aria-busy="true">
      <span class="visually-hidden">{locale.messages.loading}</span>
      <div class="skeleton" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}

interface CardProps {
  app: App;
  status: ServiceStatus;
  locale: Locale;
  features: HostFeatures;
}

function StatusCard({ app, status, locale, features }: CardProps) {
  const [action, setAction] = useState<Action>({ kind: "idle" });
  const restartRef = useRef<HTMLButtonElement>(null);
  const confirmRef = useRef<HTMLButtonElement>(null);
  const t = locale.messages;
  const canAct = features.serverTools && status.actions.restart.allowed;

  useEffect(() => {
    if (action.kind === "confirming") confirmRef.current?.focus();
    if (action.kind === "failed") restartRef.current?.focus();
  }, [action.kind]);

  const prepare = async () => {
    setAction({ kind: "preparing" });
    try {
      const result = await app.callServerTool({ name: TOOL_NAMES.prepareRestart, arguments: { serviceId: status.service.id } });
      const preview = readRestartPreview(result.structuredContent);
      const token = result._meta?.[CONFIRM_TOKEN_META_KEY];
      if (result.isError || !preview || typeof token !== "string") {
        setAction({ kind: "failed", message: textOf(result) ?? t.failed });
        return;
      }
      setAction({ kind: "confirming", preview, token, idempotencyKey: newIdempotencyKey() });
    } catch {
      setAction({ kind: "failed", message: t.failed });
    }
  };

  const confirm = async (pending: Extract<Action, { kind: "confirming" }>) => {
    setAction({ kind: "submitting" });
    try {
      const result = await app.callServerTool({
        name: TOOL_NAMES.confirmRestart,
        arguments: { serviceId: status.service.id, confirmToken: pending.token, idempotencyKey: pending.idempotencyKey },
      });
      const receipt = readRestartReceipt(result.structuredContent);
      if (result.isError || !receipt) {
        setAction({ kind: "failed", message: textOf(result) ?? t.failed });
        return;
      }
      setAction({ kind: "accepted", operationId: receipt.operationId });
      if (features.updateModelContext) {
        await app.updateModelContext({
          content: [{ type: "text", text: `The user restarted ${status.service.name}; operation ${receipt.operationId} was accepted.` }],
        });
      }
    } catch {
      setAction({ kind: "failed", message: t.failed });
    }
  };

  const cancel = () => {
    setAction({ kind: "idle" });
    queueMicrotask(() => restartRef.current?.focus());
  };

  const announcement =
    action.kind === "submitting" ? t.restartRequested : action.kind === "accepted" ? t.restartAccepted : action.kind === "confirming" ? action.preview.summary : "";

  return (
    <article class="card" aria-labelledby="service-title">
      <header class="header">
        <h2 class="title" id="service-title">
          {status.service.name}
        </h2>
        <span class="badge" data-state={status.state}>
          {t.states[status.state]}
        </span>
      </header>
      <dl class="facts">
        <div>
          <dt>{t.release}</dt>
          <dd>{status.release}</dd>
        </div>
        <div>
          <dt>{t.replicas}</dt>
          <dd>
            {status.replicas.ready}/{status.replicas.desired}
          </dd>
        </div>
        <div>
          <dt>{t.updated}</dt>
          <dd>
            <time dateTime={status.updatedAt}>{locale.formatDateTime(status.updatedAt)}</time>
          </dd>
        </div>
      </dl>
      <p class="note" role="status" aria-live="polite">
        {announcement}
      </p>
      {action.kind === "failed" && (
        <p class="note" data-tone="danger" role="alert">
          {action.message}
        </p>
      )}
      {!features.serverTools && <p class="note">{t.actionsUnavailable}</p>}
      {features.serverTools && !status.actions.restart.allowed && <p class="note">{t.restartNotAllowed}</p>}
      {canAct && action.kind === "confirming" && (
        <div class="actions">
          <button class="button" data-variant="primary" type="button" ref={confirmRef} onClick={() => confirm(action)}>
            {t.confirmRestart}
          </button>
          <button class="button" type="button" onClick={cancel}>
            {t.cancel}
          </button>
        </div>
      )}
      {canAct && action.kind !== "confirming" && action.kind !== "accepted" && (
        <div class="actions">
          <button
            class="button"
            type="button"
            ref={restartRef}
            disabled={action.kind === "preparing" || action.kind === "submitting"}
            onClick={prepare}
          >
            {t.restart}
          </button>
        </div>
      )}
    </article>
  );
}

function Root() {
  const [app, setApp] = useState<App | null>(null);
  const [view, setView] = useState<View>({ kind: "waiting" });
  const [context, setContext] = useState<McpUiHostContext>({});
  const locale = useMemo(() => resolveLocale(context.locale, context.timeZone), [context.locale, context.timeZone]);

  useEffect(() => {
    document.documentElement.lang = locale.tag;
  }, [locale.tag]);

  useEffect(() => {
    connectToHost({
      onInput: () => setView({ kind: "waiting" }),
      onResult: (result) => {
        const status = readServiceStatus(result.structuredContent);
        setView(status ? { kind: "ready", status } : { kind: "unreadable" });
      },
      onCancelled: () => setView({ kind: "unreadable" }),
      onContext: setContext,
    })
      .then(setApp)
      .catch((error: unknown) => {
        console.error(error);
        setView({ kind: "unreadable" });
      });
  }, []);

  const insets = context.safeAreaInsets;
  return (
    <main style={insets ? { padding: `${insets.top}px ${insets.right}px ${insets.bottom}px ${insets.left}px` } : undefined}>
      {view.kind === "unreadable" ? (
        <div class="card">
          <p class="note">{locale.messages.unreadable}</p>
        </div>
      ) : view.kind === "waiting" || !app ? (
        <Skeleton locale={locale} />
      ) : (
        <StatusCard app={app} status={view.status} locale={locale} features={readHostFeatures(app.getHostCapabilities())} />
      )}
    </main>
  );
}

render(<Root />, document.getElementById("root")!);

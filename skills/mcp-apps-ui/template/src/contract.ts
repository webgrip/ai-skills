export const SERVICE_STATES = ["healthy", "degraded", "down"] as const;

export type ServiceState = (typeof SERVICE_STATES)[number];

export interface ServiceStatus {
  version: 1;
  service: { id: string; name: string };
  state: ServiceState;
  release: string;
  replicas: { ready: number; desired: number };
  updatedAt: string;
  actions: { restart: { allowed: boolean } };
}

export interface RestartPreview {
  serviceId: string;
  summary: string;
  expiresAt: string;
}

export interface RestartReceipt {
  serviceId: string;
  operationId: string;
  outcome: "accepted" | "duplicate";
}

export const STATUS_RESOURCE_URI = "ui://service-status/v1/card.html";

export const TOOL_NAMES = {
  show: "service_status_show",
  prepareRestart: "service_restart_prepare",
  confirmRestart: "service_restart_confirm",
} as const;

export const CONFIRM_TOKEN_META_KEY = "example.invalid/confirmToken";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function readServiceStatus(value: unknown): ServiceStatus | null {
  if (!isRecord(value) || value.version !== 1) return null;
  const { service, state, release, replicas, updatedAt, actions } = value;
  if (!isRecord(service) || typeof service.id !== "string" || typeof service.name !== "string") return null;
  if (!SERVICE_STATES.includes(state as ServiceState)) return null;
  if (typeof release !== "string" || typeof updatedAt !== "string") return null;
  if (!isRecord(replicas) || typeof replicas.ready !== "number" || typeof replicas.desired !== "number") return null;
  if (!isRecord(actions) || !isRecord(actions.restart) || typeof actions.restart.allowed !== "boolean") return null;
  return value as unknown as ServiceStatus;
}

export function readRestartPreview(value: unknown): RestartPreview | null {
  if (!isRecord(value)) return null;
  const { serviceId, summary, expiresAt } = value;
  if (typeof serviceId !== "string" || typeof summary !== "string" || typeof expiresAt !== "string") return null;
  return { serviceId, summary, expiresAt };
}

export function readRestartReceipt(value: unknown): RestartReceipt | null {
  if (!isRecord(value)) return null;
  const { serviceId, operationId, outcome } = value;
  if (typeof serviceId !== "string" || typeof operationId !== "string") return null;
  if (outcome !== "accepted" && outcome !== "duplicate") return null;
  return { serviceId, operationId, outcome };
}

export function describeStatus(status: ServiceStatus): string {
  const { service, state, release, replicas, updatedAt } = status;
  return `${service.name} is ${state}: release ${release}, ${replicas.ready}/${replicas.desired} replicas ready, updated ${updatedAt}.`;
}

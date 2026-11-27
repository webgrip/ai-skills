#!/usr/bin/env python3
from fastmcp import Context, FastMCP
from fastmcp.apps import AppConfig
from fastmcp.server.dependencies import get_access_token
from fastmcp.tools import ToolResult

from stdlib_server import APP_HTML_PATH, EXTENSION_ID, RESTARTERS, SCHEMA, STATUS_RESOURCE_URI, ServiceStatusServer


def current_principal():
    token = get_access_token()
    return token.claims.get("sub", token.client_id) if token else "local-operator"


core = ServiceStatusServer(
    principal=current_principal,
    may_restart=lambda who, service_id: who in RESTARTERS.get(service_id, set()),
)
mcp = FastMCP("service-status")


def as_tool_result(result):
    return ToolResult(
        content=result["content"][0]["text"],
        structured_content=result.get("structuredContent"),
        meta=result.get("_meta"),
        is_error=result.get("isError", False),
    )


@mcp.tool(
    name="service_status_show",
    title="Show service status",
    description=(
        "Shows the current health, release and replica count of one service as a status card. "
        "Use it when the user asks how a service is doing. Read-only; restarting happens from the card after the user confirms."
    ),
    output_schema=SCHEMA,
    annotations={"title": "Show service status", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    app=AppConfig(resource_uri=STATUS_RESOURCE_URI, visibility=["model", "app"]),
)
def service_status_show(serviceId: str, ctx: Context) -> ToolResult:
    return as_tool_result(core.show({"serviceId": serviceId}, supports_apps=ctx.client_supports_extension(EXTENSION_ID)))


@mcp.tool(
    name="service_restart_prepare",
    title="Prepare a service restart",
    description="Step one of a restart from the status card: checks permission and returns what will happen plus a short-lived confirmation.",
    annotations={"title": "Prepare a service restart", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
    app=AppConfig(resource_uri=STATUS_RESOURCE_URI, visibility=["app"]),
)
def service_restart_prepare(serviceId: str) -> ToolResult:
    return as_tool_result(core.prepare({"serviceId": serviceId}))


@mcp.tool(
    name="service_restart_confirm",
    title="Confirm a service restart",
    description="Step two of a restart from the status card. Requires the confirmation from step one and an idempotency key; repeating a key returns the first receipt.",
    annotations={"title": "Confirm a service restart", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": False, "idempotentHint": True},
    app=AppConfig(resource_uri=STATUS_RESOURCE_URI, visibility=["app"]),
)
def service_restart_confirm(serviceId: str, confirmToken: str, idempotencyKey: str) -> ToolResult:
    return as_tool_result(core.confirm({"serviceId": serviceId, "confirmToken": confirmToken, "idempotencyKey": idempotencyKey}))


@mcp.resource(STATUS_RESOURCE_URI, name="Service status card", app=AppConfig(prefers_border=True))
def service_status_card() -> str:
    return APP_HTML_PATH.read_text()


if __name__ == "__main__":
    mcp.run()

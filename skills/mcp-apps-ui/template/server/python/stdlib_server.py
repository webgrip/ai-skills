#!/usr/bin/env python3
import json
import os
import secrets
import sys
import time
import uuid
from pathlib import Path

EXTENSION_ID = "io.modelcontextprotocol/ui"
APP_MIME_TYPE = "text/html;profile=mcp-app"
CLIENT_CAPABILITIES_META_KEY = "io.modelcontextprotocol/clientCapabilities"
CONFIRM_TOKEN_META_KEY = "example.invalid/confirmToken"
STATUS_RESOURCE_URI = "ui://service-status/v1/card.html"
SUPPORTED_PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18")
CONFIRM_WINDOW_SECONDS = 120

ROOT = Path(__file__).resolve().parents[2]
APP_HTML_PATH = ROOT / "dist" / "app" / "app.html"
SCHEMA = json.loads((ROOT / "contract" / "service-status.schema.json").read_text())
INVENTORY = {
    status["service"]["id"]: status
    for status in (
        json.loads((ROOT / "contract" / "fixtures" / name).read_text())
        for name in ("healthy.json", "degraded.json")
    )
}
RESTARTERS = {"checkout-api": {"local-operator"}}
SERVICE_ID_SCHEMA = {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,62}$"}


def tool_ui_meta(resource_uri, visibility):
    return {"ui": {"resourceUri": resource_uri, "visibility": visibility}, "ui/resourceUri": resource_uri}


def client_supports_apps(capabilities):
    settings = (capabilities or {}).get("extensions", {}).get(EXTENSION_ID) or {}
    return APP_MIME_TYPE in (settings.get("mimeTypes") or [])


def text_result(text, structured=None, meta=None, is_error=False):
    result = {"content": [{"type": "text", "text": text}]}
    if structured is not None:
        result["structuredContent"] = structured
    if meta:
        result["_meta"] = meta
    if is_error:
        result["isError"] = True
    return result


def describe(status):
    replicas = status["replicas"]
    return (
        f"{status['service']['name']} is {status['state']}: release {status['release']}, "
        f"{replicas['ready']}/{replicas['desired']} replicas ready, updated {status['updatedAt']}."
    )


class ServiceStatusServer:
    def __init__(self, principal, may_restart, clock=time.time):
        self.principal = principal
        self.may_restart = may_restart
        self.clock = clock
        self.session_capabilities = {}
        self.pending = {}
        self.receipts = {}

    def tools(self):
        return [
            {
                "name": "service_status_show",
                "title": "Show service status",
                "description": (
                    "Shows the current health, release and replica count of one service as a status card. "
                    "Use it when the user asks how a service is doing. Read-only; restarting happens from the card after the user confirms."
                ),
                "inputSchema": {"type": "object", "properties": {"serviceId": SERVICE_ID_SCHEMA}, "required": ["serviceId"], "additionalProperties": False},
                "outputSchema": SCHEMA,
                "annotations": {"title": "Show service status", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
                "_meta": tool_ui_meta(STATUS_RESOURCE_URI, ["model", "app"]),
            },
            {
                "name": "service_restart_prepare",
                "title": "Prepare a service restart",
                "description": "Step one of a restart from the status card: checks permission and returns what will happen plus a short-lived confirmation.",
                "inputSchema": {"type": "object", "properties": {"serviceId": SERVICE_ID_SCHEMA}, "required": ["serviceId"], "additionalProperties": False},
                "annotations": {"title": "Prepare a service restart", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
                "_meta": tool_ui_meta(STATUS_RESOURCE_URI, ["app"]),
            },
            {
                "name": "service_restart_confirm",
                "title": "Confirm a service restart",
                "description": "Step two of a restart from the status card. Requires the confirmation from step one and an idempotency key; repeating a key returns the first receipt.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "serviceId": SERVICE_ID_SCHEMA,
                        "confirmToken": {"type": "string", "minLength": 16},
                        "idempotencyKey": {"type": "string", "minLength": 8, "maxLength": 64},
                    },
                    "required": ["serviceId", "confirmToken", "idempotencyKey"],
                    "additionalProperties": False,
                },
                "annotations": {"title": "Confirm a service restart", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": False, "idempotentHint": True},
                "_meta": tool_ui_meta(STATUS_RESOURCE_URI, ["app"]),
            },
        ]

    def status_for(self, service_id):
        status = INVENTORY.get(service_id)
        if status is None:
            return None
        allowed = self.may_restart(self.principal(), service_id)
        return {**status, "actions": {"restart": {"allowed": allowed}}}

    def show(self, args, supports_apps):
        status = self.status_for(args.get("serviceId", ""))
        if status is None:
            return text_result(f"Service {args.get('serviceId')} not found. Ask the user for the exact service id.", is_error=True)
        text = describe(status)
        if not supports_apps:
            text += " Restarting needs an operator console; this client shows text only."
        return text_result(text, structured=status)

    def prepare(self, args):
        principal, service_id = self.principal(), args.get("serviceId", "")
        status = INVENTORY.get(service_id)
        if status is None:
            return text_result(f"Service {service_id} not found.", is_error=True)
        if not self.may_restart(principal, service_id):
            return text_result(f"You are not allowed to restart {status['service']['name']}.", is_error=True)
        token = secrets.token_urlsafe(24)
        expires_at = self.clock() + CONFIRM_WINDOW_SECONDS
        self.pending[token] = (principal, service_id, expires_at)
        preview = {
            "serviceId": service_id,
            "summary": f"Restart all {status['replicas']['desired']} replicas of {status['service']['name']} ({status['release']}) one at a time.",
            "expiresAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires_at)),
        }
        return text_result(preview["summary"], structured=preview, meta={CONFIRM_TOKEN_META_KEY: token})

    def confirm(self, args):
        principal, service_id = self.principal(), args.get("serviceId", "")
        receipt_key = (principal, args.get("idempotencyKey", ""))
        earlier = self.receipts.get(receipt_key)
        if earlier:
            return text_result(f"Restart {earlier['operationId']} was already accepted.", structured={**earlier, "outcome": "duplicate"})
        confirmation = self.pending.pop(args.get("confirmToken", ""), None)
        if confirmation is None or confirmation[:2] != (principal, service_id):
            return text_result("This confirmation is not valid. Start the restart again from the status card.", is_error=True)
        if confirmation[2] < self.clock():
            return text_result("This confirmation expired. Start the restart again from the status card.", is_error=True)
        if not self.may_restart(principal, service_id):
            return text_result("You are no longer allowed to restart this service.", is_error=True)
        receipt = {"serviceId": service_id, "operationId": str(uuid.uuid4()), "outcome": "accepted"}
        self.receipts[receipt_key] = receipt
        print(json.dumps({"audit": "service.restart", "principal": principal, "serviceId": service_id, "operationId": receipt["operationId"]}), file=sys.stderr)
        return text_result(f"Restart {receipt['operationId']} accepted for {service_id}.", structured=receipt)

    def handle(self, method, params):
        request_capabilities = (params.get("_meta") or {}).get(CLIENT_CAPABILITIES_META_KEY) or self.session_capabilities
        if method == "initialize":
            self.session_capabilities = params.get("capabilities") or {}
            requested = params.get("protocolVersion")
            return {
                "protocolVersion": requested if requested in SUPPORTED_PROTOCOL_VERSIONS else SUPPORTED_PROTOCOL_VERSIONS[0],
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "service-status", "version": "1.0.0"},
            }
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": self.tools()}
        if method == "resources/list":
            return {"resources": [{"uri": STATUS_RESOURCE_URI, "name": "Service status card", "mimeType": APP_MIME_TYPE}]}
        if method == "resources/read":
            if params.get("uri") != STATUS_RESOURCE_URI:
                raise LookupError(f"Unknown resource {params.get('uri')}")
            return {"contents": [{"uri": STATUS_RESOURCE_URI, "mimeType": APP_MIME_TYPE, "text": APP_HTML_PATH.read_text(), "_meta": {"ui": {"prefersBorder": True}}}]}
        if method == "tools/call":
            name, args = params.get("name"), params.get("arguments") or {}
            if name == "service_status_show":
                return self.show(args, client_supports_apps(request_capabilities))
            if name == "service_restart_prepare":
                return self.prepare(args)
            if name == "service_restart_confirm":
                return self.confirm(args)
            return text_result(f"Unknown tool {name}.", is_error=True)
        raise NotImplementedError(method)


def serve(server, stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        if "id" not in message:
            continue
        try:
            reply = {"jsonrpc": "2.0", "id": message["id"], "result": server.handle(message.get("method"), message.get("params") or {})}
        except NotImplementedError as missing:
            reply = {"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": f"Method not found: {missing}"}}
        except LookupError as unknown:
            reply = {"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32002, "message": str(unknown)}}
        stdout.write(json.dumps(reply) + "\n")
        stdout.flush()


if __name__ == "__main__":
    principal = os.environ.get("MCP_PRINCIPAL", "local-operator")
    serve(ServiceStatusServer(principal=lambda: principal, may_restart=lambda who, service_id: who in RESTARTERS.get(service_id, set())))

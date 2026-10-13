#!/usr/bin/env python3
import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

USAGE = """Static check of an MCP tool surface: a tools/list result, a JSON-RPC response,
a bare array of tools, or a directory of one-tool JSON snapshots (*.json, *.snap).
Finds missing or contradictory annotations, undescribed parameters, name-rule
violations, secrets mirrored into headers and an oversized surface. Stdlib only,
no network. Exit 0 clean, 1 findings at or above --fail-on, 2 unreadable input."""

SEVERITY_RANK = {"note": 0, "warn": 1, "error": 2}
SPEC_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
DIRECTORY_NAME_LIMIT = 64
THIN_DESCRIPTION_CHARS = 40
COUNT_NOTE = 15
COUNT_WARN = 25
TOKENS_WARN = 10_000
CHARS_PER_TOKEN = 4
MODEL_INSTRUCTION = re.compile(
    r"(ignore|disregard)\s+(all\s+|any\s+)?(previous|prior|other)"
    r"|before\s+(using|calling)\s+(any|every)\s+(other\s+)?tools?"
    r"|instead\s+of\s+(any|all|the)\s+other\s+tools?"
    r"|<\s*/?\s*important\s*>"
    r"|system\s+prompt"
    r"|do\s+not\s+(tell|mention|reveal)\b.{0,20}\buser",
    re.IGNORECASE,
)
SENSITIVE_PARAM = re.compile(r"token|secret|password|passwd|api[_-]?key|credential|email|ssn|iban", re.IGNORECASE)
PAGE_SIZE_PARAM = re.compile(r"^(limit|per_?page|page_?size|max_?results|count|top)$", re.IGNORECASE)
READ_NAME = re.compile(r"(^|[_.-])(get|list|search|read|find|describe|show)([_.-]|$)", re.IGNORECASE)
HTTP_READ = {"get", "head"}
HTTP_WRITE = {"post", "put", "patch", "delete"}


@dataclass
class Finding:
    severity: str
    rule: str
    tool: str
    message: str


def load_tools(path: Path) -> list[dict]:
    if path.is_dir():
        tools = []
        for file in sorted([*path.glob("*.json"), *path.glob("*.snap")]):
            tools.extend(load_tools(file))
        return tools
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "result" in data:
        data = data["result"]
    if isinstance(data, dict) and "tools" in data:
        data = data["tools"]
    if isinstance(data, dict) and "name" in data and "inputSchema" in data:
        data = [data]
    if not isinstance(data, list):
        raise ValueError(f"{path}: no tools array found")
    return [tool for tool in data if isinstance(tool, dict)]


def is_bool(value) -> bool:
    return isinstance(value, bool)


def schema_types(schema: dict) -> set[str]:
    declared = schema.get("type")
    if isinstance(declared, list):
        return set(declared)
    return {declared} if isinstance(declared, str) else set()


def check_name(tool: dict, name: str, seen: set[str]) -> list[Finding]:
    found = []
    if not SPEC_NAME.match(name):
        found.append(Finding("error", "name-invalid", name, "name must be 1-128 chars of A-Z a-z 0-9 _ . -"))
    elif len(name) > DIRECTORY_NAME_LIMIT:
        found.append(Finding("warn", "name-over-64", name, f"{len(name)} chars; the Claude connector directory caps names at 64"))
    if name in seen:
        found.append(Finding("error", "name-duplicate", name, "tool names must be unique within a server"))
    seen.add(name)
    return found


def check_description(tool: dict, name: str) -> list[Finding]:
    description = tool.get("description")
    if not isinstance(description, str) or not description.strip():
        return [Finding("error", "description-missing", name, "the description is the only routing signal the model gets")]
    found = []
    if len(description.strip()) < THIN_DESCRIPTION_CHARS:
        found.append(Finding("note", "description-thin", name, "say when to use it, what it returns and which sibling to use instead"))
    match = MODEL_INSTRUCTION.search(description)
    if match:
        found.append(Finding("warn", "description-instructs-model", name, f"steers the model beyond this tool's function: '{match.group(0)}'"))
    return found


def check_annotations(tool: dict, name: str) -> list[Finding]:
    annotations = tool.get("annotations") if isinstance(tool.get("annotations"), dict) else {}
    found = []
    if not tool.get("title") and not annotations.get("title"):
        found.append(Finding("warn", "title-missing", name, "set title (or annotations.title) for the client's approval UI"))
    read_only = annotations.get("readOnlyHint")
    if not is_bool(read_only):
        found.append(Finding("warn", "readonly-hint-missing", name, "readOnlyHint unset defaults to false: the tool is treated as mutating"))
    if read_only is not True and not is_bool(annotations.get("destructiveHint")):
        found.append(Finding("warn", "destructive-hint-missing", name, "destructiveHint unset defaults to true on a non-read-only tool"))
    if read_only is True and annotations.get("destructiveHint") is True:
        found.append(Finding("error", "hint-contradiction", name, "readOnlyHint and destructiveHint are both true"))
    if not is_bool(annotations.get("openWorldHint")):
        found.append(Finding("note", "openworld-hint-missing", name, "openWorldHint unset defaults to true; set false for a bounded private system"))
    if read_only is not True and READ_NAME.search(name) and not re.search(r"write|update|create|delete|set|add|remove|mark", name, re.IGNORECASE):
        found.append(Finding("note", "read-name-not-read-only", name, "the name reads like a query but readOnlyHint is not true"))
    return found


def check_input_schema(tool: dict, name: str) -> list[Finding]:
    schema = tool.get("inputSchema")
    if not isinstance(schema, dict) or "object" not in schema_types(schema):
        return [Finding("error", "input-schema-missing", name, "inputSchema must be a JSON Schema of type object")]
    found = []
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    if schema.get("additionalProperties") is not False:
        found.append(Finding("note", "schema-open", name, "set additionalProperties: false so misspelt arguments fail loudly"))
    for missing in sorted(set(schema.get("required") or []) - set(properties)):
        found.append(Finding("error", "required-unknown", name, f"required lists '{missing}', which is not a property"))
    for param, spec in properties.items():
        if not isinstance(spec, dict):
            continue
        found.extend(check_param(name, param, spec))
    return found


def check_param(name: str, param: str, spec: dict) -> list[Finding]:
    found = []
    types = schema_types(spec)
    if not spec.get("description") and "$ref" not in spec:
        found.append(Finding("warn", "param-undescribed", name, f"'{param}' has no description"))
    if "object" in types and not spec.get("properties") and spec.get("additionalProperties") is not False:
        found.append(Finding("note", "param-opaque-object", name, f"'{param}' is a free-form object; flatten it into named primitives"))
    if types & {"integer", "number"} and PAGE_SIZE_PARAM.match(param) and "maximum" not in spec:
        found.append(Finding("note", "page-size-unbounded", name, f"'{param}' has no maximum; bound it and give a default"))
    if "x-mcp-header" in spec and SENSITIVE_PARAM.search(param):
        found.append(Finding("error", "sensitive-header-mirror", name, f"'{param}' is mirrored into an Mcp-Param header; never secrets or PII"))
    enum = {str(value).lower() for value in spec.get("enum") or []}
    if enum & HTTP_READ and enum & HTTP_WRITE:
        found.append(Finding("warn", "read-write-mixed", name, f"'{param}' selects both reads and writes; split read and write tools"))
    return found


def check_surface(tools: list[dict]) -> list[Finding]:
    found = []
    count = len(tools)
    if count > COUNT_WARN:
        found.append(Finding("warn", "tool-count", "*", f"{count} tools; past ~25 switch to toolsets or a search plus execute layer"))
    elif count > COUNT_NOTE:
        found.append(Finding("note", "tool-count", "*", f"{count} tools; audit for merges past ~15"))
    tokens = surface_tokens(tools)
    if tokens > TOKENS_WARN:
        found.append(Finding("warn", "surface-tokens", "*", f"~{tokens} tokens of definitions before the first message"))
    return found


def surface_tokens(tools: list[dict]) -> int:
    without_icons = [{key: value for key, value in tool.items() if key != "icons"} for tool in tools]
    return len(json.dumps(without_icons, separators=(",", ":"))) // CHARS_PER_TOKEN


def lint(tools: list[dict]) -> list[Finding]:
    if not tools:
        return [Finding("error", "no-tools", "*", "no tools found in the input")]
    found = []
    seen: set[str] = set()
    for tool in tools:
        name = str(tool.get("name") or "")
        found.extend(check_name(tool, name, seen))
        found.extend(check_description(tool, name))
        found.extend(check_annotations(tool, name))
        found.extend(check_input_schema(tool, name))
        if "outputSchema" not in tool:
            found.append(Finding("note", "output-schema-missing", name, "declare outputSchema and return structuredContent with a text mirror"))
    found.extend(check_surface(tools))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--fail-on", choices=["note", "warn", "error", "never"], default="warn")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        tools = [tool for path in args.paths for tool in load_tools(path)]
    except (OSError, ValueError) as problem:
        print(f"tools_lint: {problem}", file=sys.stderr)
        return 2
    findings = lint(tools)
    findings.sort(key=lambda f: (-SEVERITY_RANK[f.severity], f.rule, f.tool))
    if args.json:
        print(json.dumps({"tools": len(tools), "approx_tokens": surface_tokens(tools), "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        for f in findings:
            print(f"{f.severity:5} {f.rule:28} {f.tool}: {f.message}")
        print(f"{len(tools)} tools, ~{surface_tokens(tools)} tokens of definitions, {len(findings)} findings")
    if args.fail_on == "never":
        return 0
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[f.severity] >= threshold for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())

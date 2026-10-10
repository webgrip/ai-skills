#!/usr/bin/env python3
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

SKIPPED_DIRECTORIES = {".git", "node_modules", "vendor", ".venv", "venv", "dist", "build", ".next", "target", "storage"}
ROOT_INSTRUCTION_FILES = [
    "CLAUDE.md",
    "CLAUDE.local.md",
    ".claude/CLAUDE.md",
    "AGENTS.md",
    "AGENTS.override.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".junie/AGENTS.md",
    ".junie/guidelines.md",
    ".cursorrules",
    ".windsurfrules",
]
RULE_DIRECTORIES = [".claude/rules", ".cursor/rules", ".github/instructions", ".ai/rules", ".ai/guidelines", ".junie/rules"]
SKILL_DIRECTORIES = [".claude/skills", ".agents/skills", ".junie/skills", ".cursor/skills", ".opencode/skills", ".openhands/skills"]
NESTED_FILE_NAMES = {"CLAUDE.md", "AGENTS.md"}
EMPHASIS = re.compile(r"\b(YOU MUST|MUST|CRITICAL|IMPORTANT|NEVER|ALWAYS|REQUIRED|DO NOT)\b")
IMPORT_REFERENCE = re.compile(r"(?<![\w@`])@((?:~/|\.{1,2}/|/)?[\w.-]+(?:/[\w.-]+)*)")
MARKDOWN_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
GENERATED_BLOCKS = [
    ("laravel-boost", re.compile(r"<laravel-boost-guidelines>"), re.compile(r"</laravel-boost-guidelines>")),
    ("marker", re.compile(r"<!--\s*(BEGIN|START)[^>]*(GENERATED|AUTO)[^>]*-->", re.I), re.compile(r"<!--\s*END[^>]*-->", re.I)),
]
CONFIG_FILES = [".claude/settings.json", ".claude/settings.local.json", ".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json", ".gemini/settings.json"]
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\u00ad\u180e]|[\U000E0000-\U000E007F]")
PIPE_TO_SHELL = re.compile(r"\b(curl|wget|iwr|Invoke-WebRequest)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b|\biex\b|\beval\s*\$\(|base64\s+(-d|--decode)", re.I)
SKILL_BROAD_TOOLS = re.compile(r"^allowed-tools:.*\bBash\b(?!\()", re.M)
COMMENT_IMPERATIVE = re.compile(r"<!--(?:(?!-->).)*\b(ignore (all|previous)|disregard|do not tell|don't mention|execute|exfiltrat|send .* to http)\b", re.I | re.S)
SECRET = re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|glpat-[A-Za-z0-9_-]{20,}|sk-(ant-)?[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
ZERO_WIDTH_JOINER = "\u200d"
EMOJI_MODIFIERS = {"\ufe0f", "\U0001f3fb", "\U0001f3fc", "\U0001f3fd", "\U0001f3fe", "\U0001f3ff"}
CODEX_PROJECT_DOC_MAX_BYTES = 32 * 1024
ANTHROPIC_LINE_TARGET = 200
LONG_LINE_CHARACTERS = 400
MARKDOWN_BYTES_PER_TOKEN = 2.9
BYTES_PER_TOKEN_VARIABLE = "AGENT_INSTRUCTIONS_BYTES_PER_TOKEN"


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def strip_code_fences(text):
    kept, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return kept


def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def tracked_files(root):
    try:
        output = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return set(output.splitlines())


def estimate_tokens(byte_count, bytes_per_token):
    return round(byte_count / bytes_per_token)


def positive_ratio(value):
    try:
        ratio = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number of bytes per token")
    if ratio <= 0:
        raise argparse.ArgumentTypeError(f"{value!r} must be above 0 bytes per token")
    return ratio


def default_bytes_per_token():
    configured = os.environ.get(BYTES_PER_TOKEN_VARIABLE)
    if not configured:
        return MARKDOWN_BYTES_PER_TOKEN
    try:
        return positive_ratio(configured)
    except argparse.ArgumentTypeError as error:
        sys.exit(f"{BYTES_PER_TOKEN_VARIABLE}: {error}")


def file_facts(root, path, bytes_per_token):
    raw = read_text(path)
    loaded = strip_html_comments(raw)
    prose = strip_code_fences(loaded)
    facts = {
        "path": str(path.relative_to(root)),
        "lines": len(raw.splitlines()),
        "bytes": len(raw.encode("utf-8")),
        "loaded_bytes": len(loaded.encode("utf-8")),
        "est_tokens": estimate_tokens(len(loaded.encode("utf-8")), bytes_per_token),
        "emphasis": len(EMPHASIS.findall("\n".join(prose))),
        "long_lines": sum(1 for line in prose if len(line) > LONG_LINE_CHARACTERS),
        "imports": import_references(prose),
    }
    if path.is_symlink():
        facts["symlink_to"] = os.readlink(path)
    blocks = generated_blocks(raw)
    if blocks:
        facts["generated_blocks"] = blocks
    return facts


def generated_blocks(text):
    lines = text.splitlines()
    found = []
    for name, start_pattern, end_pattern in GENERATED_BLOCKS:
        start = next((index for index, line in enumerate(lines) if start_pattern.search(line)), None)
        if start is None:
            continue
        end = next((index for index in range(start + 1, len(lines)) if end_pattern.search(lines[index])), len(lines) - 1)
        found.append({"kind": name, "start_line": start + 1, "end_line": end + 1, "lines": end - start + 1, "outside_lines": len(lines) - (end - start + 1)})
    return found


def import_references(lines):
    references = []
    for line in lines:
        without_code = re.sub(r"`[^`]*`", "", line)
        references.extend(match.group(1).rstrip(".,;:") for match in IMPORT_REFERENCE.finditer(without_code))
    return references


def import_target(path, name):
    return Path(os.path.expanduser(name)) if name.startswith("~") else (Path(name) if name.startswith("/") else path.parent / name)


def looks_like_file(name):
    return "/" in name or re.search(r"\.(md|mdc|txt)$", name) is not None


def resolve_imports(root, path, depth=0, seen=None):
    seen = seen if seen is not None else set()
    real = path.resolve()
    if depth > 4 or real in seen or not path.exists():
        return 0, 0, []
    seen.add(real)
    text = strip_html_comments(read_text(path))
    total_bytes, total_lines, missing = len(text.encode("utf-8")), len(text.splitlines()), []
    for name in import_references(strip_code_fences(text)):
        target = import_target(path, name)
        if not target.is_file():
            if looks_like_file(name) and name.endswith((".md", ".mdc", ".txt")):
                missing.append(f"{path.relative_to(root) if path.is_relative_to(root) else path} -> @{name}")
            continue
        size, lines, deeper_missing = resolve_imports(root, target, depth + 1, seen)
        total_bytes += size
        total_lines += lines
        missing.extend(deeper_missing)
    return total_bytes, total_lines, missing


def unscoped_rules(root):
    directory = root / ".claude" / "rules"
    if not directory.is_dir():
        return []
    return [path for path in sorted(directory.rglob("*.md")) if not re.match(r"^---\s*\n(?:.*\n)*?paths\s*:", read_text(path))]


def launch_cost(root):
    seen, total_bytes, total_lines, missing = set(), 0, 0, []
    entries = [root / "CLAUDE.md", root / ".claude" / "CLAUDE.md", root / "CLAUDE.local.md", *unscoped_rules(root)]
    for entry in entries:
        if entry.is_file():
            size, lines, entry_missing = resolve_imports(root, entry, seen=seen)
            total_bytes += size
            total_lines += lines
            missing.extend(entry_missing)
    return total_bytes, total_lines, missing


def dead_links(root, path):
    dead = []
    for line in strip_code_fences(strip_html_comments(read_text(path))):
        for target in MARKDOWN_LINK.findall(line):
            if re.match(r"^[a-z]+:", target) or target.startswith("/"):
                continue
            if not (path.parent / target).exists():
                dead.append(f"{path.relative_to(root)} -> {target}")
    return dead


def claude_agents_relation(root):
    claude, agents = root / "CLAUDE.md", root / "AGENTS.md"
    if not claude.exists() and not agents.exists():
        return "neither"
    if not claude.exists():
        return "agents-only"
    if not agents.exists():
        return "claude-only"
    if claude.is_symlink() and claude.resolve() == agents.resolve():
        return "claude-symlink-to-agents"
    if agents.is_symlink() and agents.resolve() == claude.resolve():
        return "agents-symlink-to-claude"
    claude_text = read_text(claude)
    first_line = next((line.strip() for line in claude_text.splitlines() if line.strip()), "")
    if first_line == "@AGENTS.md":
        return "claude-imports-agents"
    if "@AGENTS.md" in claude_text:
        return "claude-imports-agents-not-first"
    agents_text = read_text(agents)
    if claude_text == agents_text:
        return "identical-copies"
    ratio = difflib.SequenceMatcher(None, claude_text, agents_text, autojunk=False).quick_ratio()
    return f"diverging-copies ({ratio:.0%} similar)"


def nested_instruction_files(root):
    found = []
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name not in SKIPPED_DIRECTORIES and not name.startswith(".")]
        current = Path(directory)
        if current == root:
            continue
        for name in files:
            if name in NESTED_FILE_NAMES:
                found.append(current / name)
    return found


def skill_directories(root, tracked):
    report = []
    names_per_directory = {}
    for relative in SKILL_DIRECTORIES:
        path = root / relative
        if not path.exists() and not path.is_symlink():
            continue
        entry = {"path": relative}
        if path.is_symlink():
            entry["symlink_to"] = os.readlink(path)
        else:
            names = sorted(child.name for child in path.iterdir() if child.is_dir())
            entry["skills"] = len(names)
            tracked_count = sum(1 for name in tracked if name.startswith(relative + "/")) if tracked is not None else None
            entry["tracked_files"] = tracked_count
            if tracked_count is None or tracked_count > 0:
                names_per_directory[relative] = set(names)
        report.append(entry)
    copies = [relative for relative, names in names_per_directory.items() if names]
    overlap = set.intersection(*(names_per_directory[relative] for relative in copies)) if len(copies) > 1 else set()
    return report, sorted(overlap)


def is_emoji(character):
    return unicodedata.category(character) == "So"


def joins_emoji(text, index):
    before = index - 1
    while before >= 0 and text[before] in EMOJI_MODIFIERS:
        before -= 1
    return before >= 0 and index + 1 < len(text) and is_emoji(text[before]) and is_emoji(text[index + 1])


def locate(text, match):
    line = text.count("\n", 0, match.start()) + 1
    return line, match.group(0)


PACKAGE_RUNNERS = {"npx", "bunx", "uvx", "pnpm", "yarn", "pipx"}
BROAD_COMMAND = re.compile(r"^(Bash|Shell)(\((\*|(python3?|node|bun|deno|ruby|perl|php|sh|bash|zsh|npx|uvx|pip|npm|docker|kubectl|ssh|curl|wget|env|xargs|find)(:\*| \*))\))?$")


def json_config_findings(name, text):
    try:
        config = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(config, dict):
        return []
    findings = []
    for grant in (config.get("permissions") or {}).get("allow") or []:
        if isinstance(grant, str) and BROAD_COMMAND.match(grant):
            findings.append(("warn", f"{name}: broad permission grant {grant} in permissions.allow"))
    if config.get("enableAllProjectMcpServers") is True:
        findings.append(("error", f"{name}: enableAllProjectMcpServers is true; any server in the repo's .mcp.json starts after one trust click"))
    for key in (config.get("env") or {}):
        if key.endswith("_BASE_URL"):
            findings.append(("error", f"{name}: env sets {key}; can redirect API traffic and keys"))
    if config.get("hooks"):
        findings.append(("info", f"{name}: defines hooks; review their commands like code"))
    for server_name, server in (config.get("mcpServers") or {}).items():
        if not isinstance(server, dict) or Path(str(server.get("command", ""))).name not in PACKAGE_RUNNERS:
            continue
        packages = [argument for argument in server.get("args") or [] if isinstance(argument, str) and not argument.startswith("-") and argument not in ("dlx", "exec", "run")]
        if packages and not re.search(r"@\d|==\d", packages[0]):
            findings.append(("warn", f"{name}: MCP server '{server_name}' runs '{packages[0]}' without a pinned version"))
        if str(server.get("url", "")).startswith("http://"):
            findings.append(("warn", f"{name}: MCP server '{server_name}' uses plain http"))
    return findings


def security_findings(root, tracked):
    findings = []
    candidates = [root / relative for relative in ROOT_INSTRUCTION_FILES + CONFIG_FILES]
    for relative in RULE_DIRECTORIES + SKILL_DIRECTORIES:
        directory = root / relative
        if directory.is_dir():
            candidates.extend(path for path in directory.rglob("*") if path.is_file() and path.suffix in (".md", ".mdc", ".php", ".json", ".sh", ".py"))
    candidates.extend(nested_instruction_files(root))
    for path in dict.fromkeys(candidates):
        if not path.is_file():
            continue
        text = read_text(path)
        name = str(path.relative_to(root))
        for match in INVISIBLE.finditer(text):
            if match.group(0) == ZERO_WIDTH_JOINER and joins_emoji(text, match.start()):
                continue
            line, character = locate(text, match)
            findings.append(("error", f"{name}:{line}: invisible or bidi character U+{ord(character):04X}"))
        for pattern, level, label in ((PIPE_TO_SHELL, "error", "fetch-and-execute instruction"), (SECRET, "error", "possible secret"), (COMMENT_IMPERATIVE, "warn", "imperative inside an HTML comment")):
            for match in pattern.finditer(text):
                line, _ = locate(text, match)
                findings.append((level, f"{name}:{line}: {label}"))
        if path.name == "SKILL.md" and SKILL_BROAD_TOOLS.search(text):
            findings.append(("warn", f"{name}: allowed-tools grants unrestricted Bash"))
        if path.suffix == ".json":
            findings.extend(json_config_findings(name, text))
        if path.name == "settings.local.json" and tracked is not None and name in tracked:
            findings.append(("error", f"{name}: per-machine settings are committed"))
    return findings


def findings_for(report, budget_lines):
    findings = []
    relation = report["claude_agents_relation"]
    if relation.startswith("diverging-copies") or relation == "identical-copies":
        findings.append(("error", f"CLAUDE.md and AGENTS.md are two copies ({relation}); make AGENTS.md canonical and CLAUDE.md '@AGENTS.md'"))
    if relation in ("claude-symlink-to-agents", "agents-symlink-to-claude"):
        findings.append(("warn", "CLAUDE.md/AGENTS.md linked by symlink; '@AGENTS.md' in a real CLAUDE.md leaves room for Claude-only lines and survives Windows checkouts"))
    if relation == "claude-imports-agents-not-first":
        findings.append(("warn", "CLAUDE.md imports AGENTS.md but not on its first line"))
    for facts in report["files"]:
        if facts["lines"] > ANTHROPIC_LINE_TARGET:
            blocks = facts.get("generated_blocks", [])
            if blocks:
                hand_written = blocks[0]["outside_lines"]
                findings.append(("info" if hand_written <= ANTHROPIC_LINE_TARGET else "warn", f"{facts['path']}: {facts['lines']} lines, of which {blocks[0]['lines']} generated and {hand_written} hand-written; budget the hand-written part and trim the generated one through the generator's exclude/override settings"))
            else:
                findings.append(("warn", f"{facts['path']}: {facts['lines']} lines, over the ~{ANTHROPIC_LINE_TARGET}-line target per file"))
        if facts["emphasis"] > 5:
            findings.append(("warn", f"{facts['path']}: {facts['emphasis']} emphasis words (MUST/CRITICAL/IMPORTANT/NEVER/ALWAYS); current Claude models overtrigger on them"))
        if facts["long_lines"]:
            findings.append(("warn", f"{facts['path']}: {facts['long_lines']} lines over {LONG_LINE_CHARACTERS} chars — paragraphs of knowledge that belong in docs/"))
        for block in facts.get("generated_blocks", []):
            findings.append(("info", f"{facts['path']}: generated {block['kind']} block, lines {block['start_line']}-{block['end_line']}; hand edits inside it are lost on regeneration"))
    agents_bytes = report.get("agents_md_chain_bytes", 0)
    if agents_bytes > CODEX_PROJECT_DOC_MAX_BYTES:
        findings.append(("warn", f"root AGENTS.md is {agents_bytes} bytes; Codex reads {CODEX_PROJECT_DOC_MAX_BYTES} bytes by default across all AGENTS.md files from the repo root to the working directory"))
    if report["claude_md_launch_bytes"] and budget_lines and report["claude_md_launch_lines"] > budget_lines:
        findings.append(("error", f"Claude Code loads {report['claude_md_launch_lines']} lines at launch (CLAUDE.md, CLAUDE.local.md, unscoped rules and their imports), over the budget of {budget_lines}"))
    for missing in report["missing_imports"]:
        findings.append(("error", f"import target missing: {missing}"))
    for dead in report["dead_links"]:
        findings.append(("warn", f"dead link: {dead}"))
    if report["duplicated_skills"]:
        findings.append(("warn", f"{len(report['duplicated_skills'])} skills are committed in more than one skills directory; keep one tracked copy and link or generate the rest"))
    if (Path(report["root"]) / "CLAUDE.local.md").exists() and (Path(report["root"]) / "AGENTS.md").exists():
        findings.append(("info", "CLAUDE.local.md exists: Claude Code then skips native AGENTS.md loading, so CLAUDE.md must import it"))
    return findings


def measure(root, budget_lines, bytes_per_token=MARKDOWN_BYTES_PER_TOKEN):
    tracked = tracked_files(root)
    paths = [root / relative for relative in ROOT_INSTRUCTION_FILES if (root / relative).exists() or (root / relative).is_symlink()]
    for relative in RULE_DIRECTORIES:
        directory = root / relative
        if directory.is_dir():
            paths.extend(sorted(path for path in directory.rglob("*") if path.is_file() and path.suffix in (".md", ".mdc", ".php")))
    paths.extend(nested_instruction_files(root))
    files = [file_facts(root, path, bytes_per_token) for path in dict.fromkeys(paths)]
    launch_bytes, launch_lines, missing = launch_cost(root)
    codex_file = root / "AGENTS.override.md" if (root / "AGENTS.override.md").is_file() else root / "AGENTS.md"
    skills, duplicated = skill_directories(root, tracked)
    dead = []
    for path in paths:
        if path.name in ("CLAUDE.md", "AGENTS.md") or path.suffix in (".md", ".mdc"):
            dead.extend(dead_links(root, path))
    report = {
        "root": str(root),
        "claude_agents_relation": claude_agents_relation(root),
        "claude_md_launch_bytes": launch_bytes,
        "claude_md_launch_tokens_est": estimate_tokens(launch_bytes, bytes_per_token),
        "bytes_per_token": bytes_per_token,
        "claude_md_launch_lines": launch_lines,
        "agents_md_chain_bytes": len(read_text(codex_file).encode("utf-8")) if codex_file.is_file() else 0,
        "files": files,
        "missing_imports": missing,
        "dead_links": dead,
        "skill_directories": skills,
        "duplicated_skills": duplicated,
    }
    report["security"] = [{"level": level, "message": message} for level, message in security_findings(root, tracked)]
    report["findings"] = [{"level": level, "message": message} for level, message in findings_for(report, budget_lines)] + report["security"]
    return report


def print_text(report):
    print(f"Repository: {report['root']}")
    print(f"CLAUDE.md / AGENTS.md: {report['claude_agents_relation']}")
    print(f"Loaded by Claude Code at launch: ~{report['claude_md_launch_lines']} lines, {report['claude_md_launch_bytes']} bytes, ~{report['claude_md_launch_tokens_est']} tokens at {report['bytes_per_token']} bytes per token")
    print()
    print(f"{'file':60} {'lines':>6} {'bytes':>8} {'~tok':>6} {'emph':>5} {'long':>5}")
    for facts in report["files"]:
        suffix = f"  -> {facts['symlink_to']}" if "symlink_to" in facts else ""
        print(f"{facts['path'][:60]:60} {facts['lines']:>6} {facts['bytes']:>8} {facts['est_tokens']:>6} {facts['emphasis']:>5} {facts['long_lines']:>5}{suffix}")
    if report["skill_directories"]:
        print()
        for entry in report["skill_directories"]:
            detail = f"-> {entry['symlink_to']}" if "symlink_to" in entry else f"{entry['skills']} skills, {entry.get('tracked_files', '?')} tracked files"
            print(f"skills: {entry['path']:20} {detail}")
    print()
    if not report["findings"]:
        print("No findings.")
    for finding in report["findings"]:
        print(f"[{finding['level']}] {finding['message']}")


def main():
    parser = argparse.ArgumentParser(description="Measure a repository's agent instruction files: size, load cost, CLAUDE.md/AGENTS.md relation, emphasis, generated blocks, dead links, duplicated skills.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument("--security-only", action="store_true", help="report only the security scan: hidden characters, fetch-and-execute, secrets, broad grants, risky MCP and hook config")
    parser.add_argument("--budget-lines", type=int, default=0, help="fail when what Claude Code loads at launch (CLAUDE.md, CLAUDE.local.md, unscoped rules, imports) exceeds this many lines")
    parser.add_argument("--fail-on", choices=["error", "warn", "never"], default="error", help="exit 1 on findings at or above this level")
    parser.add_argument("--bytes-per-token", type=positive_ratio, default=default_bytes_per_token(), help=f"bytes per token for the token estimates (default {MARKDOWN_BYTES_PER_TOKEN}, measured on Markdown instruction files with claude -p /context; override with {BYTES_PER_TOKEN_VARIABLE})")
    arguments = parser.parse_args()
    root = Path(arguments.root).resolve()
    report = measure(root, arguments.budget_lines, arguments.bytes_per_token)
    if arguments.security_only:
        report["findings"] = report["security"]
        for finding in report["findings"]:
            print(f"[{finding['level']}] {finding['message']}")
        if not report["findings"]:
            print("No security findings.")
    elif arguments.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    levels = {"error": {"error"}, "warn": {"error", "warn"}, "never": set()}[arguments.fail_on]
    sys.exit(1 if any(finding["level"] in levels for finding in report["findings"]) else 0)


if __name__ == "__main__":
    main()

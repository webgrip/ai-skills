#!/usr/bin/env python3
import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

ZERO_WIDTH_SPACE = "​"
FENCE = re.compile(r"^\s{0,3}(```|~~~)")
QUICK_ACTION = re.compile(r"^(\s*)/(?=[A-Za-z])")
MENTION = re.compile(r"(?<![\w.+\-/`])@(?=[A-Za-z0-9_])")
CLOSING_KEYWORD = re.compile(
    r"\b(close[sd]?|closing|fix(?:e[sd])?|fixing|resolve[sd]?|resolving|implement(?:s|ed|ing)?)"
    r"(?=:?\s+(?:[\w.\-]+(?:/[\w.\-]+)*)?#\d|:?\s+https?://\S+/issues/\d)",
    re.IGNORECASE,
)
RULES = ("quick-action", "mention", "closing-keyword")
DEFAULT_MAX_AGE_SECONDS = 300
EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_USAGE = 2


def break_keyword(match: "re.Match[str]") -> str:
    word = match.group(1)
    return word[0] + ZERO_WIDTH_SPACE + word[1:]


def neutralise_line(line: str, fired: Dict[str, int]) -> str:
    escaped, quick_actions = QUICK_ACTION.subn(r"\1\\/", line)
    escaped, mentions = MENTION.subn("@" + ZERO_WIDTH_SPACE, escaped)
    escaped, keywords = CLOSING_KEYWORD.subn(break_keyword, escaped)
    fired["quick-action"] += quick_actions
    fired["mention"] += mentions
    fired["closing-keyword"] += keywords
    return escaped


def neutralise(text: str) -> Tuple[str, Dict[str, int]]:
    fired = {rule: 0 for rule in RULES}
    inside_fence = False
    output: List[str] = []
    for line in text.splitlines(keepends=True):
        if FENCE.match(line):
            inside_fence = not inside_fence
            output.append(line)
            continue
        output.append(line if inside_fence else neutralise_line(line, fired))
    return "".join(output), fired


def read_text(path: Optional[str]) -> str:
    if path is None:
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def command_neutralise(arguments: argparse.Namespace) -> int:
    safe_text, fired = neutralise(read_text(arguments.file))
    if arguments.json:
        fired_rules = {rule: count for rule, count in fired.items() if count}
        print(json.dumps({"text": safe_text, "fired": fired_rules}, ensure_ascii=False))
    else:
        sys.stdout.write(safe_text)
    return 0


def header_lookup(headers: Dict[str, str]) -> Dict[str, str]:
    return {name.lower(): str(value) for name, value in headers.items()}


def gitlab_signing_key(secret: str) -> bytes:
    encoded = secret[len("whsec_"):] if secret.startswith("whsec_") else secret
    return base64.b64decode(encoded, validate=True)


def verify_gitlab(headers: Dict[str, str], body: bytes, secret: str, now: int, max_age: int) -> Tuple[bool, str]:
    message_id = headers.get("webhook-id")
    timestamp = headers.get("webhook-timestamp")
    signatures = headers.get("webhook-signature")
    if not signatures:
        if "x-gitlab-token" in headers:
            return False, "no webhook-signature: X-Gitlab-Token is a plain shared secret, configure a signing token"
        return False, "no webhook-signature header"
    if not message_id or not timestamp:
        return False, "webhook-id or webhook-timestamp missing"
    if not timestamp.isdigit():
        return False, "webhook-timestamp is not a Unix timestamp"
    if abs(now - int(timestamp)) > max_age:
        return False, f"webhook-timestamp is more than {max_age} s away from now: possible replay"
    signed = f"{message_id}.{timestamp}.".encode() + body
    digest = hmac.new(gitlab_signing_key(secret), signed, hashlib.sha256).digest()
    expected = "v1," + base64.b64encode(digest).decode()
    if any(hmac.compare_digest(expected, candidate) for candidate in signatures.split()):
        return True, "signature valid"
    return False, "signature mismatch"


def verify_hex_signature(received: Optional[str], prefix: str, body: bytes, secret: str) -> Tuple[bool, str]:
    if not received:
        return False, "no signature header"
    expected = prefix + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if hmac.compare_digest(expected, received.strip()):
        return True, "signature valid"
    return False, "signature mismatch"


def delivery_id(forge: str, headers: Dict[str, str]) -> Optional[str]:
    names = {
        "gitlab": ("webhook-id", "idempotency-key"),
        "github": ("x-github-delivery",),
        "forgejo": ("x-forgejo-delivery", "x-gitea-delivery"),
    }[forge]
    return next((headers[name] for name in names if name in headers), None)


def verify(forge: str, headers: Dict[str, str], body: bytes, secret: str, now: int, max_age: int) -> Tuple[bool, str]:
    if forge == "gitlab":
        return verify_gitlab(headers, body, secret, now, max_age)
    if forge == "github":
        return verify_hex_signature(headers.get("x-hub-signature-256"), "sha256=", body, secret)
    received = headers.get("x-forgejo-signature") or headers.get("x-gitea-signature")
    return verify_hex_signature(received, "", body, secret)


def load_headers(path: str) -> Dict[str, str]:
    with open(path, encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("headers file must hold a JSON object of header name to value")
    return header_lookup(loaded)


def command_verify(arguments: argparse.Namespace) -> int:
    secret = os.environ.get(arguments.secret_env)
    if not secret:
        print(f"error: environment variable {arguments.secret_env} is empty or unset", file=sys.stderr)
        return EXIT_USAGE
    headers = load_headers(arguments.headers)
    with open(arguments.body, "rb") as handle:
        body = handle.read()
    now = arguments.now if arguments.now is not None else int(time.time())
    valid, reason = verify(arguments.forge, headers, body, secret, now, arguments.max_age)
    report = {
        "forge": arguments.forge,
        "valid": valid,
        "reason": reason,
        "delivery_id": delivery_id(arguments.forge, headers),
    }
    print(json.dumps(report))
    return EXIT_VALID if valid else EXIT_INVALID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge_safety.py",
        description="Neutralise untrusted text before a forge write; verify a captured webhook delivery.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    neutralise_parser = commands.add_parser(
        "neutralise",
        help="escape quick-action lines, break @mentions and closing keywords outside code fences",
    )
    neutralise_parser.add_argument("file", nargs="?", help="input file; stdin when omitted")
    neutralise_parser.add_argument("--json", action="store_true", help="print the text and the rules that fired as JSON")
    neutralise_parser.set_defaults(handler=command_neutralise)

    verify_parser = commands.add_parser("verify", help="check a captured webhook delivery's signature")
    verify_parser.add_argument("--forge", choices=("gitlab", "github", "forgejo"), required=True)
    verify_parser.add_argument("--headers", required=True, help="JSON object of the delivery's headers")
    verify_parser.add_argument("--body", required=True, help="the raw request body, byte for byte")
    verify_parser.add_argument("--secret-env", default="WEBHOOK_SECRET", help="environment variable holding the secret")
    verify_parser.add_argument("--max-age", type=int, default=DEFAULT_MAX_AGE_SECONDS, help="GitLab timestamp tolerance in seconds")
    verify_parser.add_argument("--now", type=int, help="Unix time to check the GitLab timestamp against")
    verify_parser.set_defaults(handler=command_verify)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        return arguments.handler(arguments)
    except (OSError, ValueError, binascii.Error) as error:
        print(f"error: {error}", file=sys.stderr)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())

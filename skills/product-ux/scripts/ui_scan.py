#!/usr/bin/env python3
"""Scan product-interface source for broken accessibility floors, form and feedback failures, deceptive patterns and unhelpful copy.

Usage:
    ui_scan.py [--json] [--fail-on fail|warn|note|never] PATH [PATH ...]

PATH is a file or a directory (walked for HTML, CSS, JS, TS, JSX, TSX, Vue,
Svelte, Astro and server-template sources; node_modules, dist and build output
are skipped). Findings are per tag or per line, except project rules that judge
the whole set at once: a focus ring removed with no :focus-visible replacement
anywhere, motion with no reduced-motion branch anywhere, toast markup with no
live region anywhere, and raw colors sprawling outside token files. Only native
lowercase elements are judged; a capitalised component is assumed to own its
own semantics. Exit status 1 when a finding at or above --fail-on exists
(default: fail). The scan reads source; it never replaces a rendered check or
a test with people.
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".njk", ".liquid", ".twig", ".php", ".erb", ".hbs", ".blade.php"}
SKIPPED_DIRECTORIES = {"node_modules", "dist", "build", ".next", ".nuxt", ".svelte-kit", ".astro", "vendor", ".git", "coverage", "storybook-static"}
SEVERITY_RANK = {"fail": 3, "warn": 2, "note": 1, "never": 99}
MINIMUM_TARGET_PX = 24
IOS_ZOOM_THRESHOLD_PX = 16
RAW_COLOR_BUDGET = 16
TAG_SCAN_LIMIT = 4000
TOKEN_FILE = re.compile(r"token|theme|palette|variables|colors|design-system", re.I)
FIELD_TAGS = {"input", "select", "textarea"}
UNLABELLED_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}
FOCUSABLE_TAGS = {"a", "button", "input", "select", "textarea", "summary"}
NON_CONTROL_TAGS = {"div", "span", "li", "td", "tr", "p", "section", "article", "img", "svg", "label", "header", "footer", "main", "ul"}
TOAST_LIBRARIES = re.compile(r"""from\s+['"](sonner|react-hot-toast|react-toastify|notistack|@radix-ui/react-toast|vue-toastification|svelte-french-toast|@zag-js/toast|@ark-ui/\w+)['"]|useToast\(""")


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str


@dataclass(frozen=True)
class LineRule:
    rule: str
    severity: str
    pattern: re.Pattern
    message: str


@dataclass(frozen=True)
class Tag:
    name: str
    attributes: str
    start: int
    end: int


LINE_RULES = [
    LineRule("zoom-blocked", "fail", re.compile(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0+)?\b", re.I),
             "viewport blocks pinch zoom; WCAG 1.4.4 and 1.4.10 need it"),
    LineRule("positive-tabindex", "fail", re.compile(r"tabindex\s*=\s*[\"'{]?\s*[1-9]", re.I),
             "positive tabindex overrides the DOM order and scrambles keyboard navigation (WCAG 2.4.3); fix the source order"),
    LineRule("paste-blocked", "fail", re.compile(r"onpaste\s*=\s*[\"']\s*return\s+false|onPaste\s*=\s*\{[^}]*preventDefault|addEventListener\(\s*['\"]paste['\"].*preventDefault", re.I),
             "blocking paste breaks password managers and fails WCAG 3.3.8 Accessible Authentication; let people paste"),
    LineRule("placeholder-copy", "fail", re.compile(r"\blorem ipsum\b|\b(john|jane) (doe|smith)\b|\bacme (inc|corp)\b|\bfoo@bar\.com\b", re.I),
             "placeholder copy or people; real content changes widths, wrapping and states"),
    LineRule("confirmshaming", "warn", re.compile(r"\bno,? thanks?,? i (don'?t|do not) (want|like|need|care)\b|\bi (prefer|'d rather|would rather) (to )?(pay full price|miss out|stay uninformed|not save)\b", re.I),
             "decline option shames the user; confirmshaming is a catalogued deceptive pattern (DSA art. 25); label the choice neutrally"),
    LineRule("vague-error-copy", "warn", re.compile(r"\bsomething went wrong\b|\ban? (unknown |unexpected )?error (has )?occurred\b|\binvalid (input|value|data|entry)\b|\boops[!,.]", re.I),
             "error copy names no cause and no fix; say what happened, why, and what to do next (WCAG 3.3.1, 3.3.3)"),
    LineRule("ambiguous-link-text", "warn", re.compile(r">\s*(click here|here|read more|learn more|more)\s*</a>", re.I),
             "link text that means nothing out of context fails WCAG 2.4.4 in link lists; name the destination"),
    LineRule("native-blocking-dialog", "warn", re.compile(r"\bwindow\.(alert|confirm|prompt)\s*\(|(^|[^\w.$])(alert|confirm|prompt)\s*\(\s*['\"`]"),
             "blocking native dialog; prefer undo for reversible actions or an in-page dialog that names the consequence"),
    LineRule("hardcoded-format", "warn", re.compile(r"""["'](MM/DD/YYYY|MM/dd/yyyy|DD/MM/YYYY|dd/MM/yyyy|mm/dd/yyyy|YYYY-MM-DD HH:mm)["']|["'][$€£]["']\s*\+|\+\s*["'][$€£]["']"""),
             "hand-built date or money format; use Intl.DateTimeFormat or Intl.NumberFormat with the user's locale"),
    LineRule("generic-action-label", "note", re.compile(r"<button\b[^>]*>\s*(submit|ok|okay|go|yes|no|send)\s*</button>", re.I),
             "button says nothing about its result; label it with the verb and object (Save changes, Delete 3 invoices)"),
    LineRule("are-you-sure", "note", re.compile(r"\bare you sure\b", re.I),
             "an 'are you sure' confirmation is clicked through by habit; offer undo for reversible actions, and name the consequence for irreversible ones"),
    LineRule("naive-plural", "note", re.compile(r"""["'`][^"'`\n]*\w\(s\)[^"'`\n]*["'`]"""),
             "'item(s)' style plural; use Intl.PluralRules or ICU messages, because many languages have more than two plural forms"),
    LineRule("z-index-escalation", "note", re.compile(r"z-index\s*:\s*\d{4,}|\bz-\[\d{4,}\]", re.I),
             "z-index arms race; define a small named layer scale (base, dropdown, sticky, overlay, toast) as tokens"),
    LineRule("truncation-hides-content", "note", re.compile(r"text-overflow\s*:\s*ellipsis|class(Name)?\s*=\s*[\"'{][^\"'}]*\b(truncate|line-clamp-\d)\b", re.I),
             "truncated text must stay reachable (full text on focus, expand, or a detail view); a title attribute alone is not keyboard or touch accessible"),
]

TAG_START = re.compile(r"<([a-zA-Z][\w.:-]*)\b")
CLICK_HANDLER = re.compile(r"(?<![\w-])(onClick|onclick|@click|on:click|v-on:click|\(click\))\s*=")
HOVER_HANDLER = re.compile(r"(?<![\w-])(onMouseEnter|onMouseOver|onmouseover|onmouseenter|@mouseenter|@mouseover|on:mouseenter|on:mouseover)\s*=")
FOCUS_HANDLER = re.compile(r"(?<![\w-])(onFocus|onfocus|@focus|on:focus|onFocusCapture|focusin)\b")
LABEL_FOR = re.compile(r"(?<![\w-])(for|htmlFor)\s*=\s*[\"'{]\s*[\"']?([\w:.-]+)")
CONSENT_CONTEXT = re.compile(r"consent|newsletter|marketing|subscribe|agree|terms|privacy|offers|partners", re.I)
IOS_ZOOM_CLASSES = re.compile(r"\btext-(xs|sm|\[1[0-5]px\])\b")
SAFE_INPUT_CLASS = re.compile(r"(?<![\w:-])text-(base|lg|xl|\[1[6-9]px\]|\[[2-9]\dpx\])\b")
CSS_BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}")
FONT_SIZE_PX = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)(px|rem|em)\b", re.I)
SIZE_PX = re.compile(r"(?<![\w-])(width|height)\s*:\s*(\d+(?:\.\d+)?)px", re.I)
MIN_SIZE_OK = re.compile(r"min-(width|height)\s*:\s*(2[4-9]|[3-9]\d|\d{3,})px|min-(width|height)\s*:\s*(1\.[5-9]|[2-9])(\.\d+)?rem", re.I)
TARGET_SELECTOR = re.compile(r"button|\bbtn\b|icon|close|toggle|\[role=.?button|checkbox|radio|chip|tab\b", re.I)
FIELD_SELECTOR = re.compile(r"(^|[\s,>+~])(input|select|textarea)\b", re.I)
HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
FINE_POINTER_MEDIA = re.compile(r"@media[^{]*(pointer\s*:\s*fine|hover\s*:\s*hover)", re.I)
OUTLINE_REMOVED = re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b", re.I)
FOCUS_VISIBLE = re.compile(r":focus-visible|focus-visible:", re.I)
MOTION_PRESENT = re.compile(r"@keyframes|animation\s*:|animation-name|animation-timeline|::view-transition|startViewTransition|\.animate\(|\bgsap\b|framer-motion|\bmotion/react\b|scroll-behavior\s*:\s*smooth", re.I)
REDUCED_MOTION_BRANCH = re.compile(r"prefers-reduced-motion|useReducedMotion|motion-safe:|motion-reduce:|MotionConfig[^>]*reducedMotion", re.I)
TOAST_MARKUP = re.compile(r"class(Name)?\s*=\s*[\"'{][^\"'}]*\b(toast|snackbar)\b", re.I)
PROPS_SPREAD = re.compile(r"\{\s*\.\.\.\s*\w+\s*\}|v-bind\s*=|\$\$restProps|\{\.\.\.\$\$props\}")
VISUALLY_ABSENT = re.compile(r"(?<![\w-])hidden(?![\w-])|display\s*:\s*['\"]?none", re.I)
BACKDROP = re.compile(r"backdrop|overlay|scrim|\binset-0\b", re.I)
PROPAGATION_GUARD = re.compile(r"(onClick|onclick|@click|on:click)\s*=\s*\{?\s*\(?\s*\w*\s*\)?\s*=>\s*\w+\.stopPropagation\(\)\s*\}?|@click\.stop\b|on:click\|stopPropagation", re.I)
LIVE_REGION = re.compile(r"aria-live|role\s*=\s*[\"'{]\s*[\"']?(status|alert|log)\b|<output\b", re.I)


def source_files(paths):
    for raw in paths:
        root = Path(raw)
        if root.is_file():
            yield root
            continue
        for candidate in sorted(root.rglob("*")):
            if SKIPPED_DIRECTORIES.intersection(candidate.relative_to(root).parts):
                continue
            if candidate.is_file() and candidate.suffix.lower() in SOURCE_SUFFIXES and ".min." not in candidate.name:
                yield candidate


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def opening_tags(text):
    for start in TAG_START.finditer(text):
        index, depth, quote, limit = start.end(), 0, None, min(len(text), start.end() + TAG_SCAN_LIMIT)
        while index < limit:
            char = text[index]
            if quote:
                quote = None if char == quote else quote
            elif char in "\"'`":
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            elif char == ">" and depth <= 0:
                yield Tag(start.group(1), text[start.end():index], start.start(), index + 1)
                break
            index += 1


def has_attribute(tag, *names):
    return any(re.search(rf"(?<![\w-]){re.escape(name)}(?=[\s=/>]|$)", tag.attributes, re.I) for name in names)


def attribute_value(tag, name):
    match = re.search(rf"(?<![\w-]){re.escape(name)}\s*=\s*(\"([^\"]*)\"|'([^']*)'|\{{([^}}]*)\}})", tag.attributes, re.I)
    if not match:
        return None
    return next(group for group in match.groups()[1:] if group is not None)


def is_wrapped_in_label(text, offset):
    return text.rfind("<label", 0, offset) > text.rfind("</label", 0, offset)


def element_content(text, tag):
    closing = text.find(f"</{tag.name}>", tag.end)
    return text[tag.end:closing] if closing != -1 else ""


def has_accessible_name(tag):
    return has_attribute(tag, "aria-label", "aria-labelledby", "title")


def field_findings(name, text, tag, labelled_ids):
    if tag.name not in FIELD_TAGS:
        return []
    findings = []
    input_type = (attribute_value(tag, "type") or "text").lower()
    if tag.name == "input" and input_type in UNLABELLED_INPUT_TYPES:
        return findings
    if PROPS_SPREAD.search(tag.attributes) or VISUALLY_ABSENT.search(tag.attributes):
        return findings
    field_id = attribute_value(tag, "id")
    labelled = has_attribute(tag, "aria-label", "aria-labelledby") or (field_id in labelled_ids) or is_wrapped_in_label(text, tag.start)
    line = line_of(text, tag.start)
    if not labelled and input_type not in {"checkbox", "radio"}:
        if has_attribute(tag, "placeholder"):
            findings.append(Finding(name, line, "placeholder-as-label", "fail", "placeholder stands in for a label; it vanishes on input, fails contrast and is not a reliable accessible name (WCAG 1.3.1, 3.3.2)"))
        else:
            findings.append(Finding(name, line, "unlabelled-field", "fail", "form field has no programmatic label; use <label for>, a wrapping <label> or aria-labelledby (WCAG 1.3.1, 4.1.2)"))
    if attribute_value(tag, "autocomplete") in {"off", "nope", "false"}:
        findings.append(Finding(name, line, "autocomplete-off", "warn", "autocomplete off defeats autofill and password managers; set the matching token (email, current-password, postal-code) per WCAG 1.3.5"))
    class_value = attribute_value(tag, "class") or attribute_value(tag, "className") or ""
    if IOS_ZOOM_CLASSES.search(class_value) and not SAFE_INPUT_CLASS.search(class_value):
        findings.append(Finding(name, line, "input-font-zoom", "warn", f"field text under {IOS_ZOOM_THRESHOLD_PX}px makes iOS Safari zoom on focus; use 16px on touch and step down from a breakpoint"))
    if input_type == "checkbox" and has_attribute(tag, "checked", "defaultChecked"):
        window = text[max(0, tag.start - 300):tag.end + 300]
        if CONSENT_CONTEXT.search(window):
            findings.append(Finding(name, line, "prechecked-consent", "fail", "pre-ticked consent is not consent (GDPR art. 4(11), CJEU Planet49 C-673/17); start unchecked"))
    return findings


def control_findings(name, text, tag, has_form):
    findings = []
    line = line_of(text, tag.start)
    if tag.name == "img" and not has_attribute(tag, "alt"):
        findings.append(Finding(name, line, "img-no-alt", "fail", "image without alt; describe it, or alt=\"\" when it is decorative (WCAG 1.1.1)"))
    if tag.name == "html" and not has_attribute(tag, "lang"):
        findings.append(Finding(name, line, "missing-lang", "warn", "<html> without lang; screen readers guess the pronunciation (WCAG 3.1.1)"))
    if tag.name == "button":
        content = element_content(text, tag)
        visible_text = re.sub(r"<[^>]*>", "", content).strip()
        graphic = re.search(r"<svg\b|<i\b|<img\b|Icon\b", content)
        named_image = re.search(r"\balt\s*=\s*[\"'][^\"']+[\"']", content)
        if graphic and not visible_text and not named_image and not has_accessible_name(tag):
            findings.append(Finding(name, line, "icon-button-no-name", "fail", "icon-only button has no accessible name; add aria-label or visually hidden text (WCAG 4.1.2), and a visible label where the icon is not universal"))
        if has_form and not has_attribute(tag, "type"):
            findings.append(Finding(name, line, "button-without-type", "note", "a <button> in a form defaults to type=submit; declare type=button for anything that is not the submit"))
        if is_submit_disabled(tag):
            findings.append(Finding(name, line, "disabled-submit", "warn", "disabled submit hides why nothing happens; keep it enabled and explain the errors on submit"))
    if tag.name == "input" and (attribute_value(tag, "type") or "").lower() == "submit" and is_submit_disabled(tag, assume_submit=True):
        findings.append(Finding(name, line, "disabled-submit", "warn", "disabled submit hides why nothing happens; keep it enabled and explain the errors on submit"))
    if tag.name in NON_CONTROL_TAGS and CLICK_HANDLER.search(tag.attributes) and not BACKDROP.search(tag.attributes) and not PROPAGATION_GUARD.search(tag.attributes):
        if not has_attribute(tag, "role") or not has_attribute(tag, "tabindex", "tabIndex"):
            findings.append(Finding(name, line, "clickable-non-control", "fail", f"<{tag.name}> with a click handler is unreachable by keyboard and unnamed to assistive tech; use <button> or <a href> (WCAG 2.1.1, 4.1.2)"))
    if tag.name == "a":
        href = attribute_value(tag, "href")
        if href in {"#", ""} or (href or "").lower().startswith("javascript:") or (href is None and CLICK_HANDLER.search(tag.attributes)):
            findings.append(Finding(name, line, "link-as-button", "warn", "a link that goes nowhere is a button in disguise; use <button> for actions and <a href> for navigation"))
    focusable = tag.name in FOCUSABLE_TAGS or re.search(r"tabindex\s*=\s*[\"'{]?\s*0", tag.attributes, re.I)
    if focusable and re.search(r"aria-hidden\s*=\s*[\"'{]\s*[\"']?true", tag.attributes, re.I):
        findings.append(Finding(name, line, "aria-hidden-focusable", "fail", "focusable element hidden from assistive tech; keyboard users land on something that announces nothing (WCAG 4.1.2)"))
    if HOVER_HANDLER.search(tag.attributes) and not FOCUS_HANDLER.search(tag.attributes):
        findings.append(Finding(name, line, "hover-only-interaction", "warn", "hover handler with no focus equivalent; keyboard and touch users never see it (WCAG 2.1.1, 1.4.13)"))
    if has_attribute(tag, "autofocus", "autoFocus"):
        findings.append(Finding(name, line, "autofocus-steals-context", "note", "autofocus skips the page context for screen-reader users and pops the mobile keyboard; use it only where the field is the whole purpose of the view"))
    return findings


def is_submit_disabled(tag, assume_submit=False):
    submit = assume_submit or (attribute_value(tag, "type") or "").lower() == "submit"
    disabled = attribute_value(tag, "disabled")
    if disabled is not None and re.search(r"!\s*\w*(valid|dirty|complete|ready|canSubmit)", disabled, re.I):
        return True
    return submit and has_attribute(tag, "disabled") and disabled not in {"false", "{false}"}


def css_findings(name, text):
    findings = []
    for block in CSS_BLOCK.finditer(text):
        selector, body = block.group(1).strip().split(";")[-1], block.group(2)
        line = line_of(text, block.start(2))
        if FIELD_SELECTOR.search(selector):
            size = FONT_SIZE_PX.search(body)
            if size and to_px(float(size.group(1)), size.group(2)) < IOS_ZOOM_THRESHOLD_PX and not FINE_POINTER_MEDIA.search(enclosing_at_rule(text, block.start())):
                findings.append(Finding(name, line, "input-font-zoom", "warn", f"field text under {IOS_ZOOM_THRESHOLD_PX}px makes iOS Safari zoom on focus; use 16px on touch and step down from a breakpoint"))
        if TARGET_SELECTOR.search(selector) and not MIN_SIZE_OK.search(body):
            small = [value for _, value in SIZE_PX.findall(body) if float(value) < MINIMUM_TARGET_PX]
            if small:
                findings.append(Finding(name, line, "small-target", "warn", f"interactive target set to {min(small, key=float)}px; WCAG 2.5.8 needs {MINIMUM_TARGET_PX}x{MINIMUM_TARGET_PX} CSS px or equivalent spacing, and touch wants 44-48"))
    return findings


def enclosing_at_rule(text, offset):
    depth = 0
    for index in range(offset - 1, -1, -1):
        char = text[index]
        if char == "}":
            depth += 1
        elif char == "{":
            if depth == 0:
                prelude_start = max(text.rfind("}", 0, index), text.rfind(";", 0, index)) + 1
                return text[prelude_start:index]
            depth -= 1
    return ""


def to_px(value, unit):
    return value if unit.lower() == "px" else value * 16


def scan_text(path, text):
    name = str(path)
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for rule in LINE_RULES:
            if rule.pattern.search(line):
                findings.append(Finding(name, number, rule.rule, rule.severity, rule.message))
    labelled_ids = {match.group(2) for match in LABEL_FOR.finditer(text)}
    has_form = "<form" in text
    for tag in opening_tags(text):
        findings += field_findings(name, text, tag, labelled_ids)
        findings += control_findings(name, text, tag, has_form)
    if path.suffix.lower() in {".css", ".scss", ".sass", ".less", ".vue", ".svelte", ".astro", ".html", ".htm"}:
        findings += css_findings(name, text)
    return findings


def scan_project(texts):
    findings = []
    combined = "\n".join(texts.values())
    if not FOCUS_VISIBLE.search(combined):
        for path, text in texts.items():
            match = OUTLINE_REMOVED.search(text)
            if match:
                findings.append(Finding(str(path), line_of(text, match.start()), "focus-ring-removed", "fail", "outline removed with no :focus-visible replacement anywhere; WCAG 2.4.7"))
    if not REDUCED_MOTION_BRANCH.search(combined):
        for path, text in texts.items():
            match = MOTION_PRESENT.search(text)
            if match:
                findings.append(Finding(str(path), line_of(text, match.start()), "motion-without-reduced-motion", "warn", "motion ships with no prefers-reduced-motion branch anywhere; swap spatial motion for fades under reduce"))
    if not LIVE_REGION.search(combined) and not TOAST_LIBRARIES.search(combined):
        for path, text in texts.items():
            match = TOAST_MARKUP.search(text)
            if match:
                findings.append(Finding(str(path), line_of(text, match.start()), "status-without-live-region", "warn", "toast or snackbar markup with no aria-live or role=status anywhere; screen readers never hear it (WCAG 4.1.3)"))
    raw_colors = {}
    for path, text in texts.items():
        if TOKEN_FILE.search(path.name):
            continue
        for match in HEX_COLOR.finditer(text):
            raw_colors.setdefault(match.group(0).lower(), (path, line_of(text, match.start())))
    if len(raw_colors) > RAW_COLOR_BUDGET:
        path, line = next(iter(raw_colors.values()))
        findings.append(Finding(str(path), line, "raw-color-sprawl", "note", f"{len(raw_colors)} distinct raw colors outside token files; route them through semantic tokens (surface, text, border, accent, status)"))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default="fail")
    arguments = parser.parse_args()

    texts = {path: path.read_text(errors="ignore") for path in source_files(arguments.paths)}
    findings = [f for path, text in texts.items() for f in scan_text(path, text)] + scan_project(texts)
    findings.sort(key=lambda f: (-SEVERITY_RANK[f.severity], f.path, f.line, f.rule))

    if arguments.json:
        print(json.dumps({"files": len(texts), "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        for f in findings:
            print(f"{f.path}:{f.line}: {f.severity}: {f.rule}: {f.message}")
        counts = {s: sum(f.severity == s for f in findings) for s in ("fail", "warn", "note")}
        print(f"{len(texts)} files, {counts['fail']} fail, {counts['warn']} warn, {counts['note']} note", file=sys.stderr)

    threshold = SEVERITY_RANK[arguments.fail_on]
    sys.exit(1 if any(SEVERITY_RANK[f.severity] >= threshold for f in findings) else 0)


if __name__ == "__main__":
    main()

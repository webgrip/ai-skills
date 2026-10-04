#!/usr/bin/env python3
"""Scan a page's source for broken motion contracts, accessibility floors, generic-template tells and unproven claims.

Usage:
    design_scan.py [--json] [--fail-on fail|warn|note|never] PATH [PATH ...]

PATH is a file or a directory (walked for HTML, CSS, JS, TS, JSX, TSX, Vue,
Svelte and Astro sources; node_modules, dist and build output are skipped).
Findings are per line, except project rules that judge the whole set at once:
motion with no reduced-motion branch anywhere, a focus ring removed with no
:focus-visible replacement anywhere. Exit status 1 when a finding at or above
--fail-on exists (default: fail). The scan reads source; it never replaces a
rendered check.
"""

import argparse
import colorsys
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".njk", ".liquid", ".twig", ".php", ".erb", ".hbs"}
SKIPPED_DIRECTORIES = {"node_modules", "dist", "build", ".next", ".nuxt", ".svelte-kit", ".astro", "vendor", ".git", "coverage"}
SEVERITY_RANK = {"fail": 3, "warn": 2, "note": 1, "never": 99}
WILL_CHANGE_BUDGET = 3
BACKDROP_FILTER_BUDGET = 3
GENERIC_GRADIENT_HUES = (220.0, 300.0)
LAYOUT_PROPERTIES = ("top", "left", "right", "bottom", "width", "height", "margin", "padding", "inset", "font-size")
GENERIC_ONLY_FAMILIES = {"inter", "roboto", "arial", "helvetica", "helvetica neue", "system-ui", "-apple-system", "blinkmacsystemfont", "segoe ui", "sans-serif", "ui-sans-serif", "open sans", "poppins", "montserrat"}


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


LINE_RULES = [
    LineRule("zoom-blocked", "fail", re.compile(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0+)?\b", re.I),
             "viewport blocks pinch zoom; WCAG 1.4.4 and 1.4.10 need it"),
    LineRule("vw-only-type", "warn", re.compile(r"font-size\s*:\s*(clamp\([^,;]+,\s*)?[\d.]+vw\s*[,);]", re.I),
             "font size driven by vw alone ignores browser zoom (WCAG 1.4.4); write the preferred value as rem + vw"),
    LineRule("transition-all", "warn", re.compile(r"transition(-property)?\s*:\s*all\b", re.I),
             "transition: all animates layout properties by accident; name the properties"),
    LineRule("infinite-animation", "warn", re.compile(r"animation(-iteration-count)?\s*:[^;{}]*\binfinite\b", re.I),
             "endless motion beside content needs a pause control (WCAG 2.2.2) or a reduced-motion stop"),
    LineRule("full-viewport-vh", "note", re.compile(r"(min-)?height\s*:\s*100vh\b", re.I),
             "100vh overflows behind mobile browser bars; prefer 100svh or 100dvh with a vh fallback"),
    LineRule("scroll-hijack-library", "warn", re.compile(r"""from\s+['"](lenis|@studio-freight/lenis|locomotive-scroll|smooth-scrollbar|fullpage\.js)['"]|new\s+(Lenis|LocomotiveScroll)\s*\(""", re.I),
             "scroll smoothing library replaces native scroll; prove keyboard, find-in-page, anchors and reduced motion still work"),
    LineRule("wheel-prevent-default", "warn", re.compile(r"""addEventListener\(\s*['"](wheel|mousewheel|touchmove)['"].*?passive\s*:\s*false""", re.I),
             "non-passive wheel or touch listener; scrolljacking costs control and INP"),
    LineRule("placeholder-copy", "fail", re.compile(r"\blorem ipsum\b|\b(john|jane) (doe|smith)\b|\bacme (inc|corp)\b", re.I),
             "placeholder copy or people; real copy changes the composition"),
    LineRule("unsourced-multiplier", "warn", re.compile(r"\b\d+(\.\d+)?\s?[x×]\s+(faster|cheaper|more|better|less|quicker|productive)\b", re.I),
             "multiplier claim; needs a claim-ledger row with method, baseline and date"),
    LineRule("vague-social-proof", "warn", re.compile(r"\btrusted by (thousands|millions|hundreds|leading|the world'?s|top)\b|\bloved by (developers|teams|thousands|millions)\b|★★★★★", re.I),
             "unquantified social proof; name the source or cut it"),
    LineRule("fake-live-activity", "fail", re.compile(r"\b(people|users|others) (are )?(viewing|watching) (this|now)\b|\bjust (signed up|purchased|bought)\b|\busers online\b|\bonly \d+ left\b", re.I),
             "simulated live activity or scarcity is a dark pattern (EU UCPD Annex I, DSA art. 25); show real, labelled data or nothing"),
    LineRule("autoplay-audio", "fail", re.compile(r"<(video|audio)\b(?![^>]*\bmuted\b)[^>]*\bautoplay\b", re.I),
             "autoplaying media with sound; WCAG 1.4.2 needs muted or a control"),
]

EMOJI_IN_HEADING = re.compile(r"<h[1-6][^>]*>\s*[\U0001F300-\U0001FAFF☀-➿]", re.I)
VIDEO_TAG = re.compile(r"<video\b[^>]*>", re.I | re.S)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I | re.S)
FONT_FACE_BLOCK = re.compile(r"@font-face\s*{[^}]*}", re.I | re.S)
KEYFRAMES_START = re.compile(r"@keyframes\s+([\w-]+)\s*{", re.I)
GRADIENT = re.compile(r"(linear|radial|conic)-gradient\(([^;{}]*)\)", re.I)
HEX_COLOR = re.compile(r"#([0-9a-f]{6}|[0-9a-f]{3})\b", re.I)
FUNCTIONAL_RGB = re.compile(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)", re.I)
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;{}]+)", re.I)
TAILWIND_GENERIC_GRADIENT = re.compile(r"\bfrom-(indigo|violet|purple|blue|fuchsia)-\d{3}\b[^\"'`]*\bto-(indigo|violet|purple|pink|blue|fuchsia)-\d{3}\b")
OUTLINE_REMOVED = re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b", re.I)
MOTION_PRESENT = re.compile(r"@keyframes|animation\s*:|animation-name|animation-timeline|::view-transition|startViewTransition|\.animate\(|\bgsap\b|framer-motion|\bmotion/react\b|scroll-behavior\s*:\s*smooth", re.I)
REDUCED_MOTION_BRANCH = re.compile(r"prefers-reduced-motion|useReducedMotion|motion-safe:|motion-reduce:|MotionConfig[^>]*reducedMotion", re.I)
FOCUS_VISIBLE = re.compile(r":focus-visible|focus-visible:", re.I)
WILL_CHANGE = re.compile(r"will-change\s*:", re.I)
BACKDROP_FILTER = re.compile(r"backdrop-filter\s*:|\bbackdrop-blur(-\w+)?\b", re.I)


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


def hue_of(color_match):
    if color_match.re is HEX_COLOR:
        digits = color_match.group(1)
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        red, green, blue = (int(digits[i:i + 2], 16) for i in (0, 2, 4))
    else:
        red, green, blue = (int(color_match.group(i)) for i in (1, 2, 3))
    hue, _, saturation = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
    return hue * 360, saturation


def is_generic_gradient(stops):
    colors = list(HEX_COLOR.finditer(stops)) + list(FUNCTIONAL_RGB.finditer(stops))
    chromatic = [hue for hue, saturation in map(hue_of, colors) if saturation > 0.35]
    low, high = GENERIC_GRADIENT_HUES
    return len(chromatic) >= 2 and all(low <= hue <= high for hue in chromatic)


def keyframe_blocks(text):
    for start in KEYFRAMES_START.finditer(text):
        depth, index = 1, start.end()
        while index < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[index], 0)
            index += 1
        yield start, text[start.end():index]


def animates_layout(body):
    declared = {name.lower() for name in re.findall(r"([\w-]+)\s*:", body)}
    return sorted(p for p in LAYOUT_PROPERTIES if p in declared)


def scan_text(path, text):
    findings = []
    name = str(path)
    for number, line in enumerate(text.splitlines(), 1):
        for rule in LINE_RULES:
            if rule.pattern.search(line):
                findings.append(Finding(name, number, rule.rule, rule.severity, rule.message))
        if TAILWIND_GENERIC_GRADIENT.search(line):
            findings.append(Finding(name, number, "generic-gradient", "note", "indigo-to-violet utility gradient is the default template look; derive color from the subject"))
    for match in EMOJI_IN_HEADING.finditer(text):
        findings.append(Finding(name, line_of(text, match.start()), "emoji-heading-icon", "note", "emoji as heading icon reads as template; use the subject's own marks or none"))
    for match in VIDEO_TAG.finditer(text):
        tag = match.group(0).lower()
        if "autoplay" in tag and "controls" not in tag and "loop" in tag:
            findings.append(Finding(name, line_of(text, match.start()), "looping-video-no-control", "warn", "looping autoplay video needs a visible pause (WCAG 2.2.2) and a reduced-motion poster"))
    for match in IMG_TAG.finditer(text):
        tag = match.group(0).lower()
        if not re.search(r"\bwidth\s*=", tag) or not re.search(r"\bheight\s*=", tag):
            if "aspect-ratio" not in tag and not re.search(r"\bfill\b", tag):
                findings.append(Finding(name, line_of(text, match.start()), "img-no-dimensions", "warn", "image without width and height reserves no space and shifts layout (CLS)"))
    for match in FONT_FACE_BLOCK.finditer(text):
        if "font-display" not in match.group(0).lower():
            findings.append(Finding(name, line_of(text, match.start()), "font-face-no-display", "warn", "@font-face without font-display; choose swap or optional and size-adjust the fallback"))
    for start, body in keyframe_blocks(text):
        layout = animates_layout(body)
        if layout:
            findings.append(Finding(name, line_of(text, start.start()), "layout-keyframes", "warn", f"@keyframes {start.group(1)} animates {', '.join(layout)}; use transform and opacity"))
    for match in GRADIENT.finditer(text):
        if is_generic_gradient(match.group(2)):
            findings.append(Finding(name, line_of(text, match.start()), "generic-gradient", "note", "blue-violet gradient is the default template look; derive color from the subject"))
    for match in FONT_FAMILY.finditer(text):
        families = {f.strip().strip("'\"").lower() for f in match.group(1).split(",")}
        if families and families <= GENERIC_ONLY_FAMILIES and "var(" not in match.group(1) and "inherit" not in families:
            findings.append(Finding(name, line_of(text, match.start()), "default-type-only", "note", "only default sans families; give display type a voice or justify the neutral choice"))
    return findings


def scan_project(texts):
    findings = []
    combined = "\n".join(texts.values())
    if not REDUCED_MOTION_BRANCH.search(combined):
        for path, text in texts.items():
            match = MOTION_PRESENT.search(text)
            if match:
                findings.append(Finding(str(path), line_of(text, match.start()), "motion-without-reduced-motion", "fail", "motion ships with no prefers-reduced-motion branch anywhere in the scanned set"))
    if not FOCUS_VISIBLE.search(combined):
        for path, text in texts.items():
            match = OUTLINE_REMOVED.search(text)
            if match:
                findings.append(Finding(str(path), line_of(text, match.start()), "focus-ring-removed", "fail", "outline removed with no :focus-visible replacement anywhere; WCAG 2.4.7"))
    for counter, budget, rule, message in (
        (WILL_CHANGE, WILL_CHANGE_BUDGET, "will-change-sprawl", "will-change on more than {budget} rules; promote layers only where a profile shows it helps"),
        (BACKDROP_FILTER, BACKDROP_FILTER_BUDGET, "glass-everywhere", "backdrop blur on more than {budget} rules; frosted glass as a default surface reads as template and costs paint"),
    ):
        hits = [(path, text, m) for path, text in texts.items() for m in counter.finditer(text)]
        if len(hits) > budget:
            path, text, first = hits[0]
            findings.append(Finding(str(path), line_of(text, first.start()), rule, "warn" if rule == "will-change-sprawl" else "note", message.format(budget=budget) + f" ({len(hits)} found)"))
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

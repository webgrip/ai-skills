#!/usr/bin/env python3
"""Audit a static site's build output and live edge for what makes Core Web Vitals good or bad.

Usage:
    perf_scan.py site PATH [--js-budget-kb N] [--css-budget-kb N] [--hero-budget-kb N] [--json] [--fail-on fail|warn|note|never]
    perf_scan.py live URL [--field] [--form-factor phone|desktop] [--timeout S] [--json] [--fail-on ...]

site: PATH is a repository with a wrangler config (its assets.directory is
scanned) or a build directory. Every page's likely LCP image, image and embed
dimensions, render-blocking scripts, fonts, JavaScript and CSS weight
(gzip-measured, as transferred), third parties and back/forward-cache
blockers are judged from the files, together with _headers.

live: measures time to first byte over three requests, compression, HTTP/3,
caching of HTML and hashed assets, and with --field reads the 75th-percentile
field data for the URL and its origin from the CrUX API (set CRUX_API_KEY; a
free key from the Google Cloud console). Missing field data is reported as
missing, never as passing. Exit status 1 when a finding at or above
--fail-on exists (default: fail). The scan reads files and responses; it is
not a browser trace, and only field data shows what real users get.
"""

import argparse
import gzip
import http.client
import json
import os
import re
import socket
import ssl
import statistics
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path

CONFIG_NAMES = ("wrangler.jsonc", "wrangler.json", "wrangler.toml")
SEVERITY_RANK = {"fail": 3, "warn": 2, "note": 1, "never": 99}
LCP_CANDIDATE_MIN_BYTES = 20 * 1024
LCP_CANDIDATE_MIN_WIDTH = 300
LEGACY_FORMAT_MIN_BYTES = 50 * 1024
IMAGE_HEAVY_BYTES = 300 * 1024
FONT_PRELOAD_LIMIT = 2
DOM_ELEMENT_LIMIT = 1500
TTFB_GOOD_MS = 800
LIVE_SAMPLES = 3
IMMUTABLE_MIN_AGE = 31536000
CRUX_ENDPOINT = os.environ.get("CRUX_ENDPOINT", "https://chromeuxreport.googleapis.com/v1/records:queryRecord")
BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
MODERN_IMAGE = re.compile(r"\.(avif|webp)(\?|$|\s)", re.I)
LEGACY_IMAGE = re.compile(r"\.(jpe?g|png)(\?|$)", re.I)
HASHED_NAME = re.compile(r"(?:[.-]([A-Za-z0-9_-]{8})|\.([0-9a-f]{16,}))\.(js|css|woff2?|avif|webp|png|jpe?g|svg)$")
TINY_BLOCKING_SCRIPT_BYTES = 1536
FONT_FACE = re.compile(r"@font-face\s*{([^}]*)}", re.I | re.S)
UNLOAD_LISTENER = re.compile(r"""addEventListener\(\s*['"]unload['"]|\bonunload\s*=|window\.onunload""")
THIRD_PARTY_FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "use.typekit.net", "fonts.bunny.net")
HEAVY_THIRD_PARTIES = {
    "googletagmanager.com": "Google Tag Manager",
    "google-analytics.com": "Google Analytics",
    "connect.facebook.net": "Meta Pixel",
    "static.hotjar.com": "Hotjar",
    "widget.intercom.io": "Intercom",
    "js.hs-scripts.com": "HubSpot",
    "cdn.cookielaw.org": "OneTrust",
    "consent.cookiebot.com": "Cookiebot",
    "www.youtube.com": "YouTube",
    "player.vimeo.com": "Vimeo",
    "maps.googleapis.com": "Google Maps",
    "embed.tawk.to": "Tawk.to",
    "snap.licdn.com": "LinkedIn Insight",
}
EMBED_HOSTS = ("youtube.com", "youtube-nocookie.com", "vimeo.com", "google.com/maps", "maps.google", "spotify.com", "twitter.com", "x.com")
FIELD_METRICS = {
    "largest_contentful_paint": ("LCP", 2500, 4000, lambda v: f"{v / 1000:.1f} s"),
    "interaction_to_next_paint": ("INP", 200, 500, lambda v: f"{v:.0f} ms"),
    "cumulative_layout_shift": ("CLS", 0.1, 0.25, lambda v: f"{v:.2f}"),
    "experimental_time_to_first_byte": ("TTFB", 800, 1800, lambda v: f"{v / 1000:.1f} s"),
}


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str
    also: list = field(default_factory=list)


@dataclass
class Element:
    tag: str
    attributes: dict
    line: int
    in_head: bool
    order: int


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements: list[Element] = []
        self.inline_scripts: list[tuple[str, int]] = []
        self.inline_styles: list[tuple[str, int]] = []
        self.in_head = False
        self.capture: list | None = None
        self.element_count = 0

    def handle_starttag(self, tag, attrs):
        attributes = {name.lower(): (value or "") for name, value in attrs}
        line = self.getpos()[0]
        self.element_count += 1
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
        if tag in ("img", "script", "link", "iframe", "video", "source", "picture", "astro-island"):
            self.elements.append(Element(tag, attributes, line, self.in_head, len(self.elements)))
        if tag == "script" and "src" not in attributes and attributes.get("type", "") not in ("application/ld+json", "application/json", "speculationrules", "importmap"):
            self.capture = ["script", line, []]
        elif tag == "style":
            self.capture = ["style", line, []]

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if self.capture and tag == self.capture[0]:
            text = "".join(self.capture[2])
            (self.inline_scripts if tag == "script" else self.inline_styles).append((text, self.capture[1]))
            self.capture = None

    def handle_data(self, data):
        if self.capture:
            self.capture[2].append(data)


def strip_jsonc(text: str) -> str:
    out, i, n, in_string = [], 0, len(text), False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            in_string = ch != '"'
            i += 1
        elif ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i)
            i = n if end == -1 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(ch)
            i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def locate_root(path: Path) -> tuple[Path | None, list[Finding]]:
    for name in CONFIG_NAMES:
        config_path = path / name
        if not config_path.exists():
            continue
        text = config_path.read_text()
        config = tomllib.loads(text) if config_path.suffix == ".toml" else json.loads(strip_jsonc(text))
        directory = (config.get("assets") or {}).get("directory") or config.get("pages_build_output_dir")
        if not directory:
            break
        root = (path / directory).resolve()
        if not root.is_dir():
            return None, [Finding(str(config_path), 0, "build-missing", "fail", f"assets directory {root} does not exist; build first, then scan")]
        return root, []
    return path.resolve(), []


def gzip_size(data: bytes) -> int:
    return len(gzip.compress(data, compresslevel=6))


class Report:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[Finding] = []

    def add(self, path, line: int, rule: str, severity: str, message: str):
        label = str(path.relative_to(self.root)) if isinstance(path, Path) and path.is_relative_to(self.root) else str(path)
        self.findings.append(Finding(label, line, rule, severity, message))


class Site:
    def __init__(self, root: Path):
        self.root = root
        self.css_cache: dict[Path, str] = {}

    def local_file(self, page: Path, reference: str) -> Path | None:
        parts = urllib.parse.urlsplit(reference)
        if parts.scheme or parts.netloc or not parts.path:
            return None
        relative = page.parent.relative_to(self.root).as_posix()
        base = "/" + (relative + "/" if relative != "." else "")
        resolved = urllib.parse.urljoin(base, urllib.parse.unquote(parts.path))
        candidate = (self.root / resolved.lstrip("/")).resolve()
        return candidate if candidate.is_file() and candidate.is_relative_to(self.root) else None

    def css_text(self, file: Path) -> str:
        if file not in self.css_cache:
            self.css_cache[file] = file.read_text(errors="replace")
        return self.css_cache[file]


def host_of(reference: str) -> str:
    return (urllib.parse.urlsplit(reference).hostname or "").lower()


def is_true(attributes: dict, name: str) -> bool:
    return name in attributes


def declared_width(attributes: dict) -> int:
    match = re.match(r"\s*(\d+)", attributes.get("width", ""))
    return int(match.group(1)) if match else 0


def has_dimensions(attributes: dict) -> bool:
    style = attributes.get("style", "").lower()
    return ("width" in attributes and "height" in attributes) or "aspect-ratio" in style or ("width" in style and "height" in style)


def modern_alternative(image: Element, elements: list[Element]) -> bool:
    if MODERN_IMAGE.search(image.attributes.get("srcset", "")) or MODERN_IMAGE.search(image.attributes.get("src", "")):
        return True
    sources = [el for el in elements[max(0, image.order - 6):image.order] if el.tag == "source"]
    return any("avif" in el.attributes.get("type", "") or "webp" in el.attributes.get("type", "") or MODERN_IMAGE.search(el.attributes.get("srcset", "")) for el in sources)


def lcp_candidate(page: Path, images: list[Element], site: Site) -> Element | None:
    for image in images:
        if image.attributes.get("fetchpriority", "").lower() == "high":
            return image
    for image in images:
        file = site.local_file(page, image.attributes.get("src", ""))
        size = file.stat().st_size if file else 0
        if declared_width(image.attributes) >= LCP_CANDIDATE_MIN_WIDTH or size >= LCP_CANDIDATE_MIN_BYTES:
            return image
    return None


def check_page(page: Path, site: Site, budgets: dict, report: Report):
    parser = PageParser()
    parser.feed(page.read_text(errors="replace"))
    parser.close()
    elements = parser.elements
    images = [el for el in elements if el.tag == "img" and not el.in_head]
    preloads = [el for el in elements if el.tag == "link" and "preload" in el.attributes.get("rel", "").lower().split()]

    candidate = lcp_candidate(page, images, site)
    if candidate:
        source = candidate.attributes.get("src", "")
        file = site.local_file(page, source)
        size = file.stat().st_size if file else 0
        if candidate.attributes.get("loading", "").lower() == "lazy":
            contradiction = candidate.attributes.get("fetchpriority", "").lower() == "high"
            report.add(page, candidate.line, "lcp-image-lazy", "fail" if contradiction else "warn",
                       f"{source} is lazy-loaded{' despite fetchpriority=high' if contradiction else ' and is the first large image on the page'}; "
                       "if it is above the fold the browser waits for layout before fetching it, which delays LCP. Lazy-load only images below the fold")
        preloaded = any(el.attributes.get("href", "") == source or el.attributes.get("imagesrcset") for el in preloads if el.attributes.get("as") == "image")
        if candidate.attributes.get("fetchpriority", "").lower() != "high" and not preloaded:
            report.add(page, candidate.line, "lcp-image-not-prioritized", "note",
                       f"{source} is the first large image and has no fetchpriority=\"high\" or image preload; if it is the LCP element, give it fetchpriority=\"high\"")
        if size > budgets["hero"]:
            report.add(page, candidate.line, "lcp-image-heavy", "note",
                       f"the first large image {source} is {size // 1024} KB; aim for {budgets['hero'] // 1024} KB or less with AVIF/WebP and srcset. Fix discovery and priority first: on slow origins the download is under 10 % of LCP")
        if file and LEGACY_IMAGE.search(source) and size > LEGACY_FORMAT_MIN_BYTES and not modern_alternative(candidate, elements):
            report.add(page, candidate.line, "lcp-image-legacy-format", "note",
                       f"the likely LCP image {source} is JPEG/PNG with no AVIF or WebP alternative; AVIF is typically far smaller at the same quality")
    for image in images:
        if image is images[0] and not image.attributes.get("src") and (image.attributes.get("data-src") or image.attributes.get("data-srcset")):
            report.add(page, image.line, "lcp-image-js-loaded", "warn",
                       "the first image has only data-src: a script loads it, so the browser's preload scanner can't start it early. Use a real src and native loading")
        if re.search(r"\d+w\b", image.attributes.get("srcset", "")) and not image.attributes.get("sizes"):
            report.add(page, image.line, "srcset-without-sizes", "warn",
                       f"<img src=\"{image.attributes.get('src', '')[:60]}\"> has a width-based srcset but no sizes; the browser assumes 100vw and downloads a larger file than shown")
        if not has_dimensions(image.attributes):
            report.add(page, image.line, "img-dimensions-missing", "warn",
                       f"<img src=\"{image.attributes.get('src', '')[:60]}\"> has no width and height (or aspect-ratio); the page shifts when it loads (CLS)")
        if image is candidate:
            continue
        file = site.local_file(page, image.attributes.get("src", ""))
        if file and file.stat().st_size > IMAGE_HEAVY_BYTES:
            report.add(page, image.line, "image-heavy", "note",
                       f"{image.attributes.get('src')} is {file.stat().st_size // 1024} KB; resize to the displayed size, serve AVIF/WebP, add srcset")

    for element in elements:
        if element.tag in ("iframe", "video") and not has_dimensions(element.attributes):
            report.add(page, element.line, "embed-dimensions-missing", "warn",
                       f"<{element.tag}> without width and height (or aspect-ratio) shifts the layout when it loads")
        if element.tag == "iframe" and any(embed in element.attributes.get("src", "") for embed in EMBED_HOSTS) and element.attributes.get("loading", "").lower() != "lazy":
            report.add(page, element.line, "embed-not-lazy", "warn",
                       f"embed {element.attributes.get('src', '')[:60]} loads eagerly; use loading=\"lazy\" or a click-to-load facade")

    for island in (el for el in elements if el.tag == "astro-island" and el.attributes.get("client") == "only"):
        report.add(page, island.line, "astro-client-only", "warn",
                   f"an Astro island with client:only ({island.attributes.get('component-url', '')[:60]}) renders no server HTML: the space shifts when it hydrates and crawlers see nothing. Use client:visible or client:idle with server rendering")
    if parser.element_count > DOM_ELEMENT_LIMIT:
        report.add(page, 1, "dom-size-large", "note",
                   f"{parser.element_count} elements; large DOMs slow style, layout and every interaction (INP). Paginate, virtualise or use content-visibility")
    head_scripts = [el for el in elements if el.tag == "script" and el.in_head and el.attributes.get("src")]
    for script in head_scripts:
        local = site.local_file(page, script.attributes["src"])
        tiny = local is not None and gzip_size(local.read_bytes()) <= TINY_BLOCKING_SCRIPT_BYTES
        if not tiny and not is_true(script.attributes, "async") and not is_true(script.attributes, "defer") and script.attributes.get("type", "") != "module":
            report.add(page, script.line, "render-blocking-script", "warn",
                       f"<script src=\"{script.attributes['src'][:60]}\"> in <head> without defer, async or type=module blocks rendering")

    js_bytes, css_bytes, third_party_hosts = 0, 0, set()
    for element in elements:
        reference = element.attributes.get("src") if element.tag == "script" else element.attributes.get("href") if element.tag == "link" else None
        if not reference:
            continue
        rel = element.attributes.get("rel", "").lower().split()
        if element.tag == "link" and not ({"stylesheet", "modulepreload"} & set(rel)):
            continue
        local = site.local_file(page, reference)
        if local:
            size = gzip_size(local.read_bytes())
            if element.tag == "script" or "modulepreload" in rel:
                js_bytes += size
            elif "stylesheet" in rel and element.in_head:
                css_bytes += size
        elif host_of(reference):
            third_party_hosts.add(host_of(reference))
    if js_bytes > budgets["js"]:
        report.add(page, 1, "js-over-budget", "warn",
                   f"{js_bytes // 1024} KB of JavaScript (gzip) on this page; the budget is {budgets['js'] // 1024} KB. Hydrate fewer islands, defer the rest, drop unused libraries")
    if css_bytes > budgets["css"]:
        report.add(page, 1, "css-over-budget", "note",
                   f"{css_bytes // 1024} KB of render-blocking CSS (gzip); the budget is {budgets['css'] // 1024} KB")
    for host in sorted(third_party_hosts):
        known = next((name for domain, name in HEAVY_THIRD_PARTIES.items() if host.endswith(domain)), None)
        if known:
            report.add(page, 1, "heavy-third-party", "warn",
                       f"{known} ({host}) loads on this page; it competes with your own resources for the main thread and the network. Load it after interaction, behind consent, or drop it")
    font_preloads = [el for el in preloads if el.attributes.get("as") == "font"]
    for preload in font_preloads:
        if "crossorigin" not in preload.attributes:
            report.add(page, preload.line, "font-preload-no-crossorigin", "warn",
                       f"font preload {preload.attributes.get('href', '')} lacks crossorigin; the browser downloads the font twice")
    if len(font_preloads) > FONT_PRELOAD_LIMIT:
        report.add(page, font_preloads[0].line, "font-preload-many", "note",
                   f"{len(font_preloads)} font preloads compete with the LCP resource; preload one or two files at most")
    for element in elements:
        if element.tag == "link" and any(font_host in element.attributes.get("href", "") for font_host in THIRD_PARTY_FONT_HOSTS):
            report.add(page, element.line, "font-third-party", "warn",
                       f"fonts from {host_of(element.attributes['href'])}: an extra origin on the critical path, and in the EU a privacy issue (a Munich court fined a site for Google Fonts in 2022). Self-host them")
            break

    css_sources = [(text, line, page) for text, line in parser.inline_styles]
    for element in elements:
        if element.tag == "link" and "stylesheet" in element.attributes.get("rel", "").lower().split():
            local = site.local_file(page, element.attributes.get("href", ""))
            if local:
                css_sources.append((site.css_text(local), 0, local))
    for text, line, origin in css_sources:
        if re.search(r"@import\s+(url\()?['\"]", text):
            report.add(origin, line, "css-import", "note",
                       "@import in CSS fetches the imported file only after this one arrives, a serial chain on the critical path; bundle or link it directly")
        reported = set()
        for block in FONT_FACE.findall(text):
            if "font-not-woff2" not in reported and re.search(r"\.(ttf|otf|woff)(\?[^)]*)?['\"]?\)", block) and ".woff2" not in block:
                reported.add("font-not-woff2")
                report.add(origin, line, "font-not-woff2", "note",
                           "an @font-face serves TTF, OTF or WOFF without WOFF2; WOFF2 is supported everywhere and markedly smaller")
            if "font-display-missing" not in reported and re.search(r"url\(", block) and "font-display" not in block:
                reported.add("font-display-missing")
                family = re.search(r"font-family\s*:\s*([^;]+)", block)
                report.add(origin, line, "font-display-missing", "warn",
                           f"@font-face {family.group(1).strip() if family else ''} has no font-display; text stays invisible while the font loads. Use swap (or optional) with a metric-matched fallback")

    scripts = [(text, line, page) for text, line in parser.inline_scripts]
    for element in elements:
        if element.tag == "script" and element.attributes.get("src"):
            local = site.local_file(page, element.attributes["src"])
            if local and local.stat().st_size < 2_000_000:
                scripts.append((local.read_text(errors="replace"), 0, local))
    for text, line, origin in scripts:
        if UNLOAD_LISTENER.search(text):
            report.add(origin, line, "unload-handler", "warn",
                       "an unload handler: Chrome stops running unload on all page loads from version 154, so the code silently does nothing, and where it still runs it blocks the back/forward cache. Use pagehide or visibilitychange")
            break


def headers_rules(root: Path) -> list[tuple[str, dict]]:
    file = root / "_headers"
    rules: list[tuple[str, dict]] = []
    if not file.exists():
        return rules
    for raw in file.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            rules.append((raw.strip(), {}))
        elif rules and ":" in raw:
            name, value = raw.strip().split(":", 1)
            rules[-1][1][name.strip().lower()] = value.strip()
    return rules


def is_hashed(name: str) -> bool:
    match = HASHED_NAME.search(name)
    if not match:
        return False
    if match.group(2):
        return True
    token = match.group(1)
    return any(c.isupper() for c in token) and any(c.islower() or c.isdigit() for c in token)


def max_age(cache_control: str) -> int:
    match = re.search(r"max-age=(\d+)", cache_control)
    return int(match.group(1)) if match else 0


def check_edge(root: Path, report: Report):
    rules = headers_rules(root)
    for pattern, headers in rules:
        cache = headers.get("cache-control", "").lower()
        if "no-store" in cache and (pattern in ("/*", "/") or pattern.endswith(".html") or pattern.endswith("/")):
            report.add(root / "_headers", 0, "html-no-store", "note",
                       f"_headers sends Cache-Control: no-store on {pattern}: no browser or edge caching of HTML, and the back/forward cache only in Chrome, under conditions. Use no-cache or a short max-age")
    hashed_dirs = sorted({file.parent.relative_to(root).as_posix() for file in root.rglob("*") if file.is_file() and is_hashed(file.name) and file.parent != root})
    for directory in hashed_dirs[:3]:
        covered = any(pattern.rstrip("*").rstrip("/").lstrip("/") in (directory, "") and max_age(headers.get("cache-control", "")) >= IMMUTABLE_MIN_AGE
                      for pattern, headers in rules if pattern.endswith("/*"))
        if not covered:
            report.add(root / "_headers" if (root / "_headers").exists() else root, 0, "assets-not-immutable", "note",
                       f"hashed files in /{directory}/ get Cloudflare's default revalidating cache; add `/{directory}/*` with `Cache-Control: public, max-age=31536000, immutable` to _headers")


def scan_site(path: Path, budgets: dict) -> Report:
    root, setup = locate_root(path)
    report = Report(path.resolve())
    report.findings.extend(setup)
    if root is None:
        return report
    report.root = root
    site = Site(root)
    for page in sorted(root.rglob("*.html")):
        check_page(page, site, budgets, report)
    check_edge(root, report)
    return report


@dataclass
class Timed:
    status: int | None
    headers: dict
    body: bytes
    ttfb_ms: float
    error: str | None = None


def timed_fetch(url: str, timeout: float, accept_encoding: str = "br, gzip, zstd") -> Timed:
    parts = urllib.parse.urlsplit(url)
    connection_class = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    options = {"timeout": timeout}
    if parts.scheme == "https":
        options["context"] = ssl.create_default_context()
    try:
        connection = connection_class(parts.netloc, **options)
        started = time.monotonic()
        connection.request("GET", (parts.path or "/") + (f"?{parts.query}" if parts.query else ""),
                           headers={"User-Agent": BROWSER_USER_AGENT, "Accept-Encoding": accept_encoding, "Accept": "text/html,*/*"})
        response = connection.getresponse()
        ttfb = (time.monotonic() - started) * 1000
        headers = {name.lower(): value for name, value in response.getheaders()}
        body = response.read(3_000_000)
        connection.close()
        return Timed(response.status, headers, body, ttfb)
    except (socket.timeout, TimeoutError):
        return Timed(None, {}, b"", 0, "timeout")
    except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
        return Timed(None, {}, b"", 0, f"{type(exc).__name__}: {exc}")


def follow(url: str, timeout: float) -> tuple[str, Timed]:
    response = timed_fetch(url, timeout)
    for _ in range(4):
        location = response.headers.get("location")
        if response.status is None or not (300 <= response.status < 400) or not location:
            break
        url = urllib.parse.urljoin(url, location)
        response = timed_fetch(url, timeout)
    return url, response


def decoded(response: Timed) -> str:
    encoding = response.headers.get("content-encoding", "")
    try:
        if encoding == "gzip":
            return gzip.decompress(response.body).decode("utf-8", errors="replace")
    except OSError:
        return ""
    return response.body.decode("utf-8", errors="replace") if not encoding else ""


def crux_record(scope: str, value: str, form_factor: str, timeout: float) -> tuple[str, dict]:
    key = os.environ.get("CRUX_API_KEY")
    if not key:
        return "no-key", {}
    body = json.dumps({scope: value, "formFactor": form_factor.upper()}).encode()
    request = urllib.request.Request(f"{CRUX_ENDPOINT}?key={urllib.parse.quote(key)}", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "ok", json.load(response).get("record", {}).get("metrics", {})
    except urllib.error.HTTPError as error:
        error.close()
        return ("missing" if error.code == 404 else f"HTTP {error.code}"), {}
    except (OSError, ValueError) as error:
        return type(error).__name__, {}


def check_field(url: str, form_factor: str, timeout: float, report: Report):
    origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(url))
    for scope, value in (("url", url), ("origin", origin)):
        status, metrics = crux_record(scope, value, form_factor, timeout)
        if status == "no-key":
            report.add(url, 0, "field-unavailable", "note",
                       "no field data read: set CRUX_API_KEY (free, Google Cloud console, CrUX API enabled) to compare with what real Chrome users get")
            return
        if status == "missing":
            report.add(url, 0, "field-data-missing", "note",
                       f"CrUX has no {form_factor} data for this {scope} (too little Chrome traffic in 28 days); missing is not passing, so use your own RUM or synthetic tests")
            continue
        if status != "ok":
            report.add(url, 0, "field-unavailable", "note", f"the CrUX API failed for the {scope} ({status}); retry later")
            continue
        for metric, (label, good, poor, show) in FIELD_METRICS.items():
            p75 = (metrics.get(metric) or {}).get("percentiles", {}).get("p75")
            if p75 is None:
                continue
            p75 = float(p75)
            minor = label == "TTFB"
            if p75 > poor:
                report.add(url, 0, "field-metric-poor", "warn" if minor else "fail",
                           f"{scope} {label} p75 is {show(p75)} on {form_factor} for real Chrome users over 28 days: poor")
            elif p75 > good:
                report.add(url, 0, "field-metric-needs-improvement", "note" if minor else "warn",
                           f"{scope} {label} p75 is {show(p75)} on {form_factor} for real Chrome users over 28 days: needs improvement")


def scan_live(url: str, field_mode: bool, form_factor: str, timeout: float) -> Report:
    url = url if "://" in url else f"https://{url}"
    report = Report(Path("."))
    final_url, first = follow(url, timeout)
    if first.status is None:
        report.add(url, 0, "live-unreachable", "fail", f"{url} did not answer: {first.error}")
        return report
    samples = [first.ttfb_ms] + [timed_fetch(final_url, timeout).ttfb_ms for _ in range(LIVE_SAMPLES - 1)]
    ttfb = statistics.median(samples)
    if ttfb > TTFB_GOOD_MS:
        report.add(final_url, 0, "ttfb-slow", "warn",
                   f"median time to first byte {ttfb:.0f} ms over {LIVE_SAMPLES} requests from here; web.dev's rough guide is under {TTFB_GOOD_MS} ms at p75. Static assets should answer from the edge: look for redirects, a Worker in front of HTML, or a cold origin")
    if not first.headers.get("content-encoding"):
        report.add(final_url, 0, "html-uncompressed", "warn", "HTML is served without Brotli, Zstandard or Gzip")
    if "no-store" in first.headers.get("cache-control", "").lower():
        report.add(final_url, 0, "html-no-store", "note",
                   "HTML is served with Cache-Control: no-store: no browser caching, and the back/forward cache only in Chrome, under conditions. Use no-cache or a short max-age")
    if "h3" not in first.headers.get("alt-svc", ""):
        report.add(final_url, 0, "http3-missing", "note", "no HTTP/3 advertised (alt-svc h3); enable it in the zone's Network settings")
    html = decoded(timed_fetch(final_url, timeout, "gzip"))
    assets = re.findall(r"""(?:src|href)=["']([^"']+\.(?:css|js))["']""", html)
    for asset in assets[:2]:
        asset_url = urllib.parse.urljoin(final_url, asset)
        if urllib.parse.urlsplit(asset_url).netloc != urllib.parse.urlsplit(final_url).netloc:
            continue
        response = timed_fetch(asset_url, timeout)
        if response.status != 200:
            continue
        if not response.headers.get("content-encoding"):
            report.add(asset_url, 0, "asset-uncompressed", "warn", "CSS or JavaScript is served without compression")
        if is_hashed(urllib.parse.urlsplit(asset_url).path) and max_age(response.headers.get("cache-control", "")) < IMMUTABLE_MIN_AGE:
            report.add(asset_url, 0, "assets-not-immutable", "note",
                       f"hashed asset served with Cache-Control: {response.headers.get('cache-control', '-')}; cache it for a year as immutable")
    if field_mode:
        check_field(final_url, form_factor, timeout, report)
    return report


def aggregate(findings: list[Finding]) -> list[Finding]:
    grouped: dict[tuple, Finding] = {}
    for finding in sorted(findings, key=lambda f: (f.path, f.line)):
        key = (finding.rule, finding.severity, finding.message)
        if key in grouped:
            grouped[key].also.append(f"{finding.path}{':' + str(finding.line) if finding.line else ''}")
        else:
            grouped[key] = finding
    return list(grouped.values())


def render(report: Report, as_json: bool) -> str:
    findings = sorted(aggregate(report.findings), key=lambda f: (-SEVERITY_RANK[f.severity], f.path, f.line))
    if as_json:
        return json.dumps({"findings": [asdict(f) for f in findings]}, indent=2)
    if not findings:
        return "no findings"
    lines = [f"{f.severity:5} {f.rule:30} {f.path}{':' + str(f.line) if f.line else ''}  {f.message}"
             + (f" (+{len(f.also)} more: {', '.join(f.also[:3])}{', …' if len(f.also) > 3 else ''})" if f.also else "") for f in findings]
    counts = Counter(f.severity for f in findings)
    lines.append(f"\n{counts['fail']} fail, {counts['warn']} warn, {counts['note']} note")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_subparsers(dest="mode", required=True)
    site_mode = modes.add_parser("site")
    site_mode.add_argument("path", type=Path)
    site_mode.add_argument("--js-budget-kb", type=int, default=100)
    site_mode.add_argument("--css-budget-kb", type=int, default=50)
    site_mode.add_argument("--hero-budget-kb", type=int, default=200)
    live_mode = modes.add_parser("live")
    live_mode.add_argument("url")
    live_mode.add_argument("--field", action="store_true")
    live_mode.add_argument("--form-factor", choices=["phone", "desktop"], default="phone")
    live_mode.add_argument("--timeout", type=float, default=15)
    for mode in (site_mode, live_mode):
        mode.add_argument("--json", action="store_true")
        mode.add_argument("--fail-on", choices=list(SEVERITY_RANK), default="fail")
    args = parser.parse_args()
    if args.mode == "site":
        budgets = {"js": args.js_budget_kb * 1024, "css": args.css_budget_kb * 1024, "hero": args.hero_budget_kb * 1024}
        report = scan_site(args.path, budgets)
    else:
        report = scan_live(args.url, args.field, args.form_factor, args.timeout)
    print(render(report, args.json))
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[f.severity] >= threshold for f in report.findings) else 0


if __name__ == "__main__":
    sys.exit(main())

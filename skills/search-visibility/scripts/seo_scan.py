#!/usr/bin/env python3
"""Audit a static site's build output and its live edge for search and AI-answer visibility.

Usage:
    seo_scan.py site PATH [--base-url URL] [--json] [--fail-on fail|warn|note|never]
    seo_scan.py live URL [--mirror HOST ...] [--sample N] [--timeout S] [--json] [--fail-on ...]

site: PATH is a repository with a wrangler config (its assets.directory is
scanned and its html_handling decides which URL serves each file) or a build
directory. Pages, sitemaps, robots.txt, _headers and _redirects are judged
together: a canonical, sitemap entry or internal link that lands on a 307
trailing-slash redirect or a missing file is caught before deploy.

live: fetches robots.txt, the sitemaps it names, a sample of their URLs, the
home page as a browser and as each crawler in crawlers.json, and every
--mirror host (*.workers.dev, *.pages.dev, staging, preview) that must not be
indexed. Exit status 1 when a finding at or above --fail-on exists (default:
fail). The scan reads files and HTTP responses; it never replaces Search
Console, Bing Webmaster Tools or a look at what the engines actually show.
"""

import argparse
import fnmatch
import http.client
import json
import re
import socket
import ssl
import sys
import tomllib
import urllib.parse
import xml.etree.ElementTree as ElementTree
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path

DATA_DIRECTORY = Path(__file__).resolve().parent
CONFIG_NAMES = ("wrangler.jsonc", "wrangler.json", "wrangler.toml")
SEVERITY_RANK = {"fail": 3, "warn": 2, "note": 1, "never": 99}
PLACEHOLDER_HOSTS = re.compile(r"(^|\.)(localhost|127\.0\.0\.1|0\.0\.0\.0|example\.(com|org|net)|[^.]+\.workers\.dev|[^.]+\.pages\.dev)$", re.I)
SITEMAP_NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
HREFLANG_CODE = re.compile(r"^(x-default|[a-z]{2,3}(-[A-Za-z]{4})?(-([A-Za-z]{2}|\d{3}))?)$")
THIN_SHELL_TEXT_CHARS = 200
GOOGLEBOT_FETCH_LIMIT_BYTES = 2 * 1024 * 1024
GENERIC_LINK_TEXT = re.compile(r"^(click here|here|read more|more|learn more|this|link|klik hier|hier|lees meer|meer|meer info)$", re.I)
AI_ADDRESSED_TEXT = re.compile(r"ignore (all |any )?(previous|prior|earlier) instructions|if you are an? (ai|llm|large language model|language model|chatbot|ai assistant)|(note|message|instruction)s? (to|for) (ai|llms?|language models|chatbots|ai assistants)|ai (assistants?|models?|agents?|crawlers?),? (should|must|always) (recommend|mention|cite|rank|say)", re.I)
PLACEHOLDER_TEXT = re.compile(r"\blorem ipsum\b", re.I)
UNIFORM_LASTMOD_MINIMUM = 5
DESCRIPTION_MINIMUM_CHARS = 50
REQUIRED_OPEN_GRAPH = ("og:title", "og:type", "og:image", "og:url")
SITEMAP_CANDIDATES = ("sitemap-index.xml", "sitemap_index.xml", "sitemap.xml")
BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
BLOCKING_STATUSES = {401, 403, 429, 503}
CLOUDFLARE_MANAGED_MARKER = "BEGIN Cloudflare Managed"
PREVIEW_IMAGE_BUDGET_BYTES = 600 * 1024


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str
    also: list = field(default_factory=list)


@dataclass
class Page:
    file: Path
    url_path: str
    line_of: dict = field(default_factory=dict)
    lang: str | None = None
    title: str | None = None
    metas: dict = field(default_factory=dict)
    canonicals: list = field(default_factory=list)
    alternates: list = field(default_factory=list)
    anchors: list = field(default_factory=list)
    images_without_alt: list = field(default_factory=list)
    h1_count: int = 0
    jsonld: list = field(default_factory=list)
    scripts: int = 0
    text_chars: int = 0
    header_noindex: bool = False
    meta_refresh: bool = False
    ids: set = field(default_factory=set)
    icons: list = field(default_factory=list)
    size: int = 0
    raw: str = ""

    @property
    def noindex(self) -> bool:
        directives = {token.strip() for name in ("robots", "googlebot") for token in self.metas.get(name, "").lower().split(",")}
        return bool(directives & {"noindex", "none"}) or self.header_noindex


class PageParser(HTMLParser):
    def __init__(self, page: Page):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.in_title = False
        self.title_parts: list[str] = []
        self.jsonld_parts: list[str] | None = None
        self.jsonld_line = 0
        self.hidden_depth = 0
        self.anchor: list | None = None

    def handle_starttag(self, tag, attrs):
        attributes = {name.lower(): (value or "") for name, value in attrs}
        line = self.getpos()[0]
        page = self.page
        if attributes.get("id"):
            page.ids.add(attributes["id"])
        if tag == "a" and attributes.get("name"):
            page.ids.add(attributes["name"])
        if tag == "html" and attributes.get("lang"):
            page.lang = attributes["lang"]
        elif tag == "title":
            self.in_title = True
            page.line_of.setdefault("title", line)
        elif tag == "meta":
            if attributes.get("http-equiv", "").lower() == "refresh":
                page.meta_refresh = True
            key = (attributes.get("name") or attributes.get("property") or "").lower()
            if key:
                page.metas[key] = attributes.get("content", "").strip()
                page.line_of.setdefault(key, line)
        elif tag == "link":
            rel = attributes.get("rel", "").lower().split()
            if "canonical" in rel:
                page.canonicals.append((attributes.get("href", "").strip(), line))
            if "alternate" in rel and attributes.get("hreflang"):
                page.alternates.append((attributes["hreflang"].strip(), attributes.get("href", "").strip(), line))
            if {"icon", "shortcut", "apple-touch-icon", "apple-touch-icon-precomposed"} & set(rel):
                page.icons.append((attributes.get("href", ""), attributes.get("type", "")))
        elif tag == "a" and "href" in attributes:
            self.anchor = [attributes["href"].strip(), attributes.get("rel", "").lower(), line, []]
            page.anchors.append(self.anchor)
        elif tag == "img" and "alt" not in attributes:
            page.images_without_alt.append(line)
        elif tag == "h1":
            page.h1_count += 1
        elif tag == "script":
            if attributes.get("type", "").lower() == "application/ld+json":
                self.jsonld_parts = []
                self.jsonld_line = line
            else:
                page.scripts += 1
                self.hidden_depth += 1
        elif tag in ("style", "template"):
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor is not None:
            self.anchor[3] = " ".join("".join(self.anchor[3]).split())
            self.anchor = None
        if tag == "title" and self.in_title:
            self.in_title = False
            self.page.title = " ".join("".join(self.title_parts).split())
        elif tag == "script":
            if self.jsonld_parts is not None:
                self.page.jsonld.append(("".join(self.jsonld_parts), self.jsonld_line))
                self.jsonld_parts = None
            elif self.hidden_depth:
                self.hidden_depth -= 1
        elif tag in ("style", "template") and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        elif self.jsonld_parts is not None:
            self.jsonld_parts.append(data)
        elif not self.hidden_depth:
            self.page.text_chars += len(data.strip())
            if self.anchor is not None and isinstance(self.anchor[3], list):
                self.anchor[3].append(data)


def load_data(name: str) -> dict:
    return json.loads((DATA_DIRECTORY / name).read_text())


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


def find_config(directory: Path) -> Path | None:
    return next((directory / name for name in CONFIG_NAMES if (directory / name).exists()), None)


def load_config(path: Path) -> dict:
    text = path.read_text()
    return tomllib.loads(text) if path.suffix == ".toml" else json.loads(strip_jsonc(text))


def route_base_url(config: dict) -> str | None:
    for route in config.get("routes") or ([config["route"]] if config.get("route") else []):
        pattern = route if isinstance(route, str) else route.get("pattern", "")
        host = pattern.split("/")[0].lstrip("*.").strip()
        if host and "*" not in host:
            return f"https://{host}"
    return None


@dataclass
class Site:
    root: Path
    html_handling: str = "auto-trailing-slash"
    not_found_handling: str = "none"
    config_path: Path | None = None
    base_url: str | None = None
    redirected: dict = field(default_factory=dict)


def locate_site(path: Path) -> tuple[Site | None, list[Finding]]:
    for directory in (path, path.parent):
        config_path = find_config(directory)
        if not config_path:
            continue
        config = load_config(config_path)
        assets = config.get("assets") or {}
        if "directory" in assets:
            root = (directory / assets["directory"]).resolve()
        elif config.get("pages_build_output_dir"):
            root = (directory / config["pages_build_output_dir"]).resolve()
        else:
            continue
        if directory == path.parent and root != path.resolve():
            continue
        if not root.is_dir():
            return None, [Finding(str(config_path), 0, "build-missing", "fail",
                                  f"assets directory {root} does not exist; run the site's build first, then scan")]
        return Site(root, assets.get("html_handling", "auto-trailing-slash"),
                    assets.get("not_found_handling", "none"), config_path, route_base_url(config)), []
    return Site(path.resolve()), []


def served_path(site: Site, file: Path) -> str:
    relative = file.relative_to(site.root).as_posix()
    if site.html_handling == "none":
        return "/" + relative
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        stem = "/" + relative[: -len("index.html")]
        return stem.rstrip("/") if site.html_handling == "drop-trailing-slash" else stem
    stem = "/" + relative[: -len(".html")]
    return stem + "/" if site.html_handling == "force-trailing-slash" else stem


def resolve(site: Site, url_path: str, served: dict[str, Path]) -> tuple[str, str | None]:
    path = urllib.parse.unquote(url_path.split("#")[0].split("?")[0]) or "/"
    if path in site.redirected:
        return "redirect", site.redirected[path]
    if path in served:
        return "ok", path
    candidates = [path.rstrip("/"), path.rstrip("/") + "/"]
    if path.endswith("/index.html"):
        candidates.append(path[: -len("index.html")])
    if path.endswith(".html"):
        candidates.append(path[: -len(".html")])
    for candidate in candidates:
        if candidate and candidate in served and candidate != path:
            return "redirect", candidate
    if (site.root / path.lstrip("/")).is_file():
        return "ok", path
    return "missing", None


def parse_redirects_file(path: Path) -> list[tuple[int, str, str, str]]:
    rules = []
    if not path.exists():
        return rules
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        parts = raw.split("#", 1)[0].split()
        if len(parts) >= 2:
            rules.append((number, parts[0], parts[1], parts[2] if len(parts) > 2 else "302"))
    return rules


def parse_headers_file(path: Path) -> list[tuple[str, dict]]:
    rules: list[tuple[str, dict]] = []
    if not path.exists():
        return rules
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            rules.append((raw.strip(), {}))
        elif rules and ":" in raw:
            name, value = raw.strip().split(":", 1)
            rules[-1][1][name.strip().lower()] = value.strip()
    return rules


def headers_pattern_matches(pattern: str, url_path: str) -> bool:
    glob = re.sub(r":[A-Za-z_]+", "*", pattern)
    return fnmatch.fnmatchcase(url_path, glob)


def parse_page(site: Site, file: Path, header_rules: list) -> Page:
    page = Page(file, served_path(site, file))
    page.raw = file.read_text(errors="replace")
    page.size = file.stat().st_size
    parser = PageParser(page)
    parser.feed(page.raw)
    parser.close()
    page.anchors = [(href, rel, line, text if isinstance(text, str) else " ".join("".join(text).split())) for href, rel, line, text in page.anchors]
    for pattern, headers in header_rules:
        robots = headers.get("x-robots-tag", "").lower()
        if pattern.startswith("/") and "noindex" in robots and headers_pattern_matches(pattern, page.url_path):
            page.header_noindex = True
    return page


def absolute(base_url: str | None, page_url_path: str, href: str) -> str:
    if base_url:
        return urllib.parse.urljoin(base_url + page_url_path, href)
    return urllib.parse.urljoin("https://site.invalid" + page_url_path, href)


def is_internal(url: str, base_url: str | None) -> bool:
    host = urllib.parse.urlsplit(url).netloc.lower()
    return host == "site.invalid" or (base_url is not None and host == urllib.parse.urlsplit(base_url).netloc.lower())


def placeholder_host(url: str) -> str | None:
    host = urllib.parse.urlsplit(url).hostname or ""
    return host if host and PLACEHOLDER_HOSTS.search(host) else None


def other_host(url: str, base_url: str | None) -> str | None:
    host = urllib.parse.urlsplit(url).hostname or ""
    if not host or host == "site.invalid" or not base_url or placeholder_host(url):
        return None
    return host if host != urllib.parse.urlsplit(base_url).hostname else None


def infer_base_url(site: Site, pages: list[Page]) -> str | None:
    if site.base_url:
        return site.base_url
    hosts = Counter()
    for page in pages:
        for href, _ in page.canonicals:
            parts = urllib.parse.urlsplit(href)
            if parts.scheme in ("http", "https") and parts.hostname and not PLACEHOLDER_HOSTS.search(parts.hostname):
                hosts[f"{parts.scheme}://{parts.netloc}"] += 1
    return hosts.most_common(1)[0][0] if hosts else None


class Report:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[Finding] = []

    def add(self, path, line: int, rule: str, severity: str, message: str):
        label = str(path.relative_to(self.root)) if isinstance(path, Path) and path.is_relative_to(self.root) else str(path)
        self.findings.append(Finding(label, line, rule, severity, message))


def check_page(page: Page, site: Site, served: dict[str, Path], retired: dict, report: Report, pages_by_path: dict):
    file = page.file
    base = site.base_url
    if page.size > GOOGLEBOT_FETCH_LIMIT_BYTES:
        report.add(file, 1, "html-over-limit", "fail",
                   f"{page.size // 1024} KiB of HTML; Googlebot reads only the first 2 MiB of uncompressed HTML and drops the rest. Move inlined SVG sprites, base64 images and data blobs out")
    ai_text = AI_ADDRESSED_TEXT.search(page.raw)
    if ai_text:
        report.add(file, page.raw.count("\n", 0, ai_text.start()) + 1, "ai-addressed-text", "fail",
                   f"text addressed to AI systems ({ai_text.group(0)!r}); engines treat it as prompt injection and spam, and it costs trust when people see it")
    placeholder = PLACEHOLDER_TEXT.search(page.raw)
    if placeholder:
        report.add(file, page.raw.count("\n", 0, placeholder.start()) + 1, "placeholder-text", "warn", "lorem ipsum in a built page; ship real copy")
    if page.url_path == "/" and page.noindex:
        report.add(file, page.line_of.get("robots", 0), "noindex-home", "fail",
                   "the home page is noindex; nothing on the site will rank. Remove the robots meta or the X-Robots-Tag rule")
    identity_urls = page.canonicals + [(page.metas.get("og:url", ""), page.line_of.get("og:url", 0))]
    for href, line in identity_urls + [(page.metas.get("og:image", ""), page.line_of.get("og:image", 0))] + [(href, line) for _, href, line in page.alternates]:
        host = placeholder_host(href) if href else None
        if host:
            report.add(file, line, "foreign-host-url", "fail",
                       f"{href} points at {host}, a development or mirror host; engines and link previews follow it there")
    for href, line in identity_urls:
        host = other_host(href, base) if href else None
        if host:
            report.add(file, line, "cross-host-canonical", "warn",
                       f"{href} names {host} as this page's home, not {urllib.parse.urlsplit(base).hostname}; right only for deliberately syndicated copies")
    if page.noindex:
        return
    if not page.title:
        report.add(file, page.line_of.get("title", 1), "title-missing", "fail",
                   "no <title>; it is the main source of the title link in results and of the name assistants cite")
    if not page.metas.get("description"):
        report.add(file, 1, "description-missing", "warn",
                   "no meta description; engines then build the snippet from page text, often badly")
    elif len(page.metas["description"]) < DESCRIPTION_MINIMUM_CHARS:
        report.add(file, page.line_of.get("description", 1), "description-thin", "note",
                   f"meta description is {len(page.metas['description'])} characters; one or two sentences that answer what the page offers work better")
    if not page.lang:
        report.add(file, 1, "lang-missing", "warn", "<html> has no lang; engines guess the language and screen readers mispronounce")
    if not page.metas.get("viewport"):
        report.add(file, 1, "viewport-missing", "warn", "no viewport meta; mobile-first indexing renders the page as a phone sees it")
    if len(page.canonicals) > 1:
        report.add(file, page.canonicals[1][1], "canonical-multiple", "fail",
                   "more than one rel=canonical; Google ignores conflicting canonicals entirely")
    if not page.canonicals:
        report.add(file, 1, "canonical-missing", "warn",
                   "no rel=canonical; tracking parameters, the trailing-slash variant and mirror hosts then compete with this URL")
    for href, line in page.canonicals[:1]:
        target = absolute(base, page.url_path, href)
        if not href.startswith(("http://", "https://")):
            report.add(file, line, "canonical-relative", "note", f"canonical {href!r} is relative; write the absolute production URL")
        if is_internal(target, base):
            state, served_as = resolve(site, urllib.parse.urlsplit(target).path, served)
            if state == "missing":
                report.add(file, line, "canonical-target-missing", "fail", f"canonical {href} matches no file in the build")
            elif state == "redirect":
                report.add(file, line, "canonical-redirects", "warn",
                           f"canonical {href} is answered with a redirect under html_handling={site.html_handling}; point it at {served_as}")
    og_url = page.metas.get("og:url", "")
    if og_url and page.canonicals:
        canonical = absolute(base, page.url_path, page.canonicals[0][0])
        if absolute(base, page.url_path, og_url).rstrip("/") != canonical.rstrip("/"):
            report.add(file, page.line_of.get("og:url", 1), "og-url-mismatch", "warn",
                       f"og:url {og_url} differs from the canonical {canonical}; shares then count toward a different URL")
    directives = {token.strip() for name in ("robots", "bingbot") for token in page.metas.get(name, "").lower().split(",")}
    if directives & {"noarchive", "nocache"}:
        report.add(file, page.line_of.get("robots", page.line_of.get("bingbot", 1)), "noarchive-set", "warn",
                   "noarchive/nocache: Google ignores it, but Bing drops the page from Copilot answers (nocache leaves only URL, title and snippet)")
    missing_og = [key for key in REQUIRED_OPEN_GRAPH if not page.metas.get(key)]
    if missing_og:
        report.add(file, 1, "og-incomplete", "warn",
                   f"missing {', '.join(missing_og)}; link previews in LinkedIn, Slack, WhatsApp and Discord fall back to guesses")
    image = page.metas.get("og:image", "")
    if image and not image.startswith(("https://", "http://")):
        report.add(file, page.line_of.get("og:image", 1), "og-image-relative", "fail",
                   f"og:image {image!r} is relative; preview consumers need an absolute URL and show no image")
    if image.startswith(("https://", "http://")) and is_internal(image, base):
        image_path = urllib.parse.unquote(urllib.parse.urlsplit(image).path)
        if not (site.root / image_path.lstrip("/")).is_file():
            report.add(file, page.line_of.get("og:image", 1), "og-image-missing", "fail",
                       f"og:image {image} matches no file in the build; every link preview of this page shows no image")
    if image and not page.metas.get("twitter:card"):
        report.add(file, page.line_of.get("og:image", 1), "twitter-card-missing", "note",
                   "no twitter:card; X shows a small card unless twitter:card is summary_large_image")
    for text, line in page.jsonld:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            report.add(file, line, "jsonld-invalid", "fail", f"JSON-LD does not parse ({exc.msg}); engines discard the whole block")
            continue
        for node in jsonld_nodes(data):
            if node.get("@type") is None and "@graph" not in node:
                report.add(file, line, "jsonld-untyped", "warn", "a JSON-LD node has no @type; nothing can use it")
        for kind in sorted({kind for node in nested_nodes(data) for kind in node_types(node)} & set(retired)):
            report.add(file, line, "jsonld-retired-type", "note", f"{kind}: {retired[kind]}")
    for hreflang, href, line in page.alternates:
        if not HREFLANG_CODE.match(hreflang):
            report.add(file, line, "hreflang-invalid", "fail", f"hreflang {hreflang!r} is not a language(-script)(-region) code or x-default")
    if page.text_chars < THIN_SHELL_TEXT_CHARS and page.scripts:
        report.add(file, 1, "thin-shell", "warn",
                   f"only {page.text_chars} characters of text without JavaScript; AI crawlers that do not render scripts see an empty page")
    if page.images_without_alt:
        report.add(file, page.images_without_alt[0], "img-alt-missing", "warn",
                   f"{len(page.images_without_alt)} <img> without alt; write alt text, or alt=\"\" when decorative")
    if page.h1_count == 0:
        report.add(file, 1, "h1-missing", "note", "no <h1>; the visible page title should be one")
    for href, rel, line, text in page.anchors:
        if GENERIC_LINK_TEXT.match(text or ""):
            report.add(file, line, "link-text-generic", "note",
                       f"link text {text!r} says nothing about {href}; engines and screen readers use anchor text to understand the target")
        target = absolute(base, page.url_path, href)
        if href.startswith(("mailto:", "tel:", "javascript:", "data:")) or not is_internal(target, base):
            continue
        if href.startswith("#"):
            if href[1:] and urllib.parse.unquote(href[1:]) not in page.ids:
                report.add(file, line, "anchor-missing", "warn", f"in-page link {href} has no matching id on this page")
            continue
        if "nofollow" in rel.split():
            report.add(file, line, "internal-nofollow", "warn", f"internal link {href} is nofollow; it hides your own page from crawlers")
        state, served_as = resolve(site, urllib.parse.urlsplit(target).path, served)
        fragment = urllib.parse.urlsplit(target).fragment
        if state != "missing" and fragment and served_as in pages_by_path:
            if urllib.parse.unquote(fragment) not in pages_by_path[served_as].ids:
                report.add(file, line, "anchor-missing", "warn", f"internal link {href} points at #{fragment}, which {served_as} does not contain")
        if state == "missing":
            report.add(file, line, "internal-link-broken", "fail", f"internal link {href} matches no file in the build")
        elif state == "redirect":
            report.add(file, line, "internal-link-redirects", "note",
                       f"internal link {href} costs a redirect under html_handling={site.html_handling}; link to {served_as}")


def jsonld_nodes(data) -> list[dict]:
    if isinstance(data, list):
        return [node for item in data for node in jsonld_nodes(item)]
    if not isinstance(data, dict):
        return []
    return [data] + jsonld_nodes(data.get("@graph", []))


def nested_nodes(data) -> list[dict]:
    if isinstance(data, list):
        return [node for item in data for node in nested_nodes(item)]
    if not isinstance(data, dict):
        return []
    return [data] + [node for value in data.values() for node in nested_nodes(value)]


def node_types(node: dict) -> list:
    kind = node.get("@type")
    return kind if isinstance(kind, list) else [kind] if kind else []


def check_hreflang_clusters(pages: list[Page], site: Site, served: dict[str, Path], report: Report):
    by_path = {page.url_path: page for page in pages}
    for page in pages:
        if page.noindex or not page.alternates:
            continue
        targets = {}
        for hreflang, href, _ in page.alternates:
            target = absolute(site.base_url, page.url_path, href)
            if is_internal(target, site.base_url):
                state, served_as = resolve(site, urllib.parse.urlsplit(target).path, served)
                targets[hreflang] = served_as if state != "missing" else None
        if page.url_path not in targets.values():
            report.add(page.file, page.alternates[0][2], "hreflang-no-self", "warn",
                       "hreflang set does not list this page itself; each language version must list every version including its own")
        if "x-default" not in targets:
            report.add(page.file, page.alternates[0][2], "hreflang-no-x-default", "note",
                       "no hreflang x-default; name the version for visitors whose language matches none")
        for hreflang, path in targets.items():
            other = by_path.get(path) if path else None
            if other is None or other is page:
                continue
            back = {absolute(site.base_url, other.url_path, href) for _, href, _ in other.alternates}
            back_paths = {urllib.parse.urlsplit(url).path for url in back}
            if page.url_path not in back_paths:
                report.add(page.file, page.alternates[0][2], "hreflang-not-reciprocal", "warn",
                           f"{path} ({hreflang}) does not link back to {page.url_path}; Google ignores one-way hreflang")


def alternate_clusters(pages: list[Page]) -> dict[str, str]:
    parent = {page.url_path: page.url_path for page in pages}

    def root(path: str) -> str:
        while parent.setdefault(path, path) != path:
            path = parent[path]
        return path

    for page in pages:
        for _, href, _ in page.alternates:
            other = urllib.parse.urlsplit(href).path or "/"
            parent[root(other)] = root(page.url_path)
    return {page.url_path: root(page.url_path) for page in pages}


def check_duplicates(pages: list[Page], report: Report):
    indexable = [page for page in pages if not page.noindex]
    cluster = alternate_clusters(indexable)
    for attribute, rule, severity, what in (("title", "title-duplicate", "warn", "title"), ("description", "description-duplicate", "note", "meta description")):
        groups = defaultdict(list)
        for page in indexable:
            value = page.title if attribute == "title" else page.metas.get("description")
            if value:
                groups[value].append(page)
        for value, group in groups.items():
            if len({cluster[page.url_path] for page in group}) > 1:
                others = ", ".join(p.url_path for p in group[1:4])
                report.add(group[0].file, group[0].line_of.get(attribute, 1), rule, severity,
                           f"{len(group)} pages share the {what} {value[:60]!r} (also {others}); each page needs its own")


def check_link_graph(pages: list[Page], site: Site, served: dict[str, Path], sitemap_paths: set, report: Report):
    inbound = Counter()
    for page in pages:
        for href, _, _, _ in page.anchors:
            target = absolute(site.base_url, page.url_path, href)
            if is_internal(target, site.base_url):
                state, served_as = resolve(site, urllib.parse.urlsplit(target).path, served)
                if state != "missing" and served_as != page.url_path:
                    inbound[served_as] += 1
    home = resolve(site, site.redirected.get("/", "/"), served)[1] or "/"
    for page in pages:
        if page.noindex or page.url_path in ("/", home):
            continue
        if not inbound[page.url_path]:
            where = "listed only in the sitemap" if page.url_path in sitemap_paths else "not linked and not in the sitemap"
            report.add(page.file, 1, "orphan-page", "warn",
                       f"{page.url_path} has no internal links pointing at it ({where}); link it from a related page")


def parse_robots(text: str) -> list[tuple[list[str], list[tuple[str, str]]]]:
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    expecting_agents = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not expecting_agents:
                groups.append(([], []))
            groups[-1][0].append(value.lower())
            expecting_agents = True
        elif key in ("allow", "disallow") and groups:
            groups[-1][1].append((key, value))
            expecting_agents = False
        else:
            expecting_agents = False
    return groups


def robots_pattern_matches(pattern: str, path: str) -> bool:
    if not pattern:
        return False
    anchored = pattern.endswith("$")
    regex = re.escape(pattern.rstrip("$")).replace(r"\*", ".*")
    return re.match(regex + ("$" if anchored else ""), path) is not None


def robots_blocks(groups, token: str | None, path: str = "/") -> bool:
    token = (token or "").lower()
    specific = [rules for agents, rules in groups if token and token in agents]
    chosen = specific or [rules for agents, rules in groups if "*" in agents]
    rules = [rule for group in chosen for rule in group]
    best_length, verdict = -1, False
    for kind, pattern in rules:
        if robots_pattern_matches(pattern, path) and len(pattern) >= best_length:
            if len(pattern) > best_length or kind == "allow":
                verdict = kind == "disallow"
            best_length = len(pattern)
    return verdict


def check_robots(text: str, origin: str, crawlers: list[dict], report: Report, base_url: str | None):
    groups = parse_robots(text)
    blocked = {crawler["token"]: robots_blocks(groups, crawler["token"]) for crawler in crawlers}
    if robots_blocks(groups, None) and all(blocked[c["token"]] for c in crawlers if c["role"] == "search"):
        report.add(origin, 0, "robots-blocks-everything", "fail", "robots.txt disallows / for every crawler; the site cannot be crawled")
    else:
        for crawler in crawlers:
            if not blocked[crawler["token"]]:
                continue
            if crawler["role"] == "search":
                report.add(origin, 0, "robots-blocks-search", "fail",
                           f"robots.txt disallows {crawler['token']} ({crawler['operator']}); the site drops out of that engine")
            elif crawler["role"] in ("ai-search", "ai-user"):
                report.add(origin, 0, "robots-blocks-ai-search", "warn",
                           f"robots.txt disallows {crawler['token']} ({crawler['operator']} {crawler['role']}); answers in {crawler['product']} cannot cite the site. Block only training crawlers if that is the intent")
    sitemaps = [line.split(":", 1)[1].strip() for line in text.splitlines() if line.lower().startswith("sitemap:")]
    if not sitemaps:
        report.add(origin, 0, "robots-sitemap-missing", "note", "robots.txt names no Sitemap:; add the absolute sitemap URL")
    for url in sitemaps:
        same_host = base_url is not None and urllib.parse.urlsplit(url).netloc == urllib.parse.urlsplit(base_url).netloc
        host = None if same_host else placeholder_host(url) or other_host(url, base_url)
        if host:
            report.add(origin, 0, "foreign-host-url", "fail", f"robots.txt Sitemap: {url} points at {host}, not the production host")
    return sitemaps


def sitemap_locations(document: ElementTree.Element) -> tuple[list[str], list[tuple[str, str | None]]]:
    children = [element.findtext(f"{SITEMAP_NAMESPACE}loc", "").strip() for element in document.findall(f"{SITEMAP_NAMESPACE}sitemap")]
    urls = [(element.findtext(f"{SITEMAP_NAMESPACE}loc", "").strip(), element.findtext(f"{SITEMAP_NAMESPACE}lastmod"))
            for element in document.findall(f"{SITEMAP_NAMESPACE}url")]
    return children, urls


def load_local_sitemaps(site: Site, start: list[str], report: Report) -> list[tuple[str, str | None]]:
    queue = [urllib.parse.urlsplit(url).path for url in start] or [f"/{name}" for name in SITEMAP_CANDIDATES if (site.root / name).exists()][:1]
    seen, entries = set(), []
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        file = site.root / path.lstrip("/")
        if not file.is_file():
            report.add(file, 0, "sitemap-missing", "warn", f"sitemap {path} is named but not in the build")
            continue
        try:
            document = ElementTree.fromstring(file.read_bytes())
        except ElementTree.ParseError as exc:
            report.add(file, 0, "sitemap-invalid", "fail", f"sitemap does not parse as XML ({exc}); engines reject it")
            continue
        children, urls = sitemap_locations(document)
        for child in children:
            host = placeholder_host(child) or other_host(child, site.base_url)
            if host:
                report.add(file, 0, "foreign-host-url", "fail", f"sitemap index lists {child} on {host}")
            queue.append(urllib.parse.urlsplit(child).path)
        entries.extend(urls)
    return entries


def check_sitemap_entries(entries, pages: list[Page], site: Site, served: dict[str, Path], report: Report, label: str) -> set:
    by_path = {page.url_path: page for page in pages}
    listed = set()
    for loc, _ in entries:
        host = placeholder_host(loc) or other_host(loc, site.base_url)
        if host:
            report.add(label, 0, "foreign-host-url", "fail", f"sitemap lists {loc} on {host}, not the production host")
            continue
        state, served_as = resolve(site, urllib.parse.urlsplit(loc).path, served)
        if state == "missing":
            report.add(label, 0, "sitemap-url-missing", "fail", f"sitemap lists {loc}, which matches no file in the build")
            continue
        if state == "redirect":
            report.add(label, 0, "sitemap-url-redirects", "warn",
                       f"sitemap lists {loc}, answered with a redirect under html_handling={site.html_handling}; list {served_as}")
        listed.add(served_as)
        page = by_path.get(served_as)
        if page and page.noindex:
            report.add(label, 0, "sitemap-url-noindex", "fail", f"sitemap lists {loc} but the page is noindex; pick one")
        elif page and page.canonicals:
            canonical = absolute(site.base_url, page.url_path, page.canonicals[0][0])
            if urllib.parse.urlsplit(canonical).path != urllib.parse.urlsplit(loc).path:
                report.add(label, 0, "sitemap-url-not-canonical", "warn", f"sitemap lists {loc} but that page's canonical is {canonical}")
    if entries:
        for page in pages:
            if not page.noindex and page.url_path not in listed:
                report.add(page.file, 0, "sitemap-omits-page", "note", f"{page.url_path} is indexable but not in the sitemap")
        lastmods = [lastmod for _, lastmod in entries if lastmod]
        if len(lastmods) >= UNIFORM_LASTMOD_MINIMUM and len(set(lastmods)) == 1:
            report.add(label, 0, "sitemap-lastmod-uniform", "note",
                       "every <lastmod> is identical (the build time); Google ignores lastmod it finds inaccurate, so emit real content dates or none")
    return listed


def check_home_identity(site: Site, pages: list[Page], served: dict[str, Path], report: Report):
    home_path = resolve(site, site.redirected.get("/", "/"), served)[1] or "/"
    home = next((page for page in pages if page.url_path == home_path), None)
    if home is None or home.noindex:
        return
    has_raster_icon = any(not href.lower().endswith(".svg") and "svg" not in kind for href, kind in home.icons)
    if not has_raster_icon and not (site.root / "favicon.ico").exists():
        report.add(home.file, 1, "favicon-unsupported", "note",
                   "no favicon Google accepts (its formats are BMP, GIF, ICO, PNG, JPEG, PPM and TIFF; SVG is not listed). Add favicon.ico or a PNG of at least 48x48 with rel=icon")
    websites = []
    for text, _ in home.jsonld:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        websites += [node for node in jsonld_nodes(data) if node.get("@type") == "WebSite" or (isinstance(node.get("@type"), list) and "WebSite" in node["@type"])]
    if not any(node.get("name") for node in websites):
        report.add(home.file, 1, "site-name-missing", "note",
                   "no WebSite JSON-LD with a name on the home page; Google takes the site name in results from it (falling back to guesses from the title)")


def check_edge_files(site: Site, pages: list[Page], header_rules: list, report: Report):
    for pattern, headers in header_rules:
        robots = headers.get("x-robots-tag", "").lower()
        if "noindex" in robots and pattern in ("/*", "/", "*"):
            report.add(site.root / "_headers", 0, "headers-noindex-all", "fail",
                       f"_headers sends X-Robots-Tag: {robots} on {pattern} for every host, production included; scope it to the mirror host")
    redirects = site.root / "_redirects"
    sources = {source: target for _, source, target, _ in parse_redirects_file(redirects)}
    for number, source, target, code in parse_redirects_file(redirects):
        if target in sources and target != source:
            report.add(redirects, number, "redirect-chain", "warn",
                       f"{source} → {target} → {sources[target]}: point {source} straight at the final URL")
        if code.rstrip("!") not in ("302", "303", "307"):
            continue
        if source == "/":
            report.add(redirects, number, "root-redirect-temporary", "note",
                       f"/ → {target} is {code}: Google does not take a temporary redirect as a canonical signal, so the root may stay the URL it shows. Use 301 if {target} is the permanent home; keep {code} only for a language chooser, with hreflang x-default on /")
        else:
            report.add(redirects, number, "redirect-temporary", "warn",
                       f"{source} → {target} is {code}; a moved page needs 301 or 308 so engines move its signals")
    if site.not_found_handling == "single-page-application" and len(pages) > 1:
        report.add(site.config_path or site.root, 0, "spa-fallback", "warn",
                   "not_found_handling is single-page-application on a multi-page site: every unknown URL answers 200 with the home page (soft 404s and duplicates); use 404-page")
    if site.not_found_handling != "single-page-application" and not (site.root / "404.html").exists():
        report.add(site.root, 0, "not-found-page-missing", "warn",
                   "no 404.html in the build; ship one and set not_found_handling = \"404-page\" so unknown URLs answer a real 404 with a way back")


def site_url_unset(pages: list[Page], site: Site, report: Report) -> str | None:
    placeholder_pages = [page for page in pages if any(placeholder_host(href) for href, _ in page.canonicals)]
    if not pages or len(placeholder_pages) * 2 < len(pages):
        return None
    host = placeholder_host(next(href for href, _ in placeholder_pages[0].canonicals if placeholder_host(href)))
    report.add(site.root, 0, "site-url-unset", "fail",
               f"{len(placeholder_pages)} of {len(pages)} pages name {host} in their canonical: the build ran without the production URL "
               "(Astro `site`, Hugo `baseURL`, Eleventy or Vite env), so canonicals, hreflang, og:url and the sitemap all point there. Set it and rebuild")
    return host


def scan_site(path: Path, base_url: str | None) -> Report:
    site, setup_findings = locate_site(path)
    report = Report(path.resolve())
    report.findings.extend(setup_findings)
    if site is None:
        return report
    report.root = site.root
    retired = load_data("rich-results.json")["retired"]
    crawlers = load_data("crawlers.json")["crawlers"]
    header_rules = parse_headers_file(site.root / "_headers")
    site.redirected = {source: target for _, source, target, code in parse_redirects_file(site.root / "_redirects")
                       if "*" not in source and ":" not in source and code.rstrip("!") != "200"}
    files = sorted(file for file in site.root.rglob("*.html") if file.name != "404.html")
    parsed = [parse_page(site, file, header_rules) for file in files]
    pages = [page for page in parsed if page.url_path not in site.redirected and not page.meta_refresh]
    for page in parsed:
        if page.meta_refresh and page.url_path not in site.redirected:
            report.add(page.file, 1, "meta-refresh-redirect", "note",
                       f"{page.url_path} redirects with a meta refresh; a _redirects rule with 301 answers before any HTML and moves signals reliably")
    if base_url:
        site.base_url = base_url.rstrip("/")
    site.base_url = infer_base_url(site, pages)
    served = {page.url_path: page.file for page in pages}
    robots_file = site.root / "robots.txt"
    sitemap_urls: list[str] = []
    if robots_file.exists():
        sitemap_urls = check_robots(robots_file.read_text(), str(robots_file.relative_to(site.root)), crawlers, report, site.base_url)
    else:
        report.add(site.root, 0, "robots-missing", "note",
                   "no robots.txt in the build; crawlers assume everything is allowed, and Cloudflare's managed robots.txt (if enabled) is all they see")
    entries = load_local_sitemaps(site, sitemap_urls, report)
    if not entries and not any(f.rule in ("sitemap-missing", "sitemap-invalid") for f in report.findings):
        report.add(site.root, 0, "sitemap-missing", "warn", "no sitemap in the build; add one (most SSGs have a plugin) and name it in robots.txt")
    listed = check_sitemap_entries(entries, pages, site, served, report, "sitemap") if entries else set()
    unset_host = site_url_unset(pages, site, report)
    for page in pages:
        check_page(page, site, served, retired, report, {p.url_path: p for p in pages})
    if unset_host:
        report.findings = [f for f in report.findings if not (f.rule == "foreign-host-url" and unset_host in f.message)]
    check_duplicates(pages, report)
    check_hreflang_clusters(pages, site, served, report)
    check_link_graph(pages, site, served, listed, report)
    check_home_identity(site, pages, served, report)
    check_edge_files(site, pages, header_rules, report)
    return report


@dataclass
class Response:
    url: str
    status: int | None
    headers: dict
    body: str
    error: str | None = None


def fetch(url: str, user_agent: str, timeout: float) -> Response:
    parts = urllib.parse.urlsplit(url)
    connection_class = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    options = {"timeout": timeout}
    if parts.scheme == "https":
        options["context"] = ssl.create_default_context()
    try:
        connection = connection_class(parts.netloc, **options)
        target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        connection.request("GET", target, headers={"User-Agent": user_agent, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
        response = connection.getresponse()
        headers = {name.lower(): value for name, value in response.getheaders()}
        body = response.read(2_000_000).decode("utf-8", errors="replace")
        connection.close()
        return Response(url, response.status, headers, body)
    except (socket.timeout, TimeoutError):
        return Response(url, None, {}, "", "timeout")
    except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
        return Response(url, None, {}, "", f"{type(exc).__name__}: {exc}")


def response_noindex(response: Response) -> bool:
    header = response.headers.get("x-robots-tag", "").lower()
    meta = re.search(r"<meta[^>]+name=[\"'](robots|googlebot)[\"'][^>]*content=[\"']([^\"']*)", response.body, re.I)
    return "noindex" in header or (meta is not None and "noindex" in meta.group(2).lower())


def follow_redirects(response: Response, timeout: float, hops: int = 3) -> Response:
    for _ in range(hops):
        location = response.headers.get("location")
        if response.status is None or not (300 <= response.status < 400) or not location:
            break
        response = fetch(urllib.parse.urljoin(response.url, location), BROWSER_USER_AGENT, timeout)
    return response


def check_live_preview_image(home: Response, timeout: float, report: Report):
    page = follow_redirects(home, timeout)
    match = re.search(r"<meta[^>]+property=[\"']og:image[\"'][^>]*content=[\"']([^\"']+)", page.body, re.I)
    if not match:
        return
    image_url = urllib.parse.urljoin(page.url, match.group(1))
    image = follow_redirects(fetch(image_url, BROWSER_USER_AGENT, timeout), timeout)
    if image.status != 200:
        report.add(image_url, 0, "live-og-image-broken", "fail",
                   f"the home page's og:image answers {image.status or image.error}; every link preview shows no image")
    elif len(image.body.encode("utf-8", errors="replace")) > PREVIEW_IMAGE_BUDGET_BYTES or int(image.headers.get("content-length", "0") or 0) > PREVIEW_IMAGE_BUDGET_BYTES:
        report.add(image_url, 0, "live-og-image-heavy", "note",
                   "og:image is over 600 KB; WhatsApp drops previews above that, so aim for 1200x630 under 600 KB")


def scan_live(url: str, mirrors: list[str], sample: int, timeout: float) -> Report:
    parts = urllib.parse.urlsplit(url if "://" in url else f"https://{url}")
    origin = f"{parts.scheme}://{parts.netloc}"
    report = Report(Path("."))
    crawlers = load_data("crawlers.json")["crawlers"]
    home = fetch(origin + "/", BROWSER_USER_AGENT, timeout)
    if home.status is None:
        report.add(origin, 0, "live-unreachable", "fail", f"{origin}/ did not answer: {home.error}")
        return report
    if response_noindex(home):
        report.add(origin + "/", 0, "live-noindex", "fail", "the live home page is noindex (header or meta); production is hidden from every engine")
    check_live_preview_image(home, timeout, report)
    robots = fetch(origin + "/robots.txt", BROWSER_USER_AGENT, timeout)
    sitemaps: list[str] = []
    if robots.status is not None and robots.status >= 500:
        report.add(origin + "/robots.txt", 0, "live-robots-error", "fail",
                   f"robots.txt answers {robots.status}; Google treats a 5xx robots.txt as disallow-all and stops crawling")
    elif robots.status == 200:
        sitemaps = check_robots(robots.body, origin + "/robots.txt", crawlers, report, origin)
        if CLOUDFLARE_MANAGED_MARKER in robots.body:
            report.add(origin + "/robots.txt", 0, "live-robots-managed", "note",
                       "Cloudflare prepends its managed robots.txt here; the rules above include its AI-crawler blocks and Content-Signal line, which your repository's robots.txt does not show")
        signals = re.findall(r"^\s*Content-Signal:\s*(.+)$", robots.body, re.I | re.M)
        if signals:
            report.add(origin + "/robots.txt", 0, "live-content-signals", "note", f"Content-Signal: {'; '.join(s.strip() for s in signals)}")
    for crawler in crawlers:
        agent = crawler.get("probe_user_agent")
        if not agent:
            continue
        probe = fetch(origin + "/", agent, timeout)
        if probe.status not in BLOCKING_STATUSES or home.status in BLOCKING_STATUSES:
            continue
        severity = {"search": "fail", "ai-search": "warn", "ai-user": "warn"}.get(crawler["role"], "note")
        consequence = f"{crawler['product']} cannot fetch the site"
        if crawler["role"] == "ai-training":
            on_cloudflare = home.headers.get("server", "").lower() == "cloudflare"
            preference_published = robots.status == 200 and CLOUDFLARE_MANAGED_MARKER in robots.body and "google-extended" in robots.body.lower()
            if on_cloudflare and not preference_published:
                severity = "warn"
                consequence = ("blocked at the edge with no Cloudflare-managed training preference in robots.txt. If that is the AI bot policy "
                               "Training = Block (or Block on pages with ads, or the legacy Block AI bots), it has also stopped verified Googlebot, "
                               "Bingbot and Applebot since 2026-09-15; use Disallow AI Training instead")
            else:
                consequence = "a policy choice for a training crawler; search and answer engines use separate crawlers"
        report.add(origin + "/", 0, "live-crawler-blocked", severity,
                   f"{crawler['token']} user agent gets {probe.status} where a browser gets {home.status}: {consequence}. "
                   "Look at Cloudflare AI Crawl Control, Bot Fight Mode and WAF rules; a spoofed user agent can also be refused as fake, so confirm in Security Events")
    explicit = bool(sitemaps)
    queue = sitemaps or [origin + "/" + name for name in SITEMAP_CANDIDATES]
    sampled, index = 0, 0
    while index < len(queue):
        sitemap = queue[index]
        index += 1
        response = fetch(sitemap, BROWSER_USER_AGENT, timeout)
        if response.status != 200:
            if explicit:
                report.add(sitemap, 0, "live-sitemap-unreachable", "warn", f"sitemap answers {response.status or response.error}")
            continue
        try:
            document = ElementTree.fromstring(response.body.encode())
        except ElementTree.ParseError:
            if explicit:
                report.add(sitemap, 0, "live-sitemap-unreachable", "warn", "sitemap does not parse as XML")
            continue
        children, urls = sitemap_locations(document)
        if not explicit:
            explicit, queue = True, queue[:index]
        queue.extend(child for child in children if child not in queue)
        for loc, _ in urls[: max(0, sample - sampled)]:
            sampled += 1
            probe = fetch(loc, BROWSER_USER_AGENT, timeout)
            if probe.status is None or probe.status >= 400:
                report.add(loc, 0, "live-sitemap-url-error", "fail", f"sitemap URL answers {probe.status or probe.error}")
            elif 300 <= probe.status < 400:
                report.add(loc, 0, "live-sitemap-url-redirects", "warn", f"sitemap URL redirects ({probe.status}) to {probe.headers.get('location')}")
            elif response_noindex(probe):
                report.add(loc, 0, "live-sitemap-url-noindex", "fail", "sitemap URL is noindex")
    for mirror in mirrors:
        mirror_url = (mirror if "://" in mirror else f"https://{mirror}").rstrip("/") + "/"
        probe = fetch(mirror_url, BROWSER_USER_AGENT, timeout)
        for _ in range(3):
            location = probe.headers.get("location")
            if probe.status is None or not (300 <= probe.status < 400) or not location:
                break
            next_url = urllib.parse.urljoin(probe.url, location)
            if urllib.parse.urlsplit(next_url).netloc != urllib.parse.urlsplit(mirror_url).netloc:
                break
            probe = fetch(next_url, BROWSER_USER_AGENT, timeout)
        if probe.status != 200 or response_noindex(probe):
            continue
        canonical = re.search(r"<link[^>]+rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)", probe.body, re.I)
        canonical_host = urllib.parse.urlsplit(canonical.group(1)).netloc if canonical else ""
        if canonical_host and canonical_host != urllib.parse.urlsplit(mirror_url).netloc:
            report.add(probe.url, 0, "live-mirror-canonical-only", "note",
                       f"mirror serves 200 without noindex and relies on its canonical to {canonical_host}; a canonical is a hint, so gate the mirror with Access or send X-Robots-Tag: noindex")
        else:
            report.add(probe.url, 0, "live-mirror-indexable", "warn",
                       "mirror serves 200 without noindex or a canonical to production; it can be indexed as a duplicate. Disable it, gate it with Access, redirect it, or send X-Robots-Tag: noindex")
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
    lines = [f"{f.severity:5} {f.rule:26} {f.path}{':' + str(f.line) if f.line else ''}  {f.message}"
             + (f" (+{len(f.also)} more: {', '.join(f.also[:3])}{', …' if len(f.also) > 3 else ''})" if f.also else "") for f in findings]
    counts = Counter(f.severity for f in findings)
    lines.append(f"\n{counts['fail']} fail, {counts['warn']} warn, {counts['note']} note")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modes = parser.add_subparsers(dest="mode", required=True)
    site_mode = modes.add_parser("site")
    site_mode.add_argument("path", type=Path)
    site_mode.add_argument("--base-url")
    live_mode = modes.add_parser("live")
    live_mode.add_argument("url")
    live_mode.add_argument("--mirror", action="append", default=[])
    live_mode.add_argument("--sample", type=int, default=20)
    live_mode.add_argument("--timeout", type=float, default=15)
    for mode in (site_mode, live_mode):
        mode.add_argument("--json", action="store_true")
        mode.add_argument("--fail-on", choices=list(SEVERITY_RANK), default="fail")
    args = parser.parse_args()
    report = scan_site(args.path, args.base_url) if args.mode == "site" else scan_live(args.url, args.mirror, args.sample, args.timeout)
    print(render(report, args.json))
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[f.severity] >= threshold for f in report.findings) else 0


if __name__ == "__main__":
    sys.exit(main())

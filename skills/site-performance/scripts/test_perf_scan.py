import base64
import gzip
import importlib.util
import json
import os
import socket
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

spec = importlib.util.spec_from_file_location("perf_scan", Path(__file__).resolve().parent / "perf_scan.py")
perf_scan = importlib.util.module_from_spec(spec)
sys.modules["perf_scan"] = perf_scan
spec.loader.exec_module(perf_scan)

BUDGETS = {"js": 100 * 1024, "css": 50 * 1024, "hero": 200 * 1024}


def incompressible(size: int) -> bytes:
    return base64.b64encode(os.urandom(size))[:size]


def careless_site(root: Path):
    dist = root / "dist"
    for directory in ("_astro", "media", "fonts"):
        (dist / directory).mkdir(parents=True)
    (root / "wrangler.toml").write_text('name = "careless"\n[assets]\ndirectory = "./dist"\n')
    (dist / "_headers").write_text("/*\n  Cache-Control: no-store\n")
    (dist / "media" / "hero.jpg").write_bytes(b"\xff\xd8\xff" + incompressible(260 * 1024))
    (dist / "media" / "gallery.png").write_bytes(b"\x89PNG" + incompressible(320 * 1024))
    (dist / "_astro" / "app.Bk3LmQ9x.js").write_bytes(b"window.addEventListener('unload',()=>{});" + incompressible(180 * 1024))
    (dist / "_astro" / "styles.Cq8ZpT2a.css").write_bytes(
        b"@import url('/_astro/extra.css');@font-face{font-family:Brand;src:url(/fonts/brand.woff2) format('woff2')}"
        b"@font-face{font-family:Old;font-display:swap;src:url(/fonts/old.ttf) format('truetype')}" + incompressible(90 * 1024))
    (dist / "_astro" / "theme.Dz4KmP8q.js").write_bytes(incompressible(4096))
    for name in ("brand.woff2", "brand-bold.woff2", "brand-italic.woff2"):
        (dist / "fonts" / name).write_bytes(b"wOF2" + b"\x00" * 100)
    (dist / "index.html").write_text("""<!doctype html>
<html lang="en">
<head>
<title>Careless</title>
<link rel="preload" href="/fonts/brand.woff2" as="font">
<link rel="preload" href="/fonts/brand-bold.woff2" as="font" crossorigin>
<link rel="preload" href="/fonts/brand-italic.woff2" as="font" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">
<link rel="stylesheet" href="/_astro/styles.Cq8ZpT2a.css">
<script src="/_astro/theme.Dz4KmP8q.js"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
</head>
<body>
<main>
<img src="/media/hero.jpg" alt="Hero" loading="lazy">
<img src="/media/gallery.png" alt="Gallery" width="1600" height="900">
<iframe src="https://www.youtube.com/embed/abc"></iframe>
<img data-src="/media/late.jpg" alt="Late" width="10" height="10">
<img src="/media/card.jpg" srcset="/media/card-400.jpg 400w, /media/card-800.jpg 800w" alt="Card" width="800" height="450">
<astro-island uid="a1" component-url="/_astro/Widget.Cx8kLm2P.js" client="only"></astro-island>
""" + "<span></span>" * 1600 + """
<video src="/media/clip.mp4" controls></video>
</main>
<script type="module" src="/_astro/app.Bk3LmQ9x.js"></script>
</body>
</html>
""")


def rules(report):
    return {finding.rule for finding in report.findings}


class JsLoadedHeroTest(unittest.TestCase):
    def test_first_image_with_only_data_src(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text('<html><body><main><img data-src="/hero.jpg" alt="" width="1200" height="600"></main></body></html>')
            self.assertIn("lcp-image-js-loaded", rules(perf_scan.scan_site(root, BUDGETS)))


class SiteTest(unittest.TestCase):
    def test_careless_site_fires_every_site_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            careless_site(root)
            self.assertEqual(rules(perf_scan.scan_site(root, BUDGETS)), {
                "lcp-image-lazy", "lcp-image-not-prioritized", "lcp-image-heavy", "lcp-image-legacy-format",
                "img-dimensions-missing", "image-heavy", "embed-dimensions-missing", "embed-not-lazy",
                "render-blocking-script", "js-over-budget", "css-over-budget", "heavy-third-party",
                "font-preload-no-crossorigin", "font-preload-many", "font-third-party", "font-display-missing",
                "unload-handler", "html-no-store", "assets-not-immutable", "srcset-without-sizes",
                "astro-client-only", "dom-size-large", "css-import", "font-not-woff2",
            })

    def test_missing_build_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wrangler.jsonc").write_text('{"name": "x", "assets": {"directory": "./dist"}}')
            self.assertEqual(rules(perf_scan.scan_site(root, BUDGETS)), {"build-missing"})

    def test_hash_detection(self):
        for name in ("BaseLayout.Cz39HSr8.css", "index-BxS3_9kP.js", "main.3f9a1c2b7d4e5f60a1b2.css"):
            self.assertTrue(perf_scan.is_hashed(name), name)
        for name in ("lockup-horizontal-512.png", "avatar-1024.png", "favicon.ico", "cards-2026.png"):
            self.assertFalse(perf_scan.is_hashed(name), name)


def serve(routes):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.do_GET()

        def do_GET(self):
            length = int(self.headers.get("Content-Length") or 0)
            self.headers["X-Body"] = self.rfile.read(length).decode() if length else ""
            status, headers, body = routes(self.path, self.headers)
            self.send_response(status)
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def slow_uncompressed_site(path, headers):
    if path == "/":
        perf_scan.time.sleep(0.9)
        return 200, {"Content-Type": "text/html", "Cache-Control": "no-store"}, b'<link rel="stylesheet" href="/_astro/site.Cz39HSr8.css">'
    if path == "/_astro/site.Cz39HSr8.css":
        return 200, {"Content-Type": "text/css", "Cache-Control": "public, max-age=0, must-revalidate"}, b"body{}"
    return 404, {}, b""


def tidy_site(path, headers):
    body = b"<html><body>fast</body></html>"
    return 200, {"Content-Type": "text/html", "Content-Encoding": "gzip", "Alt-Svc": 'h3=":443"'}, gzip.compress(body)


def crux(path, headers):
    query = json.loads(headers["X-Body"])
    if "url" in query:
        return 404, {"Content-Type": "application/json"}, b'{"error": {"code": 404, "message": "chrome ux report data not found"}}'
    metrics = {
        "largest_contentful_paint": {"percentiles": {"p75": 4300}},
        "interaction_to_next_paint": {"percentiles": {"p75": 260}},
        "cumulative_layout_shift": {"percentiles": {"p75": "0.04"}},
    }
    return 200, {"Content-Type": "application/json"}, json.dumps({"record": {"metrics": metrics}}).encode()


def closed_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class LiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = [serve(handler) for handler in (slow_uncompressed_site, tidy_site, crux)]
        cls.origins = [f"http://127.0.0.1:{server.server_address[1]}" for server in cls.servers]
        perf_scan.CRUX_ENDPOINT = cls.origins[2] + "/v1/records:queryRecord"
        os.environ["CRUX_API_KEY"] = "test-key"

    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.shutdown()
            server.server_close()

    def test_slow_uncompressed_uncached_site(self):
        self.assertEqual(rules(perf_scan.scan_live(self.origins[0], False, "phone", 5)), {
            "ttfb-slow", "html-uncompressed", "html-no-store", "http3-missing", "asset-uncompressed", "assets-not-immutable",
        })

    def test_field_data_from_origin_when_page_has_none(self):
        report = perf_scan.scan_live(self.origins[1], True, "phone", 5)
        self.assertEqual(rules(report), {"field-data-missing", "field-metric-poor", "field-metric-needs-improvement"})
        poor = next(f for f in report.findings if f.rule == "field-metric-poor")
        self.assertIn("origin LCP p75 is 4.3 s", poor.message)

    def test_field_without_key(self):
        os.environ.pop("CRUX_API_KEY")
        try:
            self.assertIn("field-unavailable", rules(perf_scan.scan_live(self.origins[1], True, "phone", 5)))
        finally:
            os.environ["CRUX_API_KEY"] = "test-key"

    def test_field_api_down(self):
        perf_scan.CRUX_ENDPOINT = f"http://127.0.0.1:{closed_port()}/v1/records:queryRecord"
        try:
            self.assertIn("field-unavailable", rules(perf_scan.scan_live(self.origins[1], True, "phone", 5)))
        finally:
            perf_scan.CRUX_ENDPOINT = self.origins[2] + "/v1/records:queryRecord"

    def test_unreachable(self):
        self.assertEqual(rules(perf_scan.scan_live(f"http://127.0.0.1:{closed_port()}", False, "phone", 5)), {"live-unreachable"})


if __name__ == "__main__":
    unittest.main()

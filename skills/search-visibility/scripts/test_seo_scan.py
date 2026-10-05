import importlib.util
import socket
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

spec = importlib.util.spec_from_file_location("seo_scan", Path(__file__).resolve().parent / "seo_scan.py")
seo_scan = importlib.util.module_from_spec(spec)
sys.modules["seo_scan"] = seo_scan
spec.loader.exec_module(seo_scan)

PAGE = "<!doctype html><html lang=\"en\"><head><title>t</title>{head}</head><body><p>text</p></body></html>"


def serve(routes):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            agent = self.headers.get("User-Agent", "")
            status, headers, body = routes(self.path, agent, self.server.server_address[1])
            self.send_response(status)
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def troubled_site(path, agent, port):
    origin = f"http://127.0.0.1:{port}"
    if path == "/":
        if "GPTBot" in agent or "OAI-SearchBot" in agent:
            return 403, {}, "blocked"
        return 200, {"Content-Type": "text/html"}, PAGE.format(head='<meta name="robots" content="noindex"><meta property="og:image" content="/card-gone.png">')
    if path == "/robots.txt":
        return 200, {"Content-Type": "text/plain"}, (
            "# BEGIN Cloudflare Managed content\nUser-agent: *\nContent-Signal: search=yes, ai-train=no\nAllow: /\n"
            f"# END Cloudflare Managed Content\n\nSitemap: {origin}/sitemap.xml\nSitemap: {origin}/missing.xml\n")
    if path == "/sitemap.xml":
        urls = "".join(f"<url><loc>{origin}{p}</loc></url>" for p in ("/ok", "/gone", "/moved", "/hidden"))
        return 200, {"Content-Type": "application/xml"}, f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    if path == "/heavy.png":
        return 200, {"Content-Type": "image/png"}, "x" * (700 * 1024)
    if path == "/ok":
        return 200, {"Content-Type": "text/html"}, PAGE.format(head="")
    if path == "/moved":
        return 301, {"Location": f"{origin}/ok"}, ""
    if path == "/hidden":
        return 200, {"Content-Type": "text/html", "X-Robots-Tag": "noindex"}, PAGE.format(head="")
    return 404, {}, "not found"


def mirror(path, agent, port):
    if path == "/":
        return 302, {"Location": "/home"}, ""
    if path == "/home":
        return 200, {"Content-Type": "text/html"}, PAGE.format(head="")
    if path == "/canonical-only/":
        return 200, {"Content-Type": "text/html"}, PAGE.format(head='<link rel="canonical" href="https://production.invalid/">')
    return 404, {}, ""


def broken_robots(path, agent, port):
    if path == "/robots.txt":
        return 503, {}, "unavailable"
    if path == "/heavy.png":
        return 200, {"Content-Type": "image/png"}, "x" * (700 * 1024)
    return 200, {"Content-Type": "text/html"}, PAGE.format(head='<meta property="og:image" content="/heavy.png">')


def closed_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def rules(report):
    return {finding.rule for finding in report.findings}


class LiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = [serve(handler) for handler in (troubled_site, mirror, broken_robots)]
        cls.origins = [f"http://127.0.0.1:{server.server_address[1]}" for server in cls.servers]

    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.shutdown()

    def test_troubled_site_and_mirrors(self):
        site, mirror_origin, _ = self.origins
        report = seo_scan.scan_live(site, [mirror_origin, f"{mirror_origin}/canonical-only"], 10, 5)
        self.assertEqual(rules(report), {
            "live-noindex", "live-robots-managed", "live-content-signals", "live-crawler-blocked",
            "live-sitemap-unreachable", "live-sitemap-url-error", "live-sitemap-url-redirects",
            "live-sitemap-url-noindex", "live-mirror-indexable", "live-mirror-canonical-only", "live-og-image-broken",
        })
        severities = {f.message.split()[0]: f.severity for f in report.findings if f.rule == "live-crawler-blocked"}
        self.assertEqual(severities, {"OAI-SearchBot": "warn", "GPTBot": "note"})

    def test_robots_5xx_is_disallow_all(self):
        self.assertEqual(rules(seo_scan.scan_live(self.origins[2], [], 5, 5)), {"live-robots-error", "live-og-image-heavy"})

    def test_unreachable_host(self):
        self.assertEqual(rules(seo_scan.scan_live(f"http://127.0.0.1:{closed_port()}", [], 5, 5)), {"live-unreachable"})


class RobotsTest(unittest.TestCase):
    def test_specific_group_overrides_star(self):
        groups = seo_scan.parse_robots("User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n")
        self.assertFalse(seo_scan.robots_blocks(groups, "Googlebot"))
        self.assertTrue(seo_scan.robots_blocks(groups, "Bingbot"))

    def test_longest_match_and_allow_tie(self):
        groups = seo_scan.parse_robots("User-agent: *\nDisallow: /\nAllow: /$\n")
        self.assertFalse(seo_scan.robots_blocks(groups, "Bingbot", "/"))
        self.assertTrue(seo_scan.robots_blocks(groups, "Bingbot", "/about"))

    def test_grouped_user_agents_share_rules(self):
        groups = seo_scan.parse_robots("User-agent: GPTBot\nUser-agent: ClaudeBot\nDisallow: /\n")
        self.assertTrue(seo_scan.robots_blocks(groups, "ClaudeBot"))
        self.assertFalse(seo_scan.robots_blocks(groups, "Claude-SearchBot"))


class SizeLimitTest(unittest.TestCase):
    def test_page_over_googlebot_fetch_limit(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            filler = "<!-- " + "x" * (seo_scan.GOOGLEBOT_FETCH_LIMIT_BYTES + 1024) + " -->"
            (root / "index.html").write_text(f"<!doctype html><html lang=\"en\"><head><title>Big</title></head><body>{filler}</body></html>")
            self.assertIn("html-over-limit", rules(seo_scan.scan_site(root, "https://big.invalid")))


class ServedPathTest(unittest.TestCase):
    def test_html_handling_modes(self):
        root = Path("/site")
        cases = {
            "auto-trailing-slash": {"index.html": "/", "about.html": "/about", "docs/index.html": "/docs/"},
            "force-trailing-slash": {"about.html": "/about/", "docs/index.html": "/docs/"},
            "drop-trailing-slash": {"about.html": "/about", "docs/index.html": "/docs"},
        }
        for mode, expected in cases.items():
            site = seo_scan.Site(root, mode)
            for file, served in expected.items():
                self.assertEqual(seo_scan.served_path(site, root / file), served, f"{mode} {file}")


if __name__ == "__main__":
    unittest.main()

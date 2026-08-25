from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.vault import (
    DownloadError,
    ResourceVault,
    clean_filename,
    content_disposition_filename,
)

PDF = b"%PDF-1.4\n% small fixture\n%%EOF\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/robots.txt":
            self.respond(b"User-agent: *\nAllow: /\n", "text/plain")
        elif self.path == "/page":
            self.respond(b'<a href="/file.pdf?download=1">PDF</a><a href="mailto:a@b.test">mail</a>', "text/html")
        elif self.path.startswith("/file.pdf"):
            self.respond(PDF, "application/pdf", {"ETag": '"fixture"'})
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/named")
            self.end_headers()
        elif self.path == "/named":
            self.respond(PDF, "application/pdf", {"Content-Disposition": "attachment; filename*=UTF-8''sample%20test.pdf"})
        elif self.path == "/fake.pdf":
            self.respond(b"<!doctype html><html>login</html>", "text/html")
        else:
            self.send_error(404)

    def respond(self, body, mime, extra=None):
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


class VaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.vault = ResourceVault(Path(self.temp.name) / "vault", obey_robots=True)

    def tearDown(self):
        self.vault.close()
        self.temp.cleanup()

    def test_discover_query_string_and_download(self):
        urls = self.vault.discover(self.base + "/page")
        self.assertEqual(urls, [self.base + "/file.pdf?download=1"])
        result = self.vault.add(urls[0], referrer=self.base + "/page")
        self.assertEqual(result.mime_type, "application/pdf")
        self.assertTrue((self.vault.root / result.local_path).exists())

    def test_redirect_content_disposition_and_dedup(self):
        first = self.vault.add(self.base + "/redirect")
        second = self.vault.add(self.base + "/file.pdf")
        self.assertEqual(first.filename, "sample test.pdf")
        self.assertEqual(first.sha256, second.sha256)
        self.assertTrue(second.duplicate)
        manifest = json.loads(self.vault.manifest_path.read_text())
        self.assertEqual(len(manifest["resources"]), 2)
        self.assertEqual(len(list(self.vault.files_dir.rglob("*.pdf"))), 1)

    def test_html_masquerading_as_pdf_is_rejected(self):
        with self.assertRaises(DownloadError):
            self.vault.add(self.base + "/fake.pdf")
        self.assertEqual(list(self.vault.temp_dir.iterdir()), [])

    def test_manifest_rebuild(self):
        self.vault.add(self.base + "/file.pdf")
        self.vault.index_path.unlink()
        data = self.vault.rebuild_manifest()
        self.assertEqual(len(data["resources"]), 1)
        self.assertEqual(len(self.vault.index_path.read_text().splitlines()), 1)

    def test_filename_safety(self):
        self.assertEqual(clean_filename("../../bad:name.pdf"), "bad_name.pdf")
        self.assertEqual(content_disposition_filename("attachment; filename*=UTF-8''hello%20world.pdf"), "hello world.pdf")


if __name__ == "__main__":
    unittest.main()

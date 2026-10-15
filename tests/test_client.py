import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock

from ternwire import TernwireClient

API_KEY = "em_test_origincheck"
PAGE = b'{"data":[],"page":{"nextCursor":null,"hasMore":false}}'


def recording_server(seen):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.headers["Authorization"])
            self.send_response(200)
            self.send_header("Content-Length", str(len(PAGE)))
            self.end_headers()
            self.wfile.write(PAGE)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class BaseUrlTransportTest(unittest.TestCase):
    def test_rejects_cleartext_non_loopback_origins(self):
        for base_url in ("http://api.example.com", "http://10.0.0.5:3001", "http://api:3001",
                         "http://localhost.example.com", "http://127.0.0.1.nip.io",
                         "http://[::2]"):
            with self.subTest(base_url=base_url), self.assertRaisesRegex(ValueError, "must use https"):
                TernwireClient(API_KEY, base_url)

    def test_accepts_https_and_loopback_origins(self):
        for base_url in ("https://api.example.com", "http://localhost:3001",
                         "http://LOCALHOST:3001", "http://api.localhost:3001",
                         "http://127.10.20.30", "http://[::1]:3001"):
            with self.subTest(base_url=base_url):
                TernwireClient(API_KEY, base_url)

    def test_loopback_client_sends_the_key(self):
        seen = []

        class Handler(BaseHTTPRequestHandler):
            def do_DELETE(self):
                seen.append(self.headers["Authorization"])
                self.send_response(204)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            client = TernwireClient(API_KEY, f"http://127.0.0.1:{server.server_port}")
            self.assertIsNone(client.delete_email_template("tpl_00000001"))
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(seen, [f"Bearer {API_KEY}"])

    def test_list_email_templates_sends_cursor_and_limit(self):
        paths = []
        page = b'{"data":[],"page":{"nextCursor":null,"hasMore":false}}'

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                paths.append(self.path)
                self.send_response(200)
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            client = TernwireClient(API_KEY, f"http://127.0.0.1:{server.server_port}")
            result = client.list_email_templates(cursor="c+/= x", limit=10)
            client.list_email_templates()
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(result, {"data": [], "page": {"nextCursor": None, "hasMore": False}})
        self.assertEqual(paths, ["/v1/templates?cursor=c%2B%2F%3D+x&limit=10", "/v1/templates"])

    def test_loopback_client_ignores_environment_proxies(self):
        api_seen, proxy_seen = [], []
        api, proxy = recording_server(api_seen), recording_server(proxy_seen)
        proxy_url = f"http://127.0.0.1:{proxy.server_port}"
        environment = {"http_proxy": proxy_url, "HTTP_PROXY": proxy_url,
                       "all_proxy": proxy_url, "ALL_PROXY": proxy_url,
                       "no_proxy": "", "NO_PROXY": ""}
        try:
            with mock.patch.dict(os.environ, environment):
                for host in ("127.0.0.1", "localhost"):
                    with self.subTest(host=host):
                        TernwireClient(API_KEY, f"http://{host}:{api.server_port}").list_email_templates()
        finally:
            for server in (api, proxy):
                server.shutdown()
                server.server_close()
        self.assertEqual(proxy_seen, [])
        self.assertEqual(api_seen, [f"Bearer {API_KEY}"] * 2)


if __name__ == "__main__":
    unittest.main()

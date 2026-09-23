"""The client must report what the server did, including the ugly parts."""
from __future__ import annotations

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from jevcompat.client import Client, Timeout, TransportError


def serve(handler_fn):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):  # noqa: N802
            handler_fn(self)

        do_GET = do_POST  # noqa: N815
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def test_redirect_is_returned_not_followed():
    def h(self):
        self.send_response(301)
        self.send_header("Location", "https://example.invalid/v1/systemone")
        self.send_header("Content-Length", "0")
        self.end_headers()
    srv, url = serve(h)
    try:
        r = Client(url).post_json("/v1/systemone", {"a": 1})
        assert r.status == 301 and r.headers["location"].startswith("https://")
    finally:
        srv.shutdown()


def test_truncated_body_is_a_transport_error_not_a_crash():
    def h(self):
        self.send_response(200)
        self.send_header("Content-Length", "500")
        self.end_headers()
        self.wfile.write(b'{"partial": ')
        self.wfile.flush()
        self.connection.shutdown(socket.SHUT_RDWR)
    srv, url = serve(h)
    try:
        with pytest.raises(TransportError):
            Client(url).post_json("/v1/systemone", {"a": 1})
    finally:
        srv.shutdown()


def test_timeout_is_its_own_kind():
    def h(self):
        time.sleep(2)
    srv, url = serve(h)
    try:
        with pytest.raises(Timeout):
            Client(url, timeout=0.3).post_json("/v1/systemone", {"a": 1})
    finally:
        srv.shutdown()


def test_nan_and_deep_nesting_are_recorded():
    from jevcompat.client import parse_json
    value, err, nonfinite = parse_json(b'{"x": NaN, "y": -Infinity}')
    assert err is None and sorted(nonfinite) == ["-Infinity", "NaN"]
    _, err, _ = parse_json(b"[" * 100000 + b"]" * 100000)
    assert err and "nested" in err

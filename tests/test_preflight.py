"""The preflight must not blame a requirement it has not proven."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from jevcompat import runner


def serve(post, get=None):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _reply(self, status, body):
            raw = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):  # noqa: N802
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            self._reply(*post(body))

        def do_GET(self):  # noqa: N802
            self._reply(*(get() if get else (404, {"detail": "no"})))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def failed(rep):
    return [r.id for r in rep.results if r.status == "fail"]


def test_warming_up_server_is_not_blamed():
    srv, url = serve(lambda b: (503, {"detail": {"error_type": "overloaded", "message": "warming up"}}))
    try:
        rep = runner.run(url, sdk=False, timeout=5)
    finally:
        srv.shutdown()
    assert rep.verdict == "not tested" and "not ready" in rep.aborted and failed(rep) == []


def test_an_unrelated_rejection_is_not_blamed_on_the_model_name():
    """A server that only rejects noul questions without criteria: no model-alias finding."""
    def post(body):
        q = next(iter((body.get("questions") or {}).values()), {})
        if q.get("type") == "noul" and not q.get("criteria"):
            return 400, {"detail": {"error_type": "bad_request", "message": "noul needs criteria"}}
        return 200, {}
    get = lambda: (200, {"models": [{"name": "local", "description": "x", "release_date": "2026-09-20"}]})  # noqa: E731
    srv, url = serve(post, get)
    try:
        rep = runner.run(url, sdk=False, timeout=5)
    finally:
        srv.shutdown()
    assert rep.verdict == "not tested" and "rejects a minimal valid request" in rep.aborted
    assert failed(rep) == []


def test_missing_route_is_http_endpoint():
    srv, url = serve(lambda b: (404, {"detail": "Not Found"}))
    try:
        rep = runner.run(url, sdk=False, timeout=5)
    finally:
        srv.shutdown()
    assert failed(rep) == ["http.endpoint"]


def test_404_without_the_word_model_still_tries_a_listed_model():
    def post(body):
        if body.get("model") == "jev-latest":
            return 404, {"detail": "unknown engine 'jev-latest'"}
        return 200, {"model": "local", "answers": {k: {"type": "noul", "noul": 0.5} for k in body["questions"]},
                     "usage": {"input_tokens": 1, "output_tokens": 1}}
    get = lambda: (200, {"models": [{"name": "local", "description": "x", "release_date": "2026-09-20"}]})  # noqa: E731
    srv, url = serve(post, get)
    try:
        rep = runner.run(url, sdk=False, timeout=5, only=set())
    finally:
        srv.shutdown()
    assert failed(rep) == ["request.model-alias"] and rep.info["model_fallback"] == "local"

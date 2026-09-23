"""A deliberately plain HTTP client.

A conformance tool must see exactly what the server sent: no retries, no redirects followed
silently, no JSON leniency. Python's json module accepts NaN and Infinity, which are not JSON,
so parsing records them instead of hiding them (SPEC.md response.finite).
"""
from __future__ import annotations

import http.client
import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from . import __version__

USER_AGENT = f"jevcompat/{__version__} (+https://github.com/mandu5/jevcompat)"
DUMMY_KEY = "jevcompat-no-key"
MAX_BODY = 16 * 1024 * 1024


class TransportError(Exception):
    """The request never produced a complete HTTP response (refused, reset, truncated)."""


class Timeout(TransportError):
    """No response within the client's timeout: inconclusive, since the limit is ours."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return 3xx as the response. Following it would turn a POST into a GET behind our back."""

    def redirect_request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes
    ms: float
    data: Any = None
    json_error: str | None = None
    nonfinite: list[str] = field(default_factory=list)

    @property
    def is_json(self) -> bool:
        return self.json_error is None

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")

    def excerpt(self, limit: int = 400) -> str:
        text = self.body.decode("utf-8", errors="replace")
        return text if len(text) <= limit else text[:limit] + f"… ({len(self.body)} bytes)"


def parse_json(body: bytes) -> tuple[Any, str | None, list[str]]:
    """(value, error, non-finite constants seen)."""
    seen: list[str] = []

    def constant(name: str) -> float:
        seen.append(name)
        return float(name.replace("Infinity", "inf"))

    try:
        return json.loads(body.decode("utf-8"), parse_constant=constant), None, seen
    except UnicodeDecodeError as e:
        return None, f"body is not UTF-8: {e}", seen
    except json.JSONDecodeError as e:
        return None, f"body is not JSON: {e}", seen
    except RecursionError:
        return None, "body is JSON nested too deeply to parse", seen


class Client:
    def __init__(self, base_url: str, key: str | None = None, model: str = "jev-latest", timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.key = key
        self.model = model
        self.timeout = timeout

    def request(self, method: str, path: str, body: bytes | None = None, *,
                auth: str | None | bool = True, headers: dict[str, str] | None = None) -> Response:
        """auth=True sends the configured key (or a dummy one, as SDKs always send a header);
        auth=False sends no Authorization header; a string sends that key."""
        h = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if body is not None:
            h["Content-Type"] = "application/json"
        if auth is True:
            h["Authorization"] = f"Bearer {self.key or DUMMY_KEY}"
        elif isinstance(auth, str):
            h["Authorization"] = f"Bearer {auth}"
        h.update(headers or {})
        req = urllib.request.Request(self.base_url + path, data=body, headers=h, method=method)
        t0 = time.perf_counter()
        try:
            with _OPENER.open(req, timeout=self.timeout) as r:
                status, raw, hdrs = r.status, r.read(MAX_BODY + 1), r.headers
        except urllib.error.HTTPError as e:
            try:
                status, raw, hdrs = e.code, e.read(MAX_BODY + 1), e.headers
            except (http.client.HTTPException, OSError) as inner:
                raise TransportError(f"{method} {path}: {e.code} with an unreadable body ({inner!r})") from None
        except TimeoutError as e:
            raise Timeout(f"{method} {path}: no response within {self.timeout:g}s") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, (TimeoutError, socket.timeout)):
                raise Timeout(f"{method} {path}: no response within {self.timeout:g}s") from None
            raise TransportError(f"{method} {path}: {e.reason}") from None
        except (http.client.HTTPException, ConnectionError, OSError) as e:
            raise TransportError(f"{method} {path}: {type(e).__name__}: {e}") from None
        if len(raw) > MAX_BODY:
            raise TransportError(f"{method} {path}: response body larger than {MAX_BODY // 2**20} MiB")
        declared = hdrs.get("Content-Length")
        if declared and declared.isdigit() and len(raw) < int(declared):  # read(amt) does not raise on a short body
            raise TransportError(f"{method} {path}: connection closed after {len(raw)} of {declared} body bytes")
        ms = (time.perf_counter() - t0) * 1000
        resp = Response(status, {k.lower(): v for k, v in hdrs.items()}, raw, ms)
        if raw:
            resp.data, resp.json_error, resp.nonfinite = parse_json(raw)
        else:
            resp.json_error = "empty body"
        return resp

    def post_json(self, path: str, payload: Any, **kw: Any) -> Response:
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self.request("POST", path, body, **kw)

    def ask(self, questions: dict[str, Any], state: Any = "", *, model: str | None = None, **extra: Any) -> Response:
        payload = {"model": model or self.model, "state": state, "questions": questions, **extra}
        return self.post_json("/v1/systemone", payload)

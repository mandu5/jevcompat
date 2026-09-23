from __future__ import annotations

import pytest

from jevcompat import runner
from jevcompat.mock import MockConfig, Running


def run_against(cfg: MockConfig | None = None, **kw):
    with Running(cfg or MockConfig()) as m:
        return runner.run(m.url, **{"sdk": False, "timeout": 10, **kw})


@pytest.fixture
def status():
    def get(report, req):
        return next(r for r in report.results if r.id == req).status
    return get

import re
from time import perf_counter
from typing import Any

from core.constants import DEFAULT_USER_AGENT, STATUS_ERROR, STATUS_FOUND
from core.interface import create_result
from core.results import ScanResults

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class LinkTrace:
    def __init__(self, target: str, options: Any = None, **_: Any) -> None:
        self.target = str(target).strip()
        self.timeout = float(getattr(options, "timeout", 10) or 10)

    def run(self) -> ScanResults:
        results = ScanResults()
        results.add(self._inspect_link())
        return results

    def _inspect_link(self):
        started = perf_counter()
        try:
            import requests

            with requests.Session() as session:
                session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
                response = session.get(self.target, timeout=self.timeout, allow_redirects=True)

            status = STATUS_ERROR if response.status_code in (401, 403, 429, 503) else STATUS_FOUND
            result = create_result("Link", status, response.url, perf_counter() - started)
            result["status_code"] = response.status_code
            result["redirect_chain"] = [item.url for item in response.history] + [response.url]
            result["headers"] = dict(response.headers)
            result["title"] = self._extract_title(response.text)
            return result
        except Exception as exc:
            result = create_result("Link", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _extract_title(self, html: str) -> str:
        match = TITLE_RE.search(html or "")
        if not match:
            return ""
        return " ".join(match.group(1).split())

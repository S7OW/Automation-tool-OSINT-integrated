from time import perf_counter
from typing import Any, Dict, List

from core.constants import DEFAULT_USER_AGENT, STATUS_ERROR, STATUS_FOUND
from core.interface import create_result
from core.results import ScanResults

TECH_PATTERNS = {
    "WordPress": ("wp-content", "wp-includes", "wordpress"),
    "React": ("reactroot", "__react", "react-dom"),
    "Next.js": ("__next", "_next/static"),
    "jQuery": ("jquery",),
    "Bootstrap": ("bootstrap",),
    "Cloudflare": ("cf-ray", "cloudflare"),
    "Google Analytics": ("google-analytics", "gtag(", "googletagmanager"),
}


class WebTrace:
    def __init__(self, target: str, options: Any = None, **_: Any) -> None:
        self.target = self._normalize_url(target)
        self.timeout = float(getattr(options, "timeout", 10) or 10)

    def run(self) -> ScanResults:
        results = ScanResults()
        results.add(self._detect_technologies())
        return results

    def _detect_technologies(self):
        started = perf_counter()
        try:
            import requests

            with requests.Session() as session:
                session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
                response = session.get(self.target, timeout=self.timeout, allow_redirects=True)

            if response.status_code in (401, 403, 429, 503):
                result = create_result("Web Technologies", STATUS_ERROR, response.url, perf_counter() - started)
                result["status_code"] = response.status_code
                result["headers"] = dict(response.headers)
                result["technologies"] = []
                return result

            headers = {key.lower(): value for key, value in response.headers.items()}
            detected = self._detect_from(headers, response.text)
            result = create_result("Web Technologies", STATUS_FOUND, response.url, perf_counter() - started)
            result["status_code"] = response.status_code
            result["technologies"] = detected
            result["headers"] = dict(response.headers)
            return result
        except Exception as exc:
            result = create_result("Web Technologies", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _detect_from(self, headers: Dict[str, str], html: str) -> List[str]:
        haystack = " ".join(list(headers.keys()) + list(headers.values()) + [html or ""]).lower()
        detected = []

        server = headers.get("server")
        powered_by = headers.get("x-powered-by")
        if server:
            detected.append(f"Server: {server}")
        if powered_by:
            detected.append(f"X-Powered-By: {powered_by}")

        for technology, patterns in TECH_PATTERNS.items():
            if any(pattern.lower() in haystack for pattern in patterns):
                detected.append(technology)

        return sorted(set(detected))

    def _normalize_url(self, target: str) -> str:
        url = str(target).strip()
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url

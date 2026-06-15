import hashlib
import re
from time import perf_counter
from typing import Any, Optional

from core.constants import STATUS_ERROR, STATUS_FOUND, STATUS_NOT_FOUND
from core.interface import create_result
from core.results import ScanResults

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class EmailTrace:
    def __init__(self, target: str, options: Any = None, **_: Any) -> None:
        self.target = str(target).strip()
        self.timeout = float(getattr(options, "timeout", 10) or 10)

    def run(self) -> ScanResults:
        results = ScanResults()
        results.add(self._validate_email())

        domain = self._extract_domain()
        if domain:
            domain_result = self._base_result("Email Domain", STATUS_FOUND, domain)
            domain_result["domain"] = domain
            results.add(domain_result)
            results.add(self._check_gravatar())

        return results

    def _validate_email(self):
        status = STATUS_FOUND if EMAIL_RE.match(self.target) else STATUS_NOT_FOUND
        result = self._base_result("Email Validation", status, self.target)
        result["valid"] = status == STATUS_FOUND
        return result

    def _extract_domain(self) -> Optional[str]:
        if "@" not in self.target or not EMAIL_RE.match(self.target):
            return None
        return self.target.rsplit("@", 1)[1].lower()

    def _check_gravatar(self):
        started = perf_counter()
        email_hash = hashlib.md5(self.target.lower().encode("utf-8")).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"

        try:
            import requests

            with requests.Session() as session:
                response = session.get(url, timeout=self.timeout, allow_redirects=False)
            status = STATUS_FOUND if response.status_code == 200 else STATUS_NOT_FOUND
            if response.status_code not in (200, 404):
                status = STATUS_ERROR
            result = create_result("Gravatar", status, url, perf_counter() - started)
            result["status_code"] = response.status_code
            return result
        except Exception as exc:
            result = create_result("Gravatar", STATUS_ERROR, url, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _base_result(self, platform: str, status: str, url: str):
        result = create_result(platform, status, url, 0.0)
        result["target"] = self.target
        return result

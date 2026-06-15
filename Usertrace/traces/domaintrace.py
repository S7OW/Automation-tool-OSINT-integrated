import socket
from time import perf_counter
from typing import Any, List

from core.constants import STATUS_ERROR, STATUS_FOUND, STATUS_NOT_FOUND
from core.interface import create_result
from core.results import ScanResults


class DomainTrace:
    def __init__(self, target: str, **_: Any) -> None:
        self.target = self._normalize_domain(target)

    def run(self) -> ScanResults:
        results = ScanResults()
        results.add(self._resolve_ips())
        results.add(self._dns_records("MX"))
        results.add(self._dns_records("NS"))
        results.add(self._whois_lookup())
        return results

    def _resolve_ips(self):
        started = perf_counter()
        try:
            addresses = sorted({info[4][0] for info in socket.getaddrinfo(self.target, None)})
            status = STATUS_FOUND if addresses else STATUS_NOT_FOUND
            result = create_result("DNS A", status, self.target, perf_counter() - started)
            result["records"] = addresses
            return result
        except Exception as exc:
            result = create_result("DNS A", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _dns_records(self, record_type: str):
        started = perf_counter()
        try:
            import dns.resolver

            answers = dns.resolver.resolve(self.target, record_type)
            records = [answer.to_text() for answer in answers]
            status = STATUS_FOUND if records else STATUS_NOT_FOUND
            result = create_result(f"DNS {record_type}", status, self.target, perf_counter() - started)
            result["records"] = records
            return result
        except ImportError:
            result = create_result(f"DNS {record_type}", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = "dnspython is not installed"
            return result
        except Exception as exc:
            result = create_result(f"DNS {record_type}", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _whois_lookup(self):
        started = perf_counter()
        try:
            import whois

            data = whois.whois(self.target)
            result = create_result("WHOIS", STATUS_FOUND, self.target, perf_counter() - started)
            result["registrar"] = self._stringify(getattr(data, "registrar", None))
            result["creation_date"] = self._stringify(getattr(data, "creation_date", None))
            result["expiration_date"] = self._stringify(getattr(data, "expiration_date", None))
            result["name_servers"] = self._listify(getattr(data, "name_servers", None))
            return result
        except ImportError:
            result = create_result("WHOIS", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = "python-whois is not installed"
            return result
        except Exception as exc:
            result = create_result("WHOIS", STATUS_ERROR, self.target, perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _normalize_domain(self, target: str) -> str:
        domain = str(target).strip().lower()
        for prefix in ("http://", "https://"):
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        return domain.split("/", 1)[0]

    def _stringify(self, value: Any) -> str:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return "" if value is None else str(value)

    def _listify(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

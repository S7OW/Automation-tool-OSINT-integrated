from threading import Lock
from typing import Any, Dict, Iterable, List, Optional

from core.constants import STATUS_ERROR, VALID_STATUSES


class ScanResults:
    def __init__(self, initial_results: Optional[Iterable[Dict[str, Any]]] = None) -> None:
        self._results: List[Dict[str, Any]] = []
        self._lock = Lock()

        if initial_results:
            self.extend(initial_results)

    def add(self, result: Dict[str, Any]) -> None:
        with self._lock:
            self._results.append(self._normalize(result))

    def extend(self, results: Iterable[Dict[str, Any]]) -> None:
        for result in results:
            self.add(result)

    def clear(self) -> None:
        with self._lock:
            self._results.clear()

    def all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(result) for result in self._results]

    def count(self) -> int:
        with self._lock:
            return len(self._results)

    def to_export(self) -> List[Dict[str, Any]]:
        return self.all()

    def to_ui(self) -> List[Dict[str, Any]]:
        return [
            {
                "platform": result["platform"],
                "status": result["status"],
                "url": result["url"],
                "response_time": result["response_time"],
            }
            for result in self.all()
        ]

    def as_dict(self) -> Dict[str, Any]:
        results = self.all()
        return {
            "count": len(results),
            "results": results,
        }

    def _normalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(result)
        normalized["platform"] = str(normalized.get("platform", "unknown"))

        status = normalized.get("status", STATUS_ERROR)
        normalized["status"] = status if status in VALID_STATUSES else STATUS_ERROR

        normalized["url"] = str(normalized.get("url", ""))

        try:
            normalized["response_time"] = float(normalized.get("response_time", 0.0))
        except (TypeError, ValueError):
            normalized["response_time"] = 0.0

        return normalized

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        return iter(self.all())

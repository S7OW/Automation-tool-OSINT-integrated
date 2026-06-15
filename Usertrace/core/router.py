from importlib import import_module
from typing import Any, Dict, Optional, Type

from core.constants import STATUS_ERROR
from core.interface import create_result
from core.results import ScanResults
from core.scanner import Scanner

TRACE_ROUTES = {
    "username": ("traces.usernametrace", "UsernameTrace"),
    "email": ("traces.emailtrace", "EmailTrace"),
    "domain": ("traces.domaintrace", "DomainTrace"),
    "link": ("traces.linktrace", "LinkTrace"),
    "metadata": ("traces.metadatatrace", "MetadataTrace"),
    "web": ("traces.webtrace", "WebTrace"),
}


class EmptyTrace:
    def __init__(self, target: str, scanner: Optional[Scanner] = None, **context: Any) -> None:
        self.target = target
        self.scanner = scanner or Scanner()
        self.context = context
        self.modules = []

    def run(self) -> ScanResults:
        return self.scanner.scan(self.modules, self.target)


class BrokenTrace(EmptyTrace):
    error = "trace route is unavailable"

    def run(self) -> ScanResults:
        results = ScanResults()
        result = create_result(self.__class__.__name__, STATUS_ERROR, self.target, 0.0)
        result["error"] = self.error
        results.add(result)
        return results


def route_command(command: str, target: str, options: Any = None) -> Dict[str, Any]:
    trace_class = _resolve_trace_class(command)
    scanner = Scanner(max_workers=_thread_count(options))
    trace = _build_trace(trace_class, target, scanner, options)
    raw_results = trace.run()
    results = _coerce_results(raw_results)

    return {
        "command": command,
        "target": target,
        "trace": trace_class.__name__,
        "count": results.count(),
        "results": results.to_export(),
    }


def _thread_count(options: Any) -> int:
    try:
        return max(1, int(getattr(options, "threads", 10) or 10))
    except (TypeError, ValueError):
        return 10


def _resolve_trace_class(command: str) -> Type[Any]:
    route = TRACE_ROUTES.get(command)
    if route is None:
        return EmptyTrace

    module_name, class_name = route

    try:
        module = import_module(module_name)
        trace_class = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        return type(class_name, (BrokenTrace,), {"error": str(exc)})

    return trace_class


def _build_trace(trace_class: Type[Any], target: str, scanner: Scanner, options: Any) -> Any:
    for kwargs in (
        {"target": target, "scanner": scanner, "options": options},
        {"target": target, "scanner": scanner},
        {"target": target},
    ):
        try:
            return trace_class(**kwargs)
        except TypeError:
            continue

    try:
        return trace_class(target, scanner, options)
    except TypeError:
        return trace_class(target)


def _coerce_results(raw_results: Any) -> ScanResults:
    if isinstance(raw_results, ScanResults):
        return raw_results

    results = ScanResults()

    if isinstance(raw_results, list):
        results.extend(raw_results)
    elif isinstance(raw_results, dict) and "results" in raw_results:
        results.extend(raw_results.get("results") or [])
    elif isinstance(raw_results, dict):
        results.add(raw_results)

    return results

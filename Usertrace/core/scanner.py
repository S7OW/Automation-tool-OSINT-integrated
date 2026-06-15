from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, List, Optional

from core.constants import STATUS_ERROR
from core.interface import create_result
from core.results import ScanResults

ModuleFunction = Callable[..., Any]


class Scanner:
    def __init__(self, max_workers: Optional[int] = None) -> None:
        self.max_workers = max_workers

    def scan(
        self,
        modules: Iterable[ModuleFunction],
        target: str,
        results: Optional[ScanResults] = None,
        **context: Any,
    ) -> ScanResults:
        storage = results or ScanResults()
        module_list = list(modules)

        if not module_list:
            return storage

        worker_count = self.max_workers or min(32, len(module_list))

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_map = {
                executor.submit(self._run_module, module, target, context): module
                for module in module_list
            }

            for future in as_completed(future_map):
                storage.add(future.result())

        return storage

    def _run_module(
        self,
        module: ModuleFunction,
        target: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        started = perf_counter()
        platform = getattr(module, "platform", None) or getattr(module, "__name__", "unknown")

        try:
            raw_result = module(target, **context)
            response_time = perf_counter() - started
            return self._normalize_result(raw_result, platform, target, response_time)
        except Exception as exc:
            response_time = perf_counter() - started
            result = create_result(
                platform=str(platform),
                status=STATUS_ERROR,
                url=str(target),
                response_time=response_time,
            )
            result["error"] = str(exc)
            return result

    def _normalize_result(
        self,
        raw_result: Any,
        platform: str,
        target: str,
        response_time: float,
    ) -> Dict[str, Any]:
        if isinstance(raw_result, dict):
            result = dict(raw_result)
            result.setdefault("platform", str(platform))
            result.setdefault("status", STATUS_ERROR)
            result.setdefault("url", str(target))
            result.setdefault("response_time", response_time)
            result["response_time"] = float(result["response_time"])
            return result

        result = create_result(
            platform=str(platform),
            status=STATUS_ERROR,
            url=str(target),
            response_time=response_time,
        )
        if raw_result is not None:
            result["data"] = raw_result
        return result


def run_scan(
    modules: Iterable[ModuleFunction],
    target: str,
    max_workers: Optional[int] = None,
    **context: Any,
) -> ScanResults:
    return Scanner(max_workers=max_workers).scan(modules, target, **context)

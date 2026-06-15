from typing import Any

from core.scanner import Scanner
from core.results import ScanResults
from modules.registry import get_modules


class UsernameTrace:
    def __init__(self, target: str, scanner: Scanner = None, options: Any = None, **_: Any) -> None:
        self.target = str(target).strip()
        self.options = options
        self.scanner = scanner or Scanner(max_workers=self._threads())
        self.modules = get_modules("username")

    def run(self) -> ScanResults:
        return self.scanner.scan(
            self.modules,
            self.target,
            timeout=self._timeout(),
        )

    def _threads(self) -> int:
        return int(getattr(self.options, "threads", 10) or 10)

    def _timeout(self) -> float:
        return float(getattr(self.options, "timeout", 10) or 10)

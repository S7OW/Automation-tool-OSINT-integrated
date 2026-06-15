import csv
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.constants import EXPORT_DIR
from core.results import ScanResults


class Exporter:
    def __init__(self, export_dir: Path = EXPORT_DIR) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, results: Any, filename: Optional[str] = None) -> Path:
        path = self._build_path(filename, "json")
        payload = self._coerce_results(results)

        with path.open("w", encoding="utf-8") as export_file:
            json.dump(payload, export_file, indent=2, ensure_ascii=False)

        return path

    def export_csv(self, results: Any, filename: Optional[str] = None) -> Path:
        path = self._build_path(filename, "csv")
        rows = self._coerce_results(results)
        fieldnames = self._fieldnames(rows)

        with path.open("w", encoding="utf-8", newline="") as export_file:
            writer = csv.DictWriter(export_file, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        return path

    def export_txt(self, results: Any, filename: Optional[str] = None) -> Path:
        path = self._build_path(filename, "txt")
        rows = self._coerce_results(results)

        with path.open("w", encoding="utf-8") as export_file:
            if not rows:
                export_file.write("No results found.\n")
                return path

            for index, row in enumerate(rows, start=1):
                export_file.write(f"Result #{index}\n")
                for key in self._fieldnames(rows):
                    export_file.write(f"{key}: {row.get(key, '')}\n")
                export_file.write("\n")

        return path

    def export(self, results: Any, export_format: str, filename: Optional[str] = None) -> Path:
        normalized_format = export_format.lower().strip()

        if normalized_format == "json":
            return self.export_json(results, filename)
        if normalized_format == "csv":
            return self.export_csv(results, filename)
        if normalized_format == "txt":
            return self.export_txt(results, filename)

        raise ValueError(f"Unsupported export format: {export_format}")

    def _build_path(self, filename: Optional[str], extension: str) -> Path:
        if filename:
            stem = Path(filename).stem
        else:
            stem = f"usertrace_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        safe_stem = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in stem)
        return self.export_dir / f"{safe_stem}.{extension}"

    def _coerce_results(self, results: Any) -> List[Dict[str, Any]]:
        if isinstance(results, ScanResults):
            return results.to_export()

        if isinstance(results, dict):
            if isinstance(results.get("results"), list):
                return [dict(row) for row in results["results"] if isinstance(row, dict)]
            return [dict(results)]

        if isinstance(results, Iterable) and not isinstance(results, (str, bytes)):
            return [dict(row) for row in results if isinstance(row, dict)]

        return []

    def _fieldnames(self, rows: List[Dict[str, Any]]) -> List[str]:
        preferred = ["platform", "status", "url", "response_time", "timestamp"]
        discovered = []

        for row in rows:
            for key in row:
                if key not in preferred and key not in discovered:
                    discovered.append(key)

        return preferred + discovered


def export_json(results: Any, filename: Optional[str] = None) -> Path:
    return Exporter().export_json(results, filename)


def export_csv(results: Any, filename: Optional[str] = None) -> Path:
    return Exporter().export_csv(results, filename)


def export_txt(results: Any, filename: Optional[str] = None) -> Path:
    return Exporter().export_txt(results, filename)


def export_results(results: Any, export_format: str, filename: Optional[str] = None) -> Path:
    return Exporter().export(results, export_format, filename)

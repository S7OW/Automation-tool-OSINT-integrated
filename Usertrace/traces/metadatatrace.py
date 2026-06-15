import json
import zipfile
from pathlib import Path
from time import perf_counter
from typing import Any, Dict
from xml.etree import ElementTree

from core.constants import STATUS_ERROR, STATUS_FOUND, STATUS_NOT_FOUND
from core.interface import create_result
from core.results import ScanResults


class MetadataTrace:
    def __init__(self, target: str, **_: Any) -> None:
        self.target = Path(str(target).strip())

    def run(self) -> ScanResults:
        results = ScanResults()
        results.add(self._extract_metadata())
        return results

    def _extract_metadata(self):
        started = perf_counter()
        try:
            if not self.target.exists() or not self.target.is_file():
                result = create_result("Metadata", STATUS_NOT_FOUND, str(self.target), perf_counter() - started)
                result["error"] = "file not found"
                return result

            suffix = self.target.suffix.lower()
            if suffix in (".jpg", ".jpeg", ".png"):
                metadata = self._image_metadata()
            elif suffix == ".pdf":
                metadata = self._pdf_metadata()
            elif suffix == ".docx":
                metadata = self._docx_metadata()
            else:
                metadata = {"error": f"unsupported file type: {suffix}"}

            status = STATUS_FOUND if metadata and "error" not in metadata else STATUS_ERROR
            result = create_result("Metadata", status, str(self.target), perf_counter() - started)
            result["metadata"] = metadata
            return result
        except Exception as exc:
            result = create_result("Metadata", STATUS_ERROR, str(self.target), perf_counter() - started)
            result["error"] = str(exc)
            return result

    def _image_metadata(self) -> Dict[str, Any]:
        try:
            from PIL import Image
        except ImportError:
            return self._exifread_metadata()

        metadata: Dict[str, Any] = {}
        with Image.open(self.target) as image:
            metadata["format"] = image.format
            metadata["size"] = list(image.size)
            metadata["mode"] = image.mode
            metadata["info"] = self._safe_values(dict(image.info))

            exif = image.getexif()
            if exif:
                metadata["exif"] = {str(key): str(value) for key, value in exif.items()}

        return metadata

    def _exifread_metadata(self) -> Dict[str, Any]:
        try:
            import exifread
        except ImportError:
            return {"error": "Pillow or exifread is required for image metadata"}

        with self.target.open("rb") as image_file:
            tags = exifread.process_file(image_file, details=False)
        return {"exif": {str(key): str(value) for key, value in tags.items()}}

    def _pdf_metadata(self) -> Dict[str, Any]:
        data = self.target.read_bytes()[:1024 * 1024]
        metadata: Dict[str, Any] = {}
        for key in (b"Title", b"Author", b"Subject", b"Creator", b"Producer", b"CreationDate", b"ModDate"):
            marker = b"/" + key + b"("
            start = data.find(marker)
            if start == -1:
                continue
            start += len(marker)
            end = data.find(b")", start)
            if end != -1:
                metadata[key.decode("ascii")] = data[start:end].decode("latin-1", errors="replace")
        return metadata

    def _docx_metadata(self) -> Dict[str, Any]:
        with zipfile.ZipFile(self.target) as archive:
            if "docProps/core.xml" not in archive.namelist():
                return {}
            xml_data = archive.read("docProps/core.xml")

        root = ElementTree.fromstring(xml_data)
        metadata = {}
        for element in root.iter():
            if element.text and element.tag:
                key = element.tag.rsplit("}", 1)[-1]
                metadata[key] = element.text
        return metadata

    def _safe_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        safe = {}
        for key, value in values.items():
            try:
                json.dumps(value)
                safe[key] = value
            except TypeError:
                safe[key] = str(value)
        return safe

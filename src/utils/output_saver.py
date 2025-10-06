"""Utility helpers for persisting command results to disk."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from src.utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_OUTPUT_FORMATS = {"txt", "md", "csv", "json"}


def _ensure_directory(path: Path) -> None:
    if path.parent.exists():
        return
    logger.debug("Creating parent directory for %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)


def _normalise_csv_rows(data: object) -> tuple[List[str], List[List[str]]]:
    """Return CSV headers and rows derived from arbitrary data."""

    if isinstance(data, list):
        if not data:
            return [], []
        if isinstance(data[0], dict):
            headers = sorted({key for row in data for key in row.keys()})
            rows: List[List[str]] = [
                [str(row.get(header, "")) for header in headers]
                for row in data
            ]
            return headers, rows
        return ["value"], [[str(item)] for item in data]

    if isinstance(data, dict):
        headers = ["key", "value"]
        rows = [[str(key), str(value)] for key, value in data.items()]
        return headers, rows

    return ["value"], [[str(data)]]


def save_results(data: object, output_path: str, output_format: str | None = None) -> Path:
    """Persist ``data`` to ``output_path`` in the requested format."""

    path = Path(output_path)
    fmt = (output_format or path.suffix.lstrip(".")).lower()
    if fmt not in SUPPORTED_OUTPUT_FORMATS:
        raise ValueError(
            f"Unsupported output format '{fmt}'. Supported formats: {sorted(SUPPORTED_OUTPUT_FORMATS)}"
        )

    if not path.suffix:
        path = path.with_suffix(f".{fmt}")

    _ensure_directory(path)

    if fmt in {"txt", "md"}:
        text = data if isinstance(data, str) else json.dumps(data, indent=2, ensure_ascii=False)
        path.write_text(str(text), encoding="utf-8")
    elif fmt == "json":
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
    else:  # fmt == "csv"
        headers, rows = _normalise_csv_rows(data)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            if headers:
                writer.writerow(headers)
            writer.writerows(rows)

    logger.info("Saved results to %s", path)
    return path

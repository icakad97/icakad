"""Utility helpers shared across icakad modules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional


def ensure_parent(path: Path) -> None:
    """Create parent directories for *path* if they do not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(data: Any, destination: str | Path) -> Path:
    """Serialize *data* to JSON and write it to *destination*."""
    target = Path(destination).expanduser().resolve()
    ensure_parent(target)
    with target.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return target


def write_text(text: str, destination: str | Path) -> Path:
    """Write plain text content to *destination*."""
    target = Path(destination).expanduser().resolve()
    ensure_parent(target)
    with target.open("w", encoding="utf-8") as fh:
        fh.write(text)
    return target


def read_text_file(path: str | Path) -> str:
    """Read UTF-8 content from *path*."""
    target = Path(path).expanduser().resolve()
    with target.open("r", encoding="utf-8") as fh:
        return fh.read()


def resolve_text_input(
    *,
    text: Optional[str] = None,
    text_file: Optional[str | Path] = None,
    allow_empty: bool = False,
) -> str:
    """Return text from either an inline value or a file path."""
    if text is not None:
        candidate = text.strip("\n")
    elif text_file is not None:
        candidate = read_text_file(text_file)
    else:
        raise ValueError("Provide text=... or text_file=... to supply content.")

    if not candidate and not allow_empty:
        raise ValueError("The supplied text is empty.")
    return candidate


def print_json(data: Any) -> None:
    """Pretty-print a JSON-compatible structure."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def comma_separated(values: Iterable[str]) -> str:
    """Join a series of strings into a comma-separated sentence."""
    return ", ".join(str(v) for v in values)

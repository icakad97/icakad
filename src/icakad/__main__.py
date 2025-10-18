"""Entry point for ``python -m icakad``."""

from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from typing import Optional

from .cli import main as cli_main

DOCS_URL = "https://linkove.icu/docs/icakad/"


def _find_local_docs() -> Optional[Path]:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "docs" / "index.html"
        if candidate.exists():
            return candidate
    return None


def run() -> int:
    if len(sys.argv) == 1:
        docs_path = _find_local_docs()
        if docs_path:
            print("Open the local documentation:", docs_path)
            try:  # pragma: no cover - optional UX improvement
                webbrowser.open(docs_path.as_uri())
            except Exception:
                pass
        else:
            print("Documentation: ", DOCS_URL)
        print("Use 'python -m icakad --help' for command examples.")
        return 0

    return cli_main(sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())

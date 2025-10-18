"""Configuration helpers for icakad clients."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_SHORTURL_BASE = "https://linkove.icu"
DEFAULT_PASTE_BASE = "https://linkove.icu"

DEFAULT_CONFIG_LOCATIONS = (
    Path.home() / ".config" / "icakad" / "config.json",
    Path.cwd() / "icakad.config.json",
)


@dataclass(frozen=True)
class Settings:
    """Simple container describing API configuration."""

    shorturl_base: str = DEFAULT_SHORTURL_BASE
    paste_base: str = DEFAULT_PASTE_BASE
    token: Optional[str] = None

    def with_overrides(self, **overrides: Any) -> "Settings":
        """Return a copy with any non-None overrides applied."""
        current: Dict[str, Any] = {
            "shorturl_base": self.shorturl_base,
            "paste_base": self.paste_base,
            "token": self.token,
        }
        for key, value in overrides.items():
            if value is not None and key in current:
                current[key] = value
        return Settings(**current)


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_settings(
    config_path: Optional[str | Path] = None,
    *,
    token: Optional[str] = None,
    shorturl_base: Optional[str] = None,
    paste_base: Optional[str] = None,
) -> Settings:
    """Load settings from config files, environment variables, and overrides."""
    settings = Settings()

    # Config file from explicit path or environment hint.
    candidate_paths = []
    if config_path:
        candidate_paths.append(Path(config_path).expanduser())
    env_path = os.environ.get("ICAKAD_CONFIG")
    if env_path:
        candidate_paths.append(Path(env_path).expanduser())
    candidate_paths.extend(DEFAULT_CONFIG_LOCATIONS)

    for path in candidate_paths:
        if path.exists() and path.is_file():
            try:
                payload = _load_json(path)
            except (OSError, ValueError) as exc:
                raise ValueError(f"Unable to read configuration from {path}: {exc}") from exc
            mapped: Dict[str, Any] = {}
            for key in ("shorturl_base", "paste_base", "token"):
                if key in payload:
                    mapped[key] = payload[key]
            settings = settings.with_overrides(**mapped)
            break

    # Environment overrides
    env_overrides = {
        "shorturl_base": os.environ.get("ICAKAD_SHORTURL_BASE"),
        "paste_base": os.environ.get("ICAKAD_PASTE_BASE"),
        "token": os.environ.get("ICAKAD_TOKEN"),
    }
    settings = settings.with_overrides(**env_overrides)

    # Direct call overrides win last.
    settings = settings.with_overrides(
        shorturl_base=shorturl_base,
        paste_base=paste_base,
        token=token,
    )

    return settings

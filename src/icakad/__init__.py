"""Интегриран CLI и API инструментар за екосистемата на icakad."""

from __future__ import annotations

import os
from typing import Any, Dict, Mapping, Optional

from .api import (
    APIError,
    PasteClient,
    ShortURLClient,
    normalise_shorturl_listing,
)

__all__ = [
    "__version__",
    "APIError",
    "ShortURLClient",
    "PasteClient",
    "get_shorturl_client",
    "get_paste_client",
    "add_link",
    "edit_link",
    "delete_link",
    "list_links",
]

__version__ = "0.2.0"

_ENV_TOKEN = "ICAKAD_TOKEN"
_ENV_SHORTURL_BASE = "ICAKAD_SHORTURL_BASE"
_ENV_PASTE_BASE = "ICAKAD_PASTE_BASE"
_DEFAULT_SHORTURL_BASE = "https://linkove.icu/api"
_DEFAULT_PASTE_BASE = "https://paste.icakad.com/api"


def _resolve_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Връща стойност от средата, като уважава празни низове."""

    value = os.getenv(name, default)
    return value if value else default


def get_shorturl_client(
    *,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> ShortURLClient:
    """Създава нов клиент за услугата за кратки линкове."""

    resolved_base = base_url or _resolve_env(_ENV_SHORTURL_BASE, _DEFAULT_SHORTURL_BASE)
    resolved_token = token or _resolve_env(_ENV_TOKEN)
    return ShortURLClient(base_url=resolved_base, token=resolved_token, debug=debug)


def get_paste_client(
    *,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> PasteClient:
    """Създава нов клиент за paste услугата."""

    resolved_base = base_url or _resolve_env(_ENV_PASTE_BASE, _DEFAULT_PASTE_BASE)
    resolved_token = token or _resolve_env(_ENV_TOKEN)
    return PasteClient(base_url=resolved_base, token=resolved_token, debug=debug)


# --- Функции за бърз достъп ---

def _ensure_client(provided: Optional[Any], factory) -> Any:
    if provided is not None:
        return provided
    return factory()


def add_link(
    slug: str,
    url: str,
    *,
    client: Optional[ShortURLClient] = None,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> Mapping[str, Any]:
    """Създава или подменя slug с подадения URL."""

    short_client = _ensure_client(
        client,
        lambda: get_shorturl_client(base_url=base_url, token=token, debug=debug),
    )
    return short_client.create(slug=slug, url=url)


def edit_link(
    slug: str,
    new_url: str,
    *,
    client: Optional[ShortURLClient] = None,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> Mapping[str, Any]:
    """Актуализира вече съществуващ slug."""

    short_client = _ensure_client(
        client,
        lambda: get_shorturl_client(base_url=base_url, token=token, debug=debug),
    )
    return short_client.update(slug=slug, url=new_url)


def delete_link(
    slug: str,
    *,
    client: Optional[ShortURLClient] = None,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> Mapping[str, Any]:
    """Изтрива slug от услугата."""

    short_client = _ensure_client(
        client,
        lambda: get_shorturl_client(base_url=base_url, token=token, debug=debug),
    )
    return short_client.delete(slug=slug)


def list_links(
    *,
    client: Optional[ShortURLClient] = None,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, str]:
    """Връща нормализиран речник от slug към URL."""

    short_client = _ensure_client(
        client,
        lambda: get_shorturl_client(base_url=base_url, token=token, debug=debug),
    )
    raw = short_client.list()
    return normalise_shorturl_listing(raw)

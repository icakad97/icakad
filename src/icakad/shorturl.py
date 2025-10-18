"""Съвместим слой за работа с услугата за кратки линкове."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .api import ShortURLClient, normalise_shorturl_listing
from . import get_shorturl_client

__all__ = [
    "ShortURLClient",
    "add_link",
    "edit_link",
    "delete_link",
    "list_links",
]


def _client(client: Optional[ShortURLClient]) -> ShortURLClient:
    return client if client is not None else get_shorturl_client()


def add_link(slug: str, url: str, *, client: Optional[ShortURLClient] = None) -> Mapping[str, Any]:
    """Създава или подменя slug."""

    return _client(client).create(slug=slug, url=url)


def edit_link(slug: str, new_url: str, *, client: Optional[ShortURLClient] = None) -> Mapping[str, Any]:
    """Актуализира slug."""

    return _client(client).update(slug=slug, url=new_url)


def delete_link(slug: str, *, client: Optional[ShortURLClient] = None) -> Mapping[str, Any]:
    """Изтрива slug."""

    return _client(client).delete(slug=slug)


def list_links(*, client: Optional[ShortURLClient] = None) -> Dict[str, str]:
    """Връща всички slug-ове като речник."""

    payload = _client(client).list()
    return normalise_shorturl_listing(payload)

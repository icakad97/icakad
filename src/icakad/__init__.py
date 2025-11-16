"""Публичен интерфейс за инструментите на пакета icakad."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .ai import AI
from .common import print_json, resolve_text_input, write_json, write_text
from .config import Settings, load_settings
from .paste import PasteClient
from .shorturl import ShortURLClient

__all__ = [
    "AI",
    "Settings",
    "load_settings",
    "add_short_link",
    "list_short_links",
    "update_short_link",
    "delete_short_link",
    "list_pastes",
    "create_paste",
    "fetch_paste",
    "print_json",
]

__version__ = "0.1.4"


# ----------------------------------------------------------------- factories
def _client_from_settings(
    *,
    settings: Optional[Settings] = None,
    token: Optional[str] = None,
    shorturl_base: Optional[str] = None,
    timeout: Optional[int] = None,
) -> ShortURLClient:
    cfg = settings or load_settings(token=token, shorturl_base=shorturl_base)
    resolved_timeout = ShortURLClient.timeout if timeout is None else timeout
    return ShortURLClient(
        base_url=cfg.shorturl_base,
        token=cfg.token,
        timeout=resolved_timeout,
    )


def _paste_client_from_settings(
    *,
    settings: Optional[Settings] = None,
    paste_base: Optional[str] = None,
    token: Optional[str] = None,
    timeout: Optional[int] = None,
) -> PasteClient:
    cfg = settings or load_settings(paste_base=paste_base, token=token)
    resolved_timeout = PasteClient.timeout if timeout is None else timeout
    return PasteClient(
        base_url=cfg.paste_base,
        token=cfg.token,
        timeout=resolved_timeout,
    )


# -------------------------------------------------------------- short links
def add_short_link(
    slug: str,
    url: str,
    *,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    **overrides: Any,
) -> Dict[str, Any]:
    client = _client_from_settings(settings=settings, **overrides)
    result = client.add_link(slug, url)
    if save_to:
        write_json(result, save_to)
    return result


def list_short_links(
    *,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    print_output: bool = True,
    **overrides: Any,
) -> Dict[str, str]:
    client = _client_from_settings(settings=settings, **overrides)
    links = client.list_links()
    if save_to:
        write_json(links, save_to)
    if print_output:
        print_json(links)
    return links


def update_short_link(
    slug: str,
    url: str,
    *,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    **overrides: Any,
) -> Dict[str, Any]:
    client = _client_from_settings(settings=settings, **overrides)
    result = client.edit_link(slug, url)
    if save_to:
        write_json(result, save_to)
    return result


def delete_short_link(
    slug: str,
    *,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    **overrides: Any,
) -> Dict[str, Any]:
    client = _client_from_settings(settings=settings, **overrides)
    result = client.delete_link(slug)
    if save_to:
        write_json(result, save_to)
    return result


# ------------------------------------------------------------------- pastes
def create_paste(
    *,
    text: Optional[str] = None,
    text_file: Optional[Union[str, Path]] = None,
    paste_id: Optional[str] = None,
    ttl: Optional[int] = None,
    as_plaintext: bool = False,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    **overrides: Any,
) -> Dict[str, Any]:
    client = _paste_client_from_settings(settings=settings, **overrides)
    body = resolve_text_input(text=text, text_file=text_file)
    result = client.create_paste(
        body,
        paste_id=paste_id,
        ttl=ttl,
        as_plaintext=as_plaintext,
    )
    if save_to:
        write_json(result, save_to)
    return result


def list_pastes(
    *,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    print_output: bool = True,
    **overrides: Any,
) -> Dict[str, Any]:
    client = _paste_client_from_settings(settings=settings, **overrides)
    result = client.list_pastes()
    if save_to:
        write_json(result, save_to)
    if print_output:
        print_json(result)
    return result


def fetch_paste(
    paste_id: str,
    *,
    raw: bool = False,
    save_to: Optional[Union[str, Path]] = None,
    settings: Optional[Settings] = None,
    **overrides: Any,
) -> Any:
    client = _paste_client_from_settings(settings=settings, **overrides)
    result = client.fetch_paste(paste_id, raw=raw)
    if save_to:
        if raw:
            write_text(result, save_to)
        else:
            write_json(result, save_to)
    return result

"""Public interface for the icakad short URL toolkit."""

from __future__ import annotations

from .shorturl import add_link, edit_link, delete_link, list_links

__all__ = [
    "TOKEN"='icakadTOKEN',
    "add_link",
    "edit_link",
    "delete_link",
    "list_links",
]

__version__ = "0.1.1"

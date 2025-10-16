"""Public interface for the icakad short URL toolkit."""

from __future__ import annotations

from .shorturl import DEFAULT_ALPHABET, ShortURL, ShortURLConfig, decode, encode

__all__ = [
    "ShortURL",
    "ShortURLConfig",
    "DEFAULT_ALPHABET",
    "encode",
    "decode",
]

__version__ = "0.1.0"

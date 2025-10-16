"""Utilities for base-n style short URL tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

DEFAULT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass(frozen=True)
class ShortURLConfig:
    """Configuration for ``ShortURL`` codecs."""

    alphabet: str = DEFAULT_ALPHABET
    min_length: int = 1

    def __post_init__(self) -> None:
        if not self.alphabet:
            raise ValueError("alphabet must contain at least one character")
        if len(set(self.alphabet)) != len(self.alphabet):
            raise ValueError("alphabet characters must be unique")
        if self.min_length < 1:
            raise ValueError("min_length must be >= 1")


class ShortURL:
    """Encode and decode integers into short, URL-friendly tokens."""

    def __init__(self, config: Optional[ShortURLConfig] = None) -> None:
        self.config = config or ShortURLConfig()
        self._base = len(self.config.alphabet)
        self._index: Dict[str, int] = {
            char: position for position, char in enumerate(self.config.alphabet)
        }

    def encode(self, number: int) -> str:
        """Convert a non-negative integer into a short token."""
        if number < 0:
            raise ValueError("number must be non-negative")

        if number == 0:
            token = self.config.alphabet[0]
        else:
            digits = []
            value = number
            while value:
                value, remainder = divmod(value, self._base)
                digits.append(self.config.alphabet[remainder])
            digits.reverse()
            token = "".join(digits)

        if len(token) < self.config.min_length:
            padding = self.config.alphabet[0] * (self.config.min_length - len(token))
            token = f"{padding}{token}"

        return token

    def decode(self, token: str) -> int:
        """Convert a short token back into the original integer."""
        if not token:
            raise ValueError("token must not be empty")

        value = 0
        for char in token:
            try:
                value = value * self._base + self._index[char]
            except KeyError as exc:
                raise ValueError(f"token contains invalid character: {char!r}") from exc

        return value


_DEFAULT_CODEC = ShortURL()


def encode(number: int, *, config: Optional[ShortURLConfig] = None) -> str:
    """Encode ``number`` using the default or a custom configuration."""
    codec = _DEFAULT_CODEC if config is None else ShortURL(config)
    return codec.encode(number)


def decode(token: str, *, config: Optional[ShortURLConfig] = None) -> int:
    """Decode ``token`` using the default or a custom configuration."""
    codec = _DEFAULT_CODEC if config is None else ShortURL(config)
    return codec.decode(token)


__all__ = [
    "ShortURL",
    "ShortURLConfig",
    "DEFAULT_ALPHABET",
    "encode",
    "decode",
]

"""Съвместимост със старото име `shortlink`.

Този модул е оставен за потребители на по-стария API. Той просто
препраща всички публични символи към :mod:`icakad.shorturl` и вдига
``DeprecationWarning`` при импорт.
"""

from __future__ import annotations

import warnings

from . import shorturl as _shorturl

globals().update(
    {
        name: getattr(_shorturl, name)
        for name in dir(_shorturl)
        if not name.startswith("_")
    }
)

warnings.warn(
    "`icakad.shortlink` е отложено в полза на `icakad.shorturl`. "
    "Моля, обновете импортите си.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [name for name in dir(_shorturl) if not name.startswith("_")]

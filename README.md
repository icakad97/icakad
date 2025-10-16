# icakad

Lightweight utilities for encoding integers into short, URL-friendly tokens.

## Installation

```bash
pip install icakad
```

## Quickstart

```python
from icakad import ShortURL, encode, decode, ShortURLConfig

token = encode(12345)
assert decode(token) == 12345

custom = ShortURL(ShortURLConfig(alphabet="abcd", min_length=6))
assert custom.encode(5) == "aaaabd"
```

## Features

- Zero-dependency implementation with a configurable alphabet
- Encode and decode helpers plus a reusable `ShortURL` codec
- Optional minimum length padding for consistent token sizes

## Development

To build the package locally:

```bash
python -m build
```

Run tests (if you add them) with:

```bash
python -m pytest
```

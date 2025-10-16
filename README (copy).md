# icakad.shorturl — Cloudflare KV Link Shortener (Client)

Tiny Python helper around your Cloudflare Worker API for creating, editing, listing, and deleting short links.

> Works on Python 3 and Pythonista 3 (no external deps besides `requests`).

## Install

```bash
pip install icakad
```

Pythonista already ships `requests`. On desktop, if needed:

```bash
pip install requests
```

## Configure

`shorturl.py` talks to your Worker:

- Base URL (without trailing `/`): `BASE`
- Bearer token header: `HEADERS = {"Authorization": "Bearer <TOKEN>", "Content-Type": "application/json"}`

Set them right after import (override defaults if needed):

```python
from icakad import shorturl as su

su.BASE = "https://lnk.icaka.eu"            # or https://linkove.icu
su.HEADERS = {
    "Authorization": "Bearer icakadTOKEN",
    "Content-Type": "application/json",
}
```

## Endpoints (as used by this client)

- `GET    /api`             → list all links
- `POST   /api`             → add a link (`{"slug": "...", "url": "..."}`)
- `POST   /api/<slug>`      → edit existing slug with a new URL
- `DELETE /api/<slug>`      → delete a slug

Your Worker should return either a list of items or `{"items":[...]}` where each item contains `slug|key|id|name` and `url|value`. The client normalizes both formats.

## Usage

```python
from icakad import shorturl as su

# configure (override defaults)
su.BASE = "https://lnk.icaka.eu"
su.HEADERS = {"Authorization": "Bearer icakadTOKEN", "Content-Type": "application/json"}

# 1) Add
res = su.add_link("avanti", "https://avanti-bg.com/")
print(res)  # JSON from the Worker

# 2) Edit (overwrites URL for the slug)
res = su.edit_link("avanti", "https://avanti-bg.com/promo")
print(res)

# 3) List
links = su.list_links()  # returns dict: {slug: url, ...}
for slug, url in links.items():
    print(slug, "→", url)

# 4) Delete
res = su.delete_link("avanti")
print(res)
```

### Pythonista 3 tip

Make a home‑screen shortcut that runs a script importing `icakad.shorturl` and calling the functions above. For share‑sheet flows, normalize input and call `su.add_link()` with a random slug when none is supplied.

## cURL (for quick testing)

```bash
# List
curl -s -H "Authorization: Bearer icakadTOKEN" https://lnk.icaka.eu/api

# Add
curl -s -X POST https://lnk.icaka.eu/api   -H "Authorization: Bearer icakadTOKEN" -H "Content-Type: application/json"   -d '{"slug":"test","url":"https://example.com"}'

# Edit
curl -s -X POST https://lnk.icaka.eu/api/test   -H "Authorization: Bearer icakadTOKEN" -H "Content-Type: application/json"   -d '{"slug":"test","url":"https://example.com/edited"}'

# Delete
curl -s -X DELETE -H "Authorization: Bearer icakadTOKEN" https://lnk.icaka.eu/api/test
```

## Return shapes

- **Add/Edit/Delete**: pass through Worker JSON (status, echo, etc.).
- **List**: returns `dict[str, str]` of `{slug: url}` after normalizing any of:
  - `[{ "key"|"slug"|"id"|"name": "...", "url"|"value": "..." }, ...]`
  - `{ "items": [ ... ] }`

## Notes

- The edit operation uses `POST /api/<slug>` by design (simple overwrite).
- Set `shorturl.DEBUG = True` to print HTTP status & payloads.
- If you change your Worker shape, adjust `list_links()` normalization accordingly.

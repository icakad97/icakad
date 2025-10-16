# icakad

Lightweight Python client for managing short links hosted on the [linkove.icu](https://linkove.icu) worker.  
The package exports a small set of helpers that wrap the service API so automations and scripts can add, edit, delete, or list slugs without hand-crafting HTTP requests.

## Highlights

- Minimal footprint: only depends on `requests`
- Module-level configuration for base URL, bearer token, and debug logging
- Uniform response handling that normalises the `list` endpoint payload

## Installation

```bash
pip install icakad
```

Install `requests` separately if it is not already available in your environment.

## Quick Start

```python
from icakad import add_link, edit_link, delete_link, list_links
from icakad import shorturl

# Configure credentials and optional debugging up front
shorturl.HEADERS["Authorization"] = "Bearer <your-token>"
shorturl.DEBUG = False

# Create or overwrite a slug
add_link(slug="docs", url="https://example.com/docs")

# Update an existing slug
edit_link(slug="docs", new_url="https://example.com/documentation")

# Fetch the full catalogue
links = list_links()
print(links.get("docs"))

# Remove a slug
delete_link(slug="docs")
```

Each helper returns the JSON body produced by the worker. Inspect it for status codes, error messages, or additional metadata.

## API Reference

All helpers live in `icakad.shorturl` and are re-exported at the package root for convenience.

| Function | Description |
| --- | --- |
| `add_link(slug: str, url: str) -> dict` | Create or overwrite a slug with the target URL. |
| `edit_link(slug: str, new_url: str) -> dict` | Update an existing slug. Backed by `POST /api/<slug>`. |
| `delete_link(slug: str) -> dict` | Delete the slug via `DELETE /api/<slug>`. |
| `list_links() -> dict[str, str]` | Retrieve all slugs. Normalises both list-style and `{"items": [...]}` payloads. |

## Configuration

Tweak behaviour by adjusting attributes on `icakad.shorturl`:

- `BASE`: API root (default `https://linkove.icu`). Point this elsewhere for staging or local testing.
- `HEADERS`: Dictionary of headers supplied with every request. Set the bearer token here.
- `DEBUG`: When `True`, prints HTTP status codes and JSON responses to stdout.

Feel free to override the module-level `requests` usage with your own session or retry logic by wrapping these helpers.

## Error Handling Tips

- Wrap calls in `try/except requests.RequestException` for transport-level issues.
- Validate mandatory keys in the returned JSON before relying on them.
- Enable `DEBUG` when tuning your worker or troubleshooting authentication.

## Development

Clone the repository and install it in editable mode:

```bash
pip install -e .
```

Build packages:

```bash
python -m build
```

Run any tests or scripts you add:

```bash
python -m pytest
```

Contributions that improve ergonomics (e.g., async helpers, richer error handling) are welcome.

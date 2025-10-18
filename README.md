# icakad

Powerful-yet-lightweight toolkit and CLI for working with the icakad services. The
package ships batteries included: a reusable HTTP client layer, helpers dedicated
for the short URL worker, a minimal paste-bin client, and a production-ready
command line interface that ties everything together.

## Installation

```bash
pip install icakad
```

The package depends on [`requests`](https://docs.python-requests.org/) which will
be pulled automatically when installing from PyPI.

## Configuration

Authentication relies on bearer tokens. The CLI and the Python helpers both read
configuration from environment variables which keeps secrets outside of scripts:

| Variable | Description | Default |
| --- | --- | --- |
| `ICAKAD_TOKEN` | Token shared by all services. | _unset_ |
| `ICAKAD_SHORTURL_BASE` | Base URL for the short link API. | `https://linkove.icu/api` |
| `ICAKAD_PASTE_BASE` | Base URL for the paste API. | `https://paste.icakad.com/api` |

You can override the defaults on a per-call basis by passing the `token` or
`base_url` parameters when constructing the dedicated clients.

## Command Line Usage

The package installs the `icakad` executable. Run `icakad --help` to explore all
commands. Highlights:

```bash
# Create or replace a short link
icakad shorturl add docs https://example.com/docs

# Update an existing slug
icakad shorturl edit docs https://example.com/documentation

# Print every slug in a compact table or as JSON
icakad shorturl list
icakad shorturl list --json

# Create a paste (reads from stdin when the content argument is omitted or set to '-')
printf 'hello world' | icakad paste create - --title demo

# Fetch or delete an existing paste
icakad paste show abc123
icakad paste delete abc123
```

Use `--token`, `--shorturl-base`, and `--paste-base` to override the defaults
without touching environment variables. The `--debug` flag prints the HTTP
status code for every request, which is handy when troubleshooting.

## Python API

The high-level helpers mirror the legacy interface but are now powered by the
new client layer:

```python
from icakad import add_link, edit_link, delete_link, list_links

add_link("docs", "https://example.com/docs")
edit_link("docs", "https://example.com/documentation")
all_links = list_links()
print(all_links["docs"])
delete_link("docs")
```

For advanced scenarios instantiate the clients directly:

```python
from icakad import get_shorturl_client, get_paste_client

short_client = get_shorturl_client(token="...custom...")
short_client.create(slug="demo", url="https://example.com")

paste_client = get_paste_client()
created = paste_client.create(content="Hello from icakad")
print(created)
```

The clients raise `icakad.APIError` with the HTTP status code and decoded JSON
payload whenever a request fails.

## Development

```bash
# Install locally
pip install -e .

# Run a quick syntax check
python -m compileall src

# Build the wheel and sdist artefacts
python -m build
```

Contributions are welcome! Feel free to open pull requests with new commands or
integrations with other icakad services.

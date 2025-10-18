# Repository Guidelines

## Project Structure & Module Organization
- Source lives in `src/icakad`; expose public helpers through `__init__.py` and keep shared utilities under `icakad/common`.
- `shorturl.py` and `paste.py` wrap the Cloudflare workers; `cli.py` powers `python -m icakad`; `config.py` resolves tokens and base URLs.
- HTML documentation is served from `docs/`; update it alongside code so non-developers can browse guides locally.
- Tests reside in `tests/` and mirror the package layout.

## Ecosystem & Links
- PyPI client: GitHub `@icakad` (`icakad` package).
- Short URL worker: GitHub `@shorturl` (`linkove.icu/api`).
- Pastebin worker: GitHub `@paste` (`linkove.icu` paste endpoints).
- Active server context: `xp97.icu`; all three projects stay in sync through their GitHub repositories.

## Build, Test, and Development Commands
- `python -m pip install -e .` — editable install for local hacking.
- `python -m build` — regenerate `dist/` artifacts after version bumps.
- `python -m unittest` or `python -m pytest` — run the test suite (ensure new helpers ship with coverage).
- `python -m icakad --help` — list CLI actions; running without arguments opens the HTML docs.

## Coding Style & Naming Conventions
- Target Python ≥3.8 with type hints; follow PEP 8 and keep lines ≤88 characters.
- Name branches `codex/<feature>` and prefer imperative commit titles.
- Export any new public function via `__all__`; prefix module-private helpers with an underscore.
- Keep JSON, HTML, and other assets in ASCII unless project requirements dictate otherwise.

## Testing Guidelines
- Mirror modules in `tests/` (e.g. `tests/test_icakad.py`) and mock network calls to keep the suite offline-friendly.
- Include regression tests when adjusting API parsing or CLI argument handling.
- Capture output written with `save_to=` in tests to guarantee the file workflows stay stable.

## Commit & Pull Request Guidelines
- Record executed build/test commands in each PR and link related worker changes when touching @shorturl or @paste.
- Provide screenshots or curl logs for API-facing changes when possible.
- Keep PR descriptions concise: problem, solution, verification.

## Security & Agent Integration Tips
- Load credentials from config files or environment variables; never commit tokens.
- Verify worker health with `curl https://linkove.icu/api/health` (or the staging equivalent at `https://xp97.icu`).
- Document cross-repo impacts in PRs so companion agents stay in sync.

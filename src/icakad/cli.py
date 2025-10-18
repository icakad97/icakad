"""Command-line interface for the icakad package."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Optional, Sequence

from . import (
    add_short_link,
    create_paste,
    delete_short_link,
    fetch_paste,
    list_pastes,
    list_short_links,
    print_json,
    update_short_link,
)
from .common import resolve_text_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="icakad",
        description="Interact with the icakad shorturl and paste services.",
    )
    parser.add_argument("--config", dest="config_path", help="Path to a config JSON file.")
    parser.add_argument("--token", help="Bearer token used for authenticated endpoints.")
    parser.add_argument("--shorturl-base", help="Override the short URL API base URL.")
    parser.add_argument("--paste-base", help="Override the paste API base URL.")

    subparsers = parser.add_subparsers(dest="command")

    # ---------------------------------------------------------------- shorturl
    shorturl_parser = subparsers.add_parser("shorturl", help="Short URL operations")
    shorturl_sub = shorturl_parser.add_subparsers(dest="action")

    shorturl_add = shorturl_sub.add_parser("add", help="Create or overwrite a slug")
    shorturl_add.add_argument("slug", help="Slug used in the short URL")
    shorturl_add.add_argument("url", help="Destination URL")
    shorturl_add.add_argument("--output", help="Write the API response to this JSON file.")
    shorturl_add.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    shorturl_edit = shorturl_sub.add_parser("update", help="Update the target URL for a slug")
    shorturl_edit.add_argument("slug", help="Slug to update")
    shorturl_edit.add_argument("url", help="New destination URL")
    shorturl_edit.add_argument("--output", help="Write the API response to this JSON file.")
    shorturl_edit.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    shorturl_del = shorturl_sub.add_parser("delete", help="Delete a slug from the service")
    shorturl_del.add_argument("slug", help="Slug to remove")
    shorturl_del.add_argument("--output", help="Write the API response to this JSON file.")
    shorturl_del.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    shorturl_list = shorturl_sub.add_parser("list", help="List all known short URLs")
    shorturl_list.add_argument("--output", help="Write the results to a JSON file.")
    shorturl_list.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    # ------------------------------------------------------------------- paste
    paste_parser = subparsers.add_parser("paste", help="Pastebin operations")
    paste_sub = paste_parser.add_subparsers(dest="action")

    paste_create = paste_sub.add_parser("create", help="Create a new paste")
    group = paste_create.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Inline text for the paste.")
    group.add_argument("--text-file", help="Read paste text from a file.")
    paste_create.add_argument("--id", dest="paste_id", help="Provide a custom paste identifier.")
    paste_create.add_argument(
        "--ttl",
        type=int,
        help="Seconds before the paste expires. Omit for no expiration.",
    )
    paste_create.add_argument(
        "--plain",
        action="store_true",
        help="Send the payload as text/plain instead of JSON.",
    )
    paste_create.add_argument("--output", help="Write the API response to this JSON file.")
    paste_create.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    paste_get = paste_sub.add_parser("get", help="Fetch a paste by ID")
    paste_get.add_argument("paste_id", help="Paste identifier to fetch")
    paste_get.add_argument("--raw", action="store_true", help="Return the raw text instead of metadata.")
    paste_get.add_argument("--output", help="Write the result to a file.")
    paste_get.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    paste_list = paste_sub.add_parser("list", help="List all pastes with metadata")
    paste_list.add_argument("--output", help="Write the results to a JSON file.")
    paste_list.add_argument("--quiet", action="store_true", help="Suppress stdout output.")

    return parser


def _common_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "config_path": getattr(args, "config_path", None),
        "token": getattr(args, "token", None),
        "base_url": getattr(args, "shorturl_base", None),
    }


def _paste_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "config_path": getattr(args, "config_path", None),
        "token": getattr(args, "token", None),
        "base_url": getattr(args, "paste_base", None),
    }


def _print_result(result: Any, quiet: bool, raw: bool = False) -> None:
    if quiet:
        return
    if raw and isinstance(result, str):
        print(result)
    else:
        print_json(result)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "shorturl":
        if args.action == "add":
            result = add_short_link(
                args.slug,
                args.url,
                save_to=args.output,
                **_common_kwargs(args),
            )
            _print_result(result, args.quiet)
            return 0
        if args.action == "update":
            result = update_short_link(
                args.slug,
                args.url,
                save_to=args.output,
                **_common_kwargs(args),
            )
            _print_result(result, args.quiet)
            return 0
        if args.action == "delete":
            result = delete_short_link(
                args.slug,
                save_to=args.output,
                **_common_kwargs(args),
            )
            _print_result(result, args.quiet)
            return 0
        if args.action == "list":
            result = list_short_links(
                save_to=args.output,
                print_output=not args.quiet,
                **_common_kwargs(args),
            )
            return 0
        parser.error("Please provide a shorturl action (add, update, delete, list).")

    if args.command == "paste":
        if args.action == "create":
            text = resolve_text_input(text=args.text, text_file=args.text_file)
            result = create_paste(
                text=text,
                paste_id=args.paste_id,
                ttl=args.ttl,
                as_plaintext=args.plain,
                save_to=args.output,
                **_paste_kwargs(args),
            )
            _print_result(result, args.quiet)
            return 0
        if args.action == "get":
            result = fetch_paste(
                args.paste_id,
                raw=args.raw,
                save_to=args.output,
                **_paste_kwargs(args),
            )
            _print_result(result, args.quiet, raw=args.raw)
            return 0
        if args.action == "list":
            result = list_pastes(
                save_to=args.output,
                print_output=not args.quiet,
                **_paste_kwargs(args),
            )
            return 0
        parser.error("Please provide a paste action (create, get, list).")

    parser.error("Unknown command. Use --help for usage details.")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

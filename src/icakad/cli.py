"""Команден интерфейс за инструментите на icakad."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from . import (
    APIError,
    __version__,
    add_link,
    delete_link,
    edit_link,
    get_paste_client,
    get_shorturl_client,
    list_links,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="icakad",
        description="CLI за управление на кратки линкове и paste услугата.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
        help="Показва версията и излиза.",
    )
    parser.add_argument(
        "--token",
        help="Bearer токен за автентикация (по подразбиране се чете от $ICAKAD_TOKEN).",
    )
    parser.add_argument(
        "--shorturl-base",
        help="Базов URL за услугата за кратки линкове.",
    )
    parser.add_argument(
        "--paste-base",
        help="Базов URL за paste услугата.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Показва отладъчна информация за HTTP заявките.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- shorturl ---
    short_parser = subparsers.add_parser(
        "shorturl", help="Операции за кратки линкове."
    )
    short_sub = short_parser.add_subparsers(dest="short_command", required=True)

    add_cmd = short_sub.add_parser("add", help="Създава или подменя slug.")
    add_cmd.add_argument("slug")
    add_cmd.add_argument("url")

    edit_cmd = short_sub.add_parser("edit", help="Актуализира съществуващ slug.")
    edit_cmd.add_argument("slug")
    edit_cmd.add_argument("url")

    delete_cmd = short_sub.add_parser("delete", help="Изтрива slug.")
    delete_cmd.add_argument("slug")

    list_cmd = short_sub.add_parser("list", help="Списък на всички slug-ове.")
    list_cmd.add_argument(
        "--json",
        action="store_true",
        help="Извежда резултата като JSON.",
    )

    # --- paste ---
    paste_parser = subparsers.add_parser("paste", help="Работа с paste услугата.")
    paste_sub = paste_parser.add_subparsers(dest="paste_command", required=True)

    paste_create = paste_sub.add_parser("create", help="Създава нов paste.")
    paste_create.add_argument("content", nargs="?", help="Съдържание или '-' за stdin.")
    paste_create.add_argument("--title")
    paste_create.add_argument("--syntax")
    paste_create.add_argument("--expires-in")
    paste_create.add_argument("--password")

    paste_show = paste_sub.add_parser("show", help="Показва paste по идентификатор.")
    paste_show.add_argument("paste_id")

    paste_delete = paste_sub.add_parser("delete", help="Изтрива paste.")
    paste_delete.add_argument("paste_id")

    return parser


def _read_content(argument: Optional[str]) -> str:
    if argument is None or argument == "-":
        return sys.stdin.read()
    return argument


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    token = args.token
    debug = args.debug

    try:
        if args.command == "shorturl":
            client = get_shorturl_client(
                base_url=args.shorturl_base,
                token=token,
                debug=debug,
            )
            if args.short_command == "add":
                payload = add_link(
                    slug=args.slug,
                    url=args.url,
                    client=client,
                )
                _echo_json(payload)
                return 0
            if args.short_command == "edit":
                payload = edit_link(
                    slug=args.slug,
                    new_url=args.url,
                    client=client,
                )
                _echo_json(payload)
                return 0
            if args.short_command == "delete":
                payload = delete_link(slug=args.slug, client=client)
                _echo_json(payload)
                return 0
            if args.short_command == "list":
                links = list_links(client=client)
                if args.json:
                    _echo_json(links)
                else:
                    for slug, url in sorted(links.items()):
                        print(f"{slug}\t{url}")
                return 0
        elif args.command == "paste":
            client = get_paste_client(
                base_url=args.paste_base,
                token=token,
                debug=debug,
            )
            if args.paste_command == "create":
                content = _read_content(args.content)
                payload = client.create(
                    content=content,
                    title=args.title,
                    syntax=args.syntax,
                    expires_in=args.expires_in,
                    password=args.password,
                )
                _echo_json(payload)
                return 0
            if args.paste_command == "show":
                payload = client.fetch(args.paste_id)
                _echo_json(payload)
                return 0
            if args.paste_command == "delete":
                payload = client.delete(args.paste_id)
                _echo_json(payload)
                return 0
    except APIError as exc:
        message = str(exc)
        if exc.payload is not None:
            try:
                detail = json.dumps(exc.payload, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                detail = str(exc.payload)
            message = f"{message}\n{detail}"
        print(message, file=sys.stderr)
        return exc.status or 1
    return 1


def _echo_json(data: Any) -> None:
    if isinstance(data, str):
        print(data)
        return
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

import argparse
from typing import TYPE_CHECKING

import mrpack.commands.diff
import mrpack.commands.list
from mrpack.output import render
from mrpack.types import GameVersion

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Modrinth-format (mrpack) modpack utilities.",
    )
    subparsers = parser.add_subparsers(required=True)

    parser_list = subparsers.add_parser(
        "list",
        help="list mods, with compatibility checks",
    )
    parser_list.set_defaults(command="list")
    parser_list.add_argument("mrpack_file", help="a Modrinth-format (mrpack) modpack")
    parser_list.add_argument(
        "--check-version",
        type=GameVersion,
        action="append",
        default=[],
        help=(
            "game version to check compatibility with; may be specified multiple times"
        ),
    )
    parser_list.add_argument(
        "--dev",
        action="store_true",
        help="display extra dev-related information",
    )
    parser_list.add_argument(
        "--csv",
        action="store_true",
        help="generate CSV instead of human-readable output",
    )

    parser_diff = subparsers.add_parser("diff", help="diff modpacks")
    parser_diff.set_defaults(command="diff")
    parser_diff.add_argument("old_file", help="a Modrinth-format (mrpack) modpack")
    parser_diff.add_argument("new_file", help="a Modrinth-format (mrpack) modpack")
    parser_diff.add_argument(
        "--csv",
        action="store_true",
        help="generate CSV instead of human-readable output",
    )

    args = parser.parse_args(args=argv)

    if args.command == "list":
        out = mrpack.commands.list.run(
            args.mrpack_file,
            frozenset(args.check_version),
            dev=args.dev,
        )
        print(render(out, csv=args.csv))
    elif args.command == "diff":
        out = mrpack.commands.diff.run(
            args.old_file,
            args.new_file,
        )
        print(render(out, csv=args.csv))
    else:
        raise NotImplementedError("Unknown subcommand")

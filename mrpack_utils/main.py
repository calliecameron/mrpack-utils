import argparse
from collections.abc import Sequence

import mrpack_utils.commands.list
from mrpack_utils.mods import GameVersion
from mrpack_utils.output import render, render_csv


def main(argv: Sequence[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Modrinth-format (mrpack) modpack utilities.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="generate CSV instead of human-readable output",
    )
    subparsers = parser.add_subparsers(required=True)

    parser_list = subparsers.add_parser("list", help="list mods, with compatibility checks")
    parser_list.set_defaults(command="list")
    parser_list.add_argument("mrpack_file", help="a Modrinth-format (mrpack) modpack")
    parser_list.add_argument(
        "--game-version",
        type=GameVersion,
        action="append",
        default=[],
        help="game version to check compatibility with; may be specified multiple times",
    )

    args = parser.parse_args(args=argv)

    if args.command == "list":
        out = mrpack_utils.commands.list.run(
            args.mrpack_file,
            frozenset(args.game_version),
        )
    else:
        raise NotImplementedError("Unknown subcommand")

    if args.csv:
        print(render_csv(out))
    else:
        print(render(out))

import argparse
import csv
import sys
from collections.abc import Mapping, Sequence, Set

import tabulate

from mrpack_utils.mods import GameVersion, Mod, Modpack, MrpackFile

Table = Sequence[tuple[str, ...]]
IncompatibleMods = Mapping[GameVersion, Set[Mod]]


def make_table(modpack: Modpack, game_versions: Set[GameVersion]) -> tuple[Table, IncompatibleMods]:
    incompatible: dict[GameVersion, set[Mod]] = {version: set() for version in game_versions}
    sorted_versions = sorted(game_versions)
    table = [
        tuple(
            ["Name", "Link", "Installed version", "On client", "On server", "Latest game version"]
            + [str(version) for version in sorted_versions],
        ),
    ]

    for mod in sorted(modpack.mods.values(), key=lambda m: m.name.lower()):
        row = [
            mod.name,
            mod.link,
            mod.version,
            mod.overridden_env.client.name.lower(),
            mod.overridden_env.server.name.lower(),
            str(mod.latest_game_version),
        ]
        for version in sorted_versions:
            if mod.compatible_with(version):
                row.append("yes")
            else:
                row.append("no")
                incompatible[version].add(mod)
        table.append(tuple(row))

    return table, {version: frozenset(incompatible[version]) for version in incompatible}


def write_csv(table: Table) -> None:
    csv.writer(sys.stdout).writerows(table)


def write_table(table: Table) -> None:
    print(tabulate.tabulate(table, headers="firstrow", tablefmt="github"))


def write_missing(mods: Set[str]) -> None:
    if mods:
        print("\nMods supposed to be on Modrinth, but not found:")
        for mod in sorted(mods, key=lambda m: m.lower()):
            print("  " + mod)


def write_unknown(mods: Set[str]) -> None:
    if mods:
        print("\nUnknown mods (probably from CurseForge) - must be checked manually:")
        for mod in sorted(mods, key=lambda m: m.lower()):
            print("  " + mod)


def write_incompatible(
    num_mods: int,
    game_versions: Set[GameVersion],
    mrpack_game_version: GameVersion,
    incompatible: IncompatibleMods,
) -> None:
    print("\nModpack game version: " + str(mrpack_game_version))

    for version in sorted(game_versions):
        print(f"\nFor version {version}:")
        mods = incompatible[version]
        if mods:
            print("  %d out of %d mods are incompatible with this version:" % (len(mods), num_mods))
            for mod in sorted(mods, key=lambda m: m.name.lower()):
                print("    " + mod.name)
        else:
            print("  All mods are compatible with this version")


def check_compatibility(versions: Sequence[str], mrpack_file: str, output_csv: bool) -> None:
    game_versions = {GameVersion(version) for version in versions}
    mrpack = MrpackFile.from_file(mrpack_file)
    (modpack,) = Modpack.load(mrpack)
    game_versions.add(modpack.game_version)

    table, incompatible = make_table(modpack, game_versions)

    if output_csv:
        write_csv(table)
    else:
        write_table(table)
        write_missing(modpack.missing_mods)
        write_unknown(modpack.unknown_mods)
        write_incompatible(len(table) - 1, game_versions, modpack.game_version, incompatible)


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Check Minecraft mods for compatibility with game versions.",
    )
    parser.add_argument("mrpack_file", help="a Modrinth-format (mrpack) modpack")
    parser.add_argument(
        "--version",
        action="append",
        default=[],
        help="game version to check; may be specified multiple times",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="generate CSV instead of a human-readable table",
    )
    args = parser.parse_args()
    check_compatibility(args.version, args.mrpack_file, args.csv)

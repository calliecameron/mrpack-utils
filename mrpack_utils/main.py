import argparse
from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet

from mrpack_utils.mods import GameVersion, Mod, Modpack
from mrpack_utils.output import IncompatibleMods, List, Set, Table

IncompatibleModMap = Mapping[GameVersion, AbstractSet[Mod]]


def make_table(
    modpack: Modpack,
    game_versions: AbstractSet[GameVersion],
) -> tuple[Table, IncompatibleModMap]:
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

    return Table(table), {version: frozenset(incompatible[version]) for version in incompatible}


def check_compatibility(versions: Sequence[str], mrpack_file: str, output_csv: bool) -> None:
    game_versions = {GameVersion(version) for version in versions}
    (modpack,) = Modpack.from_files(mrpack_file)
    game_versions.add(modpack.game_version)

    table, incompatible = make_table(modpack, game_versions)

    if output_csv:
        print(table.render_csv())
    else:
        out = [
            table.render(),
            Set("Mods supposed to be on Modrinth, but not found", modpack.missing_mods).render(),
            Set(
                "Unknown mods (probably from CurseForge) - must be checked manually",
                modpack.unknown_mods,
            ).render(),
            List(["Modpack game version: " + str(modpack.game_version)]).render(),
        ] + [
            IncompatibleMods(
                num_mods=len(modpack.mods),
                game_version=str(version),
                mods={mod.name for mod in incompatible[version]},
            ).render()
            for version in sorted(game_versions)
        ]
        print("\n\n".join([item for item in out if item]))


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

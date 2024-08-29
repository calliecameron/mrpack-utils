import pathlib
from collections.abc import Set as AbstractSet

from frozendict import frozendict

from mrpack_utils.mods import GameVersion, Mod, Modpack
from mrpack_utils.output import Element, IncompatibleMods, List, Set, Table

IncompatibleModMap = frozendict[GameVersion, frozenset[Mod]]


def _make_table(
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

    return Table(table), frozendict(
        {version: frozenset(incompatible[version]) for version in incompatible},
    )


def run(mrpack_file: str, game_versions: AbstractSet[GameVersion]) -> tuple[Element, ...]:
    (modpack,) = Modpack.from_files(mrpack_file)
    game_versions = set(game_versions)
    game_versions.add(modpack.game_version)
    table, incompatible = _make_table(modpack, game_versions)

    return tuple(
        [
            table,
            Set("Mods supposed to be on Modrinth, but not found", modpack.missing_mods),
            Set(
                "Unknown mods (probably from CurseForge) - must be checked manually",
                {pathlib.PurePath(file).name for file in modpack.unknown_mods},
            ),
            List(["Modpack game version: " + str(modpack.game_version)]),
        ]
        + [
            IncompatibleMods(
                num_mods=len(modpack.mods),
                game_version=str(version),
                mods={mod.name for mod in incompatible[version]},
            )
            for version in sorted(game_versions)
        ],
    )

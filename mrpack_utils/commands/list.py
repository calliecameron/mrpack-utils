from collections.abc import Sequence
from collections.abc import Set as AbstractSet

from frozendict import frozendict

from mrpack_utils.mods import GameVersion, Mod, Modpack
from mrpack_utils.output import Element, IncompatibleMods, Set, Table

IncompatibleModMap = frozendict[GameVersion, frozenset[Mod]]

_NAME = "Name"
_LINK = "Link"
_INSTALLED_VERSION = "Installed version"
_CLIENT = "On client"
_SERVER = "On server"
_LATEST_GAME_VERSION = "Latest game version"
_LICENSE = "License"
_MODRINTH_CLIENT = "Modrinth client"
_MODRINTH_SERVER = "Modrinth server"
_SOURCE = "Source"
_ISSUES = "Issues"


def _headers(game_versions: AbstractSet[GameVersion], dev: bool) -> list[str]:
    out = [_NAME, _LINK, _INSTALLED_VERSION, _CLIENT, _SERVER, _LATEST_GAME_VERSION] + [
        str(version) for version in sorted(game_versions)
    ]
    if dev:
        out += [_LICENSE, _MODRINTH_CLIENT, _MODRINTH_SERVER, _SOURCE, _ISSUES]
    return out


def _empty_row(headers: Sequence[str]) -> list[str]:
    return [""] * len(headers)


def _modpack_data(modpack: Modpack, headers: Sequence[str]) -> list[list[str]]:
    def _row(name: str, version: str) -> list[str]:
        row = _empty_row(headers)
        row[headers.index(_NAME)] = name
        row[headers.index(_INSTALLED_VERSION)] = version
        return row

    return [
        _row("modpack: " + modpack.name, modpack.version),
        _row("minecraft", str(modpack.game_version)),
    ] + [_row(name, version) for (name, version) in sorted(modpack.dependencies.items())]


def _mods(
    modpack: Modpack,
    game_versions: AbstractSet[GameVersion],
    dev: bool,
) -> tuple[list[list[str]], IncompatibleModMap]:
    incompatible: dict[GameVersion, set[Mod]] = {version: set() for version in game_versions}
    out = []

    for mod in sorted(modpack.mods.values(), key=lambda m: m.name.lower()):
        row = [
            mod.name,
            mod.link,
            mod.version,
            mod.overridden_env.client.name.lower(),
            mod.overridden_env.server.name.lower(),
            str(mod.latest_game_version),
        ]
        for version in sorted(game_versions):
            if mod.compatible_with(version):
                row.append("yes")
            else:
                row.append("no")
                incompatible[version].add(mod)
        if dev:
            row += [
                mod.mod_license,
                mod.original_env.client.name.lower(),
                mod.original_env.server.name.lower(),
                mod.source_url,
                mod.issues_url,
            ]
        out.append(row)

    return out, frozendict(
        {version: frozenset(incompatible[version]) for version in incompatible},
    )


def _unknown_mods(
    modpack: Modpack,
    game_versions: AbstractSet[GameVersion],
    dev: bool,
) -> list[list[str]]:
    out = []
    versions = ["check manually"] * len(game_versions)
    for name, version in sorted(modpack.unknown_mods.items()):
        row = [
            name,
            "unknown - probably CurseForge",
            version,
            "unknown",
            "unknown",
            "unknown",
            *versions,
        ]
        if dev:
            row += [""] * 5
        out.append(row)
    return out


def _other_files(modpack: Modpack, headers: Sequence[str]) -> list[list[str]]:
    out = []
    for name, version in sorted(modpack.other_files.items()):
        row = _empty_row(headers)
        row[headers.index(_NAME)] = name
        row[headers.index(_INSTALLED_VERSION)] = version
        row[headers.index(_LINK)] = "non-mod file"
        out.append(row)
    return out


def run(
    mrpack_file: str,
    game_versions: AbstractSet[GameVersion],
    dev: bool,
) -> tuple[Element, ...]:
    (modpack,) = Modpack.from_files(mrpack_file)
    game_versions = set(game_versions)
    game_versions.add(modpack.game_version)

    headers = _headers(game_versions, dev)
    modpack_data = _modpack_data(modpack, headers)
    mods, incompatible = _mods(modpack, game_versions, dev)
    unknown_mods = _unknown_mods(modpack, game_versions, dev)
    other_files = _other_files(modpack, headers)

    return tuple(
        [
            Table(
                [
                    headers,
                    *modpack_data,
                    *mods,
                    *unknown_mods,
                    *other_files,
                ],
            ),
            Set("Mods supposed to be on Modrinth, but not found", modpack.missing_mods),
        ]
        + [
            IncompatibleMods(
                num_mods=len(modpack.mods),
                game_version=str(version),
                mods={mod.name for mod in incompatible[version]},
                curseforge_warning=len(modpack.unknown_mods) > 0,
            )
            for version in sorted(game_versions)
        ],
    )

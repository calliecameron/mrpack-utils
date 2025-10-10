import binascii
from pathlib import PurePath
from typing import TYPE_CHECKING

from frozendict import frozendict

from mrpack.moddb import ModDB
from mrpack.modpack import Mod, Modpack
from mrpack.mrpack import Mrpack
from mrpack.output import (
    Element,
    IncompatibleMods,
    MissingMods,
    Table,
    UnknownDependencies,
)
from mrpack.types import GameVersion

if TYPE_CHECKING:
    from collections.abc import Sequence, Set

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


def _headers(game_versions: Set[GameVersion], *, dev: bool) -> list[str]:
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
        _row("modpack: " + modpack.index.name, modpack.index.version),
        _row("minecraft", str(modpack.index.dependencies.game_version)),
    ] + [
        _row(name, version)
        for (name, version) in sorted(
            modpack.index.dependencies.others.items(),
            key=lambda i: i[0].lower(),
        )
    ]


def _mods(
    modpack: Modpack,
    game_versions: Set[GameVersion],
    *,
    dev: bool,
) -> tuple[list[list[str]], IncompatibleModMap]:
    incompatible: dict[GameVersion, set[Mod]] = {
        version: set() for version in game_versions
    }
    out = []

    for mod in sorted(modpack.mods.values(), key=lambda m: m.project.title.lower()):
        row = [
            mod.project.title,
            mod.link,
            mod.version_number,
            mod.env.client.name.lower(),
            mod.env.server.name.lower(),
            str(mod.latest_game_version or ""),
        ]
        for version in sorted(game_versions):
            if mod.compatible_with(version):
                row.append("yes")
            else:
                row.append("no")
                incompatible[version].add(mod)
        if dev:
            row += [
                mod.project.project_license,
                mod.project.env.client.name.lower(),
                mod.project.env.server.name.lower(),
                mod.project.source_url,
                mod.project.issues_url,
            ]
        out.append(row)

    return out, frozendict(
        {version: frozenset(incompatible[version]) for version in incompatible},
    )


def _unknown_mods(
    modpack: Modpack,
    game_versions: Set[GameVersion],
    *,
    dev: bool,
) -> list[list[str]]:
    out = []
    versions = ["check manually"] * len(game_versions)
    for path, override in sorted(
        modpack.overrides.items(),
        key=lambda i: str(i[0]).lower(),
    ):
        if path.parts[1] == "mods":
            row = [
                str(path),
                "unknown - probably CurseForge",
                f"{binascii.crc32(override.data):08x}",
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
    for path, override in sorted(
        modpack.overrides.items(),
        key=lambda i: str(i[0]).lower(),
    ):
        if path.parts[1] != "mods":
            row = _empty_row(headers)
            row[headers.index(_NAME)] = str(path)
            row[headers.index(_INSTALLED_VERSION)] = (
                f"{binascii.crc32(override.data):08x}"
            )
            row[headers.index(_LINK)] = "non-mod file"
            out.append(row)
    return out


def run(
    mrpack_file: str,
    game_versions: Set[GameVersion],
    *,
    dev: bool,
) -> tuple[Element, ...]:
    mrp = Mrpack.from_file(mrpack_file)
    db = ModDB.load([mrp], fetch_versions=True)
    modpack = Modpack.load(mrp, db)
    game_versions = set(game_versions)
    game_versions.add(modpack.index.dependencies.game_version)

    headers = _headers(game_versions, dev=dev)
    modpack_data = _modpack_data(modpack, headers)
    mods, incompatible = _mods(modpack, game_versions, dev=dev)
    unknown_mods = _unknown_mods(modpack, game_versions, dev=dev)
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
            UnknownDependencies(modpack.index.dependencies.unknown_dependencies),
            MissingMods(
                {
                    str(PurePath(*m.index_entry.path.parts[1:]))
                    for m in modpack.project_missing_mods
                }
                | {
                    str(PurePath(*m.index_entry.path.parts[1:]))
                    for m in modpack.file_missing_mods
                },
            ),
        ]
        + [
            IncompatibleMods(
                num_mods=len(modpack.mods),
                game_version=str(version),
                mods={mod.project.title for mod in incompatible[version]},
                curseforge_warning=len(
                    [p for p in modpack.overrides if p.parts[1] == "mods"],
                )
                > 0,
            )
            for version in sorted(game_versions)
        ],
    )

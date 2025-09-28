import binascii
from collections.abc import Mapping
from pathlib import PurePath

from mrpack.moddb import ModDB
from mrpack.modpack import Modpack
from mrpack.mrpack import Mrpack
from mrpack.output import Element, MissingMods, Table, UnknownDependencies


def _diff(old: Mapping[str, str], new: Mapping[str, str]) -> list[tuple[str, str, str]]:
    kept_keys = old.keys() & new.keys()
    added_keys = new.keys() - old.keys()
    removed_keys = old.keys() - new.keys()

    updated_keys = {k for k in kept_keys if new[k] != old[k]}

    return [
        *[(k, old[k], new[k]) for k in sorted(updated_keys, key=lambda s: s.lower())],
        *[(k, "", new[k]) for k in sorted(added_keys, key=lambda s: s.lower())],
        *[(k, old[k], "") for k in sorted(removed_keys, key=lambda s: s.lower())],
    ]


def _modpack_data(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    out = []
    if old.index.name != new.index.name:
        out.append(("modpack name", old.index.name, new.index.name))
    if old.index.version != new.index.version:
        out.append(("modpack version", old.index.version, new.index.version))
    if old.index.dependencies.game_version != new.index.dependencies.game_version:
        out.append(
            (
                "minecraft",
                str(old.index.dependencies.game_version),
                str(new.index.dependencies.game_version),
            ),
        )

    return out + _diff(old.index.dependencies.others, new.index.dependencies.others)


def _mods(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(
        {mod.project.title: mod.version_number for mod in old.mods.values()},
        {mod.project.title: mod.version_number for mod in new.mods.values()},
    )


def _unknown_mods(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(
        {
            str(o.path): f"{binascii.crc32(o.data):08x}"
            for o in old.overrides.values()
            if o.path.parts[1] == "mods"
        },
        {
            str(o.path): f"{binascii.crc32(o.data):08x}"
            for o in new.overrides.values()
            if o.path.parts[1] == "mods"
        },
    )


def _other_files(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(
        {
            str(o.path): f"{binascii.crc32(o.data):08x}"
            for o in old.overrides.values()
            if o.path.parts[1] != "mods"
        },
        {
            str(o.path): f"{binascii.crc32(o.data):08x}"
            for o in new.overrides.values()
            if o.path.parts[1] != "mods"
        },
    )


def run(old_file: str, new_file: str) -> tuple[Element, ...]:
    old_mrpack = Mrpack.from_file(old_file)
    new_mrpack = Mrpack.from_file(new_file)
    db = ModDB.load([old_mrpack, new_mrpack], fetch_versions=False)
    old = Modpack.load(old_mrpack, db)
    new = Modpack.load(new_mrpack, db)

    return (
        Table(
            [
                ["Name", "Old", "New"],
                *_modpack_data(old, new),
                *_mods(old, new),
                *_unknown_mods(old, new),
                *_other_files(old, new),
            ],
        ),
        UnknownDependencies(
            old.index.dependencies.unknown_dependencies
            | new.index.dependencies.unknown_dependencies,
        ),
        MissingMods(
            {
                str(PurePath(*m.index_entry.path.parts[1:]))
                for m in old.project_missing_mods
            }
            | {
                str(PurePath(*m.index_entry.path.parts[1:]))
                for m in old.file_missing_mods
            }
            | {
                str(PurePath(*m.index_entry.path.parts[1:]))
                for m in new.project_missing_mods
            }
            | {
                str(PurePath(*m.index_entry.path.parts[1:]))
                for m in new.file_missing_mods
            },
        ),
    )

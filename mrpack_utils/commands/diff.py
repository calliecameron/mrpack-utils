from collections.abc import Mapping

from mrpack_utils.mods import Modpack
from mrpack_utils.output import Element, MissingMods, Table


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
    if old.name != new.name:
        out.append(("modpack name", old.name, new.name))
    if old.version != new.version:
        out.append(("modpack version", old.version, new.version))
    if old.game_version != new.game_version:
        out.append(("minecraft", str(old.game_version), str(new.game_version)))

    return out + _diff(old.dependencies, new.dependencies)


def _mods(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(
        {mod.name: mod.version for mod in old.mods.values()},
        {mod.name: mod.version for mod in new.mods.values()},
    )


def _unknown_mods(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(old.unknown_mods, new.unknown_mods)


def _other_files(old: Modpack, new: Modpack) -> list[tuple[str, str, str]]:
    return _diff(old.other_files, new.other_files)


def run(old_file: str, new_file: str) -> tuple[Element, ...]:
    old, new = Modpack.from_files(old_file, new_file)

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
        MissingMods(old.missing_mods | new.missing_mods),
    )

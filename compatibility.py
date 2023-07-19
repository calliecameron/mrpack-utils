#!/usr/bin/env python3

import argparse
import csv
import functools
import json
import re
import sys
import zipfile
from collections.abc import Mapping, Sequence, Set

import requests
import tabulate


class ModpackException(Exception):
    pass


@functools.total_ordering
class GameVersion:
    def __init__(self, version: str) -> None:
        super().__init__()
        match = re.fullmatch(r"[0-9]+\.[0-9]+(\.[0-9]+)?", version)
        if match is None:
            raise ValueError("Not a valid game version: " + version)
        self._version = tuple(int(segment) for segment in version.split("."))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version == other._version

    def __hash__(self) -> int:
        return hash(self._version)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version < other._version

    def __repr__(self) -> str:
        return ".".join(str(segment) for segment in self._version)

    @staticmethod
    def from_list(versions: Sequence[str]) -> "frozenset[GameVersion]":
        # We deliberately skip over any versions that don't parse
        out = set()
        for version in versions:
            try:
                out.add(GameVersion(version))
            except ValueError:
                pass
        return frozenset(out)


@functools.total_ordering
class Mod:
    def __init__(self, mod_id: str, name: str, slug: str, versions: Set[GameVersion]) -> None:
        super().__init__()
        self._id = mod_id
        self._name = name
        self._link = "https://modrinth.com/mod/" + slug
        self._game_versions = frozenset(versions)
        self._latest_game_version = max(self._game_versions)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mod):
            raise NotImplementedError
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Mod):
            raise NotImplementedError
        return self._name.lower() < other._name.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def link(self) -> str:
        return self._link

    @property
    def game_versions(self) -> frozenset[GameVersion]:
        return self._game_versions

    @property
    def latest_game_version(self) -> GameVersion:
        return self._latest_game_version

    def compatible_with(self, version: GameVersion) -> bool:
        return version in self._game_versions


def load_mrpack(mrpack: str) -> tuple[frozenset[str], GameVersion]:
    try:
        with zipfile.ZipFile(mrpack) as z:
            with z.open("modrinth.index.json") as f:
                j = json.load(f)

        return (
            frozenset(file["hashes"]["sha512"] for file in j["files"]),
            GameVersion(j["dependencies"]["minecraft"]),
        )
    except Exception as e:
        raise ModpackException("Failed to load mrpack file: " + str(e)) from e


def load_mods(hashes: Set[str]) -> frozenset[Mod]:
    versions_response = requests.post(
        "https://api.modrinth.com/v2/version_files",
        json={"hashes": sorted(hashes), "algorithm": "sha512"},
        timeout=10,
    )
    versions_response.raise_for_status()
    versions = versions_response.json()

    ids = set(versions[hash]["project_id"] for hash in versions)

    projects_response = requests.get(
        "https://api.modrinth.com/v2/projects",
        {"ids": "[" + ", ".join('"%s"' % id for id in sorted(ids)) + "]"},
        timeout=10,
    )
    projects_response.raise_for_status()
    projects = projects_response.json()

    mods = set()
    for project in projects:
        versions = GameVersion.from_list(project["game_versions"])
        mods.add(Mod(project["id"], project["title"], project["slug"], versions))

    return frozenset(mods)


Table = Sequence[tuple[str, ...]]
IncompatibleMods = Mapping[GameVersion, Set[Mod]]


def make_table(mods: Set[Mod], game_versions: Set[GameVersion]) -> tuple[Table, IncompatibleMods]:
    incompatible: dict[GameVersion, set[Mod]] = {version: set() for version in game_versions}
    sorted_versions = sorted(game_versions)
    table = [
        tuple(
            ["Name", "Link", "Latest game version"] + [str(version) for version in sorted_versions]
        )
    ]

    for mod in sorted(mods):
        row = [mod.name, mod.link, str(mod.latest_game_version)]
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


def write_incompatible(
    num_mods: int,
    game_versions: Set[GameVersion],
    mrpack_game_version: GameVersion,
    incompatible: IncompatibleMods,
) -> None:
    print("\nModpack game version: " + str(mrpack_game_version))

    for version in sorted(game_versions):
        print("\nFor version %s:" % version)
        mods = incompatible[version]
        if mods:
            print("  %d out of %d mods are incompatible with this version:" % (len(mods), num_mods))
            for mod in sorted(mods):
                print("    " + mod.name)
        else:
            print("  All mods are compatible with this version")


def check_compatibility(versions: Sequence[str], mrpack_file: str, output_csv: bool) -> None:
    game_versions = set(GameVersion(version) for version in versions)
    hashes, mrpack_game_version = load_mrpack(mrpack_file)
    game_versions.add(mrpack_game_version)
    mods = load_mods(hashes)

    table, incompatible = make_table(mods, game_versions)

    if output_csv:
        write_csv(table)
    else:
        write_table(table)
        write_incompatible(len(table) - 1, game_versions, mrpack_game_version, incompatible)


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("mrpack_file")
    parser.add_argument("--check-version", action="append", default=[])
    parser.add_argument("--csv", action="store_true")
    args = parser.parse_args()
    check_compatibility(args.check_version, args.mrpack_file, args.csv)


if __name__ == "__main__":  # pragma: no cover
    main()

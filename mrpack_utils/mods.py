import contextlib
import functools
import json
import pathlib
import re
import zipfile
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, TypeAlias, cast

import requests
from frozendict import frozendict


class ModpackError(Exception):
    pass


VersionHash: TypeAlias = str
ProjectID: TypeAlias = str


class Requirement(Enum):
    UNKNOWN = auto()
    REQUIRED = auto()
    OPTIONAL = auto()
    UNSUPPORTED = auto()

    @staticmethod
    def from_str(s: str) -> "Requirement":
        if not s:
            return Requirement.UNKNOWN
        if s == "required":
            return Requirement.REQUIRED
        if s == "optional":
            return Requirement.OPTIONAL
        if s == "unsupported":
            return Requirement.UNSUPPORTED
        raise ValueError(
            "Requirement value must be one of {required, optional, unsupported}, got '" + s + "'",
        )


@dataclass(frozen=True, kw_only=True)
class Env:
    client: Requirement
    server: Requirement

    @staticmethod
    def from_dict(env: Mapping[str, str]) -> "Env":
        if env.keys() != frozenset(["client", "server"]):
            raise ValueError("Env must have keys {client, server}, got " + str(env.keys()))
        return Env(
            client=Requirement.from_str(env["client"]),
            server=Requirement.from_str(env["server"]),
        )


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
            with contextlib.suppress(ValueError):
                out.add(GameVersion(version))
        return frozenset(out)


class _MrpackFile:
    def __init__(
        self,
        *,
        name: str,
        version: str,
        game_version: GameVersion,
        mod_hashes: Set[VersionHash],
        mod_jars: Mapping[VersionHash, str],
        mod_envs: Mapping[VersionHash, Env],
        unknown_mods: Set[str],
    ) -> None:
        super().__init__()
        self._name = name
        self._version = version
        self._game_version = game_version
        self._mod_hashes = frozenset(mod_hashes)
        self._mod_jars = frozendict(mod_jars)
        self._mod_envs = frozendict(mod_envs)
        self._unknown_mods = frozenset(unknown_mods)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def game_version(self) -> GameVersion:
        return self._game_version

    @property
    def mod_hashes(self) -> frozenset[VersionHash]:
        return self._mod_hashes

    @property
    def mod_jars(self) -> frozendict[VersionHash, str]:
        return self._mod_jars

    @property
    def mod_envs(self) -> frozendict[VersionHash, Env]:
        return self._mod_envs

    @property
    def unknown_mods(self) -> frozenset[str]:
        return self._unknown_mods

    @staticmethod
    def from_file(filename: str) -> "_MrpackFile":
        try:
            with zipfile.ZipFile(filename) as z:
                with z.open("modrinth.index.json") as f:
                    j = json.load(f)

                unknown_mods = set()
                for file in z.namelist():
                    path = pathlib.PurePath(file)
                    if path.suffix == ".jar" and str(path.parent) in (
                        "overrides/mods",
                        "server-overrides/mods",
                        "client-overrides/mods",
                    ):
                        unknown_mods.add(path.name)

            return _MrpackFile(
                name=j["name"],
                version=j["versionId"],
                game_version=GameVersion(j["dependencies"]["minecraft"]),
                mod_hashes=frozenset(file["hashes"]["sha512"] for file in j["files"]),
                mod_jars={
                    file["hashes"]["sha512"]: file["path"].split("/")[-1] for file in j["files"]
                },
                mod_envs={
                    file["hashes"]["sha512"]: Env.from_dict(file["env"])
                    for file in j["files"]
                    if "env" in file
                },
                unknown_mods=unknown_mods,
            )
        except Exception as e:
            raise ModpackError("Failed to load mrpack file: " + str(e)) from e


@dataclass(frozen=True, kw_only=True)
class _ModStub:
    name: str
    slug: str
    env: Env
    mod_license: str
    source_url: str
    issues_url: str
    game_versions: Set[GameVersion]


class Mod:
    def __init__(
        self,
        *,
        name: str,
        slug: str,
        version: str,
        original_env: Env,
        overridden_env: Env,
        mod_license: str,
        source_url: str,
        issues_url: str,
        game_versions: Set[GameVersion],
    ) -> None:
        super().__init__()
        self._name = name
        self._link = "https://modrinth.com/mod/" + slug
        self._version = version
        self._original_env = original_env
        self._overridden_env = overridden_env
        self._mod_license = mod_license
        self._source_url = source_url
        self._issues_url = issues_url
        self._game_versions = frozenset(game_versions)
        self._latest_game_version = max(self._game_versions)

    @property
    def name(self) -> str:
        return self._name

    @property
    def link(self) -> str:
        return self._link

    @property
    def version(self) -> str:
        return self._version

    @property
    def original_env(self) -> Env:
        return self._original_env

    @property
    def overridden_env(self) -> Env:
        return self._overridden_env

    @property
    def mod_license(self) -> str:
        return self._mod_license

    @property
    def source_url(self) -> str:
        return self._source_url

    @property
    def issues_url(self) -> str:
        return self._issues_url

    @property
    def game_versions(self) -> frozenset[GameVersion]:
        return self._game_versions

    @property
    def latest_game_version(self) -> GameVersion:
        return self._latest_game_version

    def compatible_with(self, version: GameVersion) -> bool:
        return version in self._game_versions


class Modpack:
    def __init__(
        self,
        *,
        name: str,
        version: str,
        game_version: GameVersion,
        mods: Mapping[ProjectID, Mod],
        missing_mods: Set[str],
        unknown_mods: Set[str],
    ) -> None:
        super().__init__()
        self._name = name
        self._version = version
        self._game_version = game_version
        self._mods = frozendict(mods)
        self._missing_mods = frozenset(missing_mods)
        self._unknown_mods = frozenset(unknown_mods)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def game_version(self) -> GameVersion:
        return self._game_version

    @property
    def mods(self) -> frozendict[ProjectID, Mod]:
        return self._mods

    @property
    def missing_mods(self) -> frozenset[str]:
        return self._missing_mods

    @property
    def unknown_mods(self) -> frozenset[str]:
        return self._unknown_mods

    @staticmethod
    def _fetch_versions(
        hashes: Set[VersionHash],
    ) -> tuple[dict[VersionHash, dict[str, Any]], frozenset[VersionHash]]:
        versions_response = requests.post(
            "https://api.modrinth.com/v2/version_files",
            json={"hashes": sorted(hashes), "algorithm": "sha512"},
            timeout=10,
        )
        versions_response.raise_for_status()
        versions = versions_response.json()

        known_hashes = frozenset(
            {
                file["hashes"]["sha512"]
                for version in versions
                for file in versions[version]["files"]
            },
        )

        return versions, known_hashes

    @staticmethod
    def _fetch_projects(versions: Mapping[VersionHash, Mapping[str, Any]]) -> list[dict[str, Any]]:
        ids = {versions[mod_hash]["project_id"] for mod_hash in versions}
        projects_response = requests.get(
            "https://api.modrinth.com/v2/projects",
            {"ids": "[" + ", ".join(f'"{mod_id}"' for mod_id in sorted(ids)) + "]"},
            timeout=10,
        )
        projects_response.raise_for_status()
        return cast(list[dict[str, Any]], projects_response.json())

    @staticmethod
    def _load(*mrpacks: _MrpackFile) -> "tuple[Modpack, ...]":
        all_hashes: set[VersionHash] = set()
        for mrpack in mrpacks:
            all_hashes |= mrpack.mod_hashes

        versions, known_hashes = Modpack._fetch_versions(all_hashes)
        projects = Modpack._fetch_projects(versions)

        mod_stubs = {}
        for project in projects:
            try:
                mod_stubs[project["id"]] = _ModStub(
                    name=project["title"],
                    slug=project["slug"],
                    env=Env(
                        client=Requirement.from_str(project.get("client", "")),
                        server=Requirement.from_str(project.get("server", "")),
                    ),
                    mod_license="" if "license" not in project else project["license"]["id"],
                    source_url=project.get("source_url", ""),
                    issues_url=project.get("issues_url", ""),
                    game_versions=GameVersion.from_list(project["game_versions"]),
                )
            except Exception as e:  # noqa: PERF203
                raise ModpackError(f"Failed to load mod {project['title']}: {e}") from e

        modpacks = []
        for mrpack in mrpacks:
            mods = {}
            missing_mods = set()
            for mod_hash in mrpack.mod_hashes:
                if mod_hash in known_hashes:
                    mod_id = versions[mod_hash]["project_id"]
                    mod_stub = mod_stubs[mod_id]
                    mods[mod_id] = Mod(
                        name=mod_stub.name,
                        slug=mod_stub.slug,
                        version=versions[mod_hash]["version_number"],
                        original_env=mod_stub.env,
                        overridden_env=mrpack.mod_envs.get(mod_hash, mod_stub.env),
                        mod_license=mod_stub.mod_license,
                        source_url=mod_stub.source_url,
                        issues_url=mod_stub.issues_url,
                        game_versions=mod_stub.game_versions,
                    )
                else:
                    missing_mods.add(mrpack.mod_jars[mod_hash])
            modpacks.append(
                Modpack(
                    name=mrpack.name,
                    version=mrpack.version,
                    game_version=mrpack.game_version,
                    mods=mods,
                    missing_mods=missing_mods,
                    unknown_mods=mrpack.unknown_mods,
                ),
            )

        return tuple(modpacks)

    @staticmethod
    def from_files(*files: str) -> "tuple[Modpack, ...]":
        return Modpack._load(*[_MrpackFile.from_file(f) for f in files])

import binascii
import sys
from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass
from typing import Any, cast

import requests
from frozendict import frozendict
from requests.utils import requote_uri

from mrpack_utils.mrpack import Mrpack
from mrpack_utils.types import Env, GameVersion, Requirement, Sha512


class ModpackError(Exception):
    pass


type ProjectID = str
type _VersionID = str


@dataclass(frozen=True, kw_only=True)
class _ModStub:
    name: str
    slug: str
    env: Env
    mod_license: str
    source_url: str
    issues_url: str
    versions: Set[_VersionID]


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
        self._link = requote_uri("https://modrinth.com/mod/" + slug)
        self._version = version
        self._original_env = original_env
        self._overridden_env = overridden_env
        self._mod_license = mod_license
        self._source_url = requote_uri(source_url)
        self._issues_url = requote_uri(issues_url)
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
    _LOADERS = frozendict(
        {
            "minecraft": "minecraft",
            "forge": "forge",
            "neoforge": "neoforge",
            "fabric-loader": "fabric",
            "quilt-loader": "quilt",
        },
    )

    def __init__(
        self,
        *,
        name: str,
        version: str,
        game_version: GameVersion,
        dependencies: Mapping[str, str],
        loaders: Set[str],
        unknown_dependencies: Set[str],
        mods: Mapping[ProjectID, Mod],
        missing_mods: Set[str],
        unknown_mods: Mapping[str, str],
        other_files: Mapping[str, str],
    ) -> None:
        super().__init__()
        self._name = name
        self._version = version
        self._game_version = game_version
        self._dependencies = frozendict(dependencies)
        self._loaders = frozenset(loaders)
        self._unknown_dependencies = frozenset(unknown_dependencies)
        self._mods = frozendict(mods)
        self._missing_mods = frozenset(missing_mods)
        self._unknown_mods = frozendict(unknown_mods)
        self._other_files = frozendict(other_files)

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
    def dependencies(self) -> frozendict[str, str]:
        return self._dependencies

    @property
    def loaders(self) -> frozenset[str]:
        return self._loaders

    @property
    def unknown_dependencies(self) -> frozenset[str]:
        return self._unknown_dependencies

    @property
    def mods(self) -> frozendict[ProjectID, Mod]:
        return self._mods

    @property
    def missing_mods(self) -> frozenset[str]:
        return self._missing_mods

    @property
    def unknown_mods(self) -> frozendict[str, str]:
        return self._unknown_mods

    @property
    def other_files(self) -> frozendict[str, str]:
        return self._other_files

    @staticmethod
    def _fetch_file_info(
        hashes: Set[Sha512],
    ) -> tuple[dict[Sha512, dict[str, Any]], frozenset[Sha512]]:
        versions_response = requests.post(
            "https://api.modrinth.com/v2/version_files",
            json={"hashes": sorted(str(h) for h in hashes), "algorithm": "sha512"},
            timeout=10,
        )
        versions_response.raise_for_status()
        versions = versions_response.json()
        versions = {Sha512(k): v for (k, v) in versions.items()}

        known_hashes = frozenset(
            {
                Sha512(file["hashes"]["sha512"])
                for version in versions
                for file in versions[version]["files"]
            },
        )

        return versions, known_hashes

    @staticmethod
    def _fetch_projects(file_info: Mapping[Sha512, Mapping[str, Any]]) -> list[dict[str, Any]]:
        ids = {file_info[mod_hash]["project_id"] for mod_hash in file_info}
        projects_response = requests.get(
            "https://api.modrinth.com/v2/projects",
            {"ids": "[" + ", ".join(f'"{mod_id}"' for mod_id in sorted(ids)) + "]"},
            timeout=10,
        )
        projects_response.raise_for_status()
        return cast("list[dict[str, Any]]", projects_response.json())

    @staticmethod
    def _fetch_versions(
        projects: Sequence[Mapping[str, Any]],
        loaders: Set[str],
    ) -> dict[_VersionID, dict[str, Any]]:
        loaders_param = "[" + ", ".join(f'"{loader}"' for loader in sorted(loaders)) + "]"
        versions = {}
        for i, project in enumerate(sorted(projects, key=lambda p: p["title"].lower())):
            sys.stderr.write(
                f"Fetching versions for mod {i + 1} of {len(projects)}: {project['title']}...\n",
            )
            versions_response = requests.get(
                f"https://api.modrinth.com/v2/project/{project['id']}/version",
                {
                    "loaders": loaders_param,
                },
                timeout=10,
            )
            versions_response.raise_for_status()
            for version in versions_response.json():
                versions[version["id"]] = version
        return cast("dict[_VersionID, dict[str, Any]]", versions)

    @staticmethod
    def _map_loaders(mrpack: Mrpack) -> frozenset[str]:
        out = set()
        for d in mrpack.index.dependencies:
            if d in Modpack._LOADERS:
                out.add(Modpack._LOADERS[d])
        return frozenset(out)

    @staticmethod
    def _load(*mrpacks: Mrpack) -> "tuple[Modpack, ...]":
        all_hashes: set[Sha512] = set()
        loaders: set[str] = set()
        for mrpack in mrpacks:
            all_hashes |= mrpack.index.files.keys()
            loaders |= Modpack._map_loaders(mrpack)

        file_info, known_hashes = Modpack._fetch_file_info(all_hashes)
        projects = Modpack._fetch_projects(file_info)
        versions = Modpack._fetch_versions(projects, loaders)

        mod_stubs = {}
        for project in projects:
            try:
                mod_stubs[project["id"]] = _ModStub(
                    name=project["title"],
                    slug=project["slug"],
                    env=Env(
                        client=Requirement.from_str(project.get("client_side", "")),
                        server=Requirement.from_str(project.get("server_side", "")),
                    ),
                    mod_license="" if "license" not in project else project["license"]["id"],
                    # Sometimes the API returns None for these - force them to be strings
                    source_url=project.get("source_url", "") or "",
                    issues_url=project.get("issues_url", "") or "",
                    versions=frozenset(
                        {
                            version
                            for version in versions
                            if versions[version]["project_id"] == project["id"]
                        },
                    ),
                )
            except Exception as e:  # pragma: no cover
                raise ModpackError(f"Failed to load mod {project['title']}: {e}") from e

        modpacks = []
        for mrpack in mrpacks:
            mods = {}
            missing_mods = set()
            for mod_hash in mrpack.index.files:
                if mod_hash in known_hashes:
                    mod_id = file_info[mod_hash]["project_id"]
                    mod_stub = mod_stubs[mod_id]
                    game_versions = set()
                    for version in mod_stub.versions:
                        if frozenset(versions[version]["loaders"]) & Modpack._map_loaders(mrpack):
                            game_versions.update(versions[version]["game_versions"])
                    mods[mod_id] = Mod(
                        name=mod_stub.name,
                        slug=mod_stub.slug,
                        version=file_info[mod_hash]["version_number"],
                        original_env=mod_stub.env,
                        overridden_env=mrpack.index.files[mod_hash].env or mod_stub.env,
                        mod_license=mod_stub.mod_license,
                        source_url=mod_stub.source_url,
                        issues_url=mod_stub.issues_url,
                        game_versions=GameVersion.from_iterable(game_versions),
                    )
                else:
                    missing_mods.add(str(mrpack.index.files[mod_hash].path.parts[-1]))
            modpacks.append(
                Modpack(
                    name=mrpack.index.name,
                    version=mrpack.index.version,
                    game_version=mrpack.index.game_version,
                    dependencies={
                        k: v for (k, v) in mrpack.index.dependencies.items() if k != "minecraft"
                    },
                    loaders=Modpack._map_loaders(mrpack),
                    unknown_dependencies=mrpack.index.dependencies.keys() - Modpack._LOADERS.keys(),
                    mods=mods,
                    missing_mods=missing_mods,
                    unknown_mods={
                        str(p): f"{binascii.crc32(o.data):08x}"
                        for (p, o) in (
                            mrpack.overrides | mrpack.client_overrides | mrpack.server_overrides
                        ).items()
                        if p.parts[1] == "mods"
                    },
                    other_files={
                        str(p): f"{binascii.crc32(o.data):08x}"
                        for (p, o) in (
                            mrpack.overrides | mrpack.client_overrides | mrpack.server_overrides
                        ).items()
                        if p.parts[1] != "mods"
                    },
                ),
            )

        return tuple(modpacks)

    @staticmethod
    def from_files(*files: str) -> "tuple[Modpack, ...]":
        return Modpack._load(*[Mrpack.load(f) for f in files])

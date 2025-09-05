from collections.abc import Mapping, Set
from dataclasses import dataclass
from pathlib import PurePath

from frozendict import frozendict
from requests.utils import requote_uri

from mrpack.api import Project
from mrpack.index import File, Index
from mrpack.moddb import ModDB
from mrpack.mrpack import Mrpack, Override
from mrpack.types import Env, GameVersion, ProjectID


class ModpackError(Exception):
    pass


@dataclass(frozen=True, kw_only=True)
class FileMissingMod:
    index_entry: File


@dataclass(frozen=True, kw_only=True)
class ProjectMissingMod:
    index_entry: File
    version_number: str


class Mod:
    def __init__(
        self,
        *,
        index_entry: File,
        project: Project,
        version_number: str,
        game_versions: Set[GameVersion],
    ) -> None:
        super().__init__()
        self._index_entry = index_entry
        self._project = project
        self._version_number = version_number
        self._link = requote_uri("https://modrinth.com/mod/" + self._project.slug)
        self._game_versions = frozenset(game_versions)
        self._latest_game_version = max(self._game_versions, default=None)

    @property
    def index_entry(self) -> File:
        return self._index_entry

    @property
    def project(self) -> Project:
        return self._project

    @property
    def version_number(self) -> str:
        return self._version_number

    @property
    def link(self) -> str:
        return self._link

    @property
    def env(self) -> Env:
        return self._index_entry.env or self._project.env

    @property
    def game_versions(self) -> frozenset[GameVersion]:
        return self._game_versions

    @property
    def latest_game_version(self) -> GameVersion | None:
        return self._latest_game_version

    def compatible_with(self, version: GameVersion) -> bool:
        return version in self._game_versions


class Modpack:
    def __init__(
        self,
        *,
        index: Index,
        mods: Mapping[ProjectID, Mod],
        project_missing_mods: Set[ProjectMissingMod],
        file_missing_mods: Set[FileMissingMod],
        overrides: Mapping[PurePath, Override],
    ) -> None:
        super().__init__()
        self._index = index
        self._mods = frozendict(mods)
        self._project_missing_mods = frozenset(project_missing_mods)
        self._file_missing_mods = frozenset(file_missing_mods)
        self._overrides = frozendict(overrides)

    @property
    def index(self) -> Index:
        return self._index

    @property
    def mods(self) -> frozendict[ProjectID, Mod]:
        return self._mods

    @property
    def project_missing_mods(self) -> frozenset[ProjectMissingMod]:
        return self._project_missing_mods

    @property
    def file_missing_mods(self) -> frozenset[FileMissingMod]:
        return self._file_missing_mods

    @property
    def overrides(self) -> frozendict[PurePath, Override]:
        return self._overrides

    @staticmethod
    def load(m: Mrpack, db: ModDB) -> "Modpack":
        mods = {}
        project_missing_mods = set()
        file_missing_mods = set()

        for h, index_entry in m.index.files.items():
            file = db.file(h)
            if file is None:
                file_missing_mods.add(FileMissingMod(index_entry=index_entry))
                continue

            project_id = file.project_id
            project = db.project(project_id)
            if project is None:
                project_missing_mods.add(
                    ProjectMissingMod(
                        index_entry=index_entry,
                        version_number=file.version_number,
                    ),
                )
                continue

            if project_id in mods:
                raise ValueError(f"Duplicate project ID '{project_id}")  # pragma: no cover

            game_versions: set[str] = set()
            for version_id in db.project_versions(project_id):
                version = db.version(version_id)
                if version and version.loaders & m.index.dependencies.loaders:
                    game_versions.update(version.game_versions)

            mods[project_id] = Mod(
                index_entry=index_entry,
                project=project,
                version_number=file.version_number,
                game_versions=GameVersion.load_multiple(game_versions),
            )

        return Modpack(
            index=m.index,
            mods=mods,
            project_missing_mods=project_missing_mods,
            file_missing_mods=file_missing_mods,
            overrides=m.overrides,
        )

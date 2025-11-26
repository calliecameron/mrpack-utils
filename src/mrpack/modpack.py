from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from requests.utils import requote_uri

from mrpack.types import Env, GameVersion, Map, ProjectID, Sha512

if TYPE_CHECKING:
    from collections.abc import Collection, Set

    from mrpack.api import Project
    from mrpack.index import File, Index
    from mrpack.moddb import ModDB
    from mrpack.mrpack import Mrpack, OverrideMap


class ModpackError(Exception):
    pass


@dataclass(frozen=True, kw_only=True)
class FileMissingMod:
    index_entry: File


class FileMissingModMap(Map[Sha512, FileMissingMod]):
    @override
    @classmethod
    def _key(cls, item: FileMissingMod) -> Sha512:
        return item.index_entry.hashes.sha512


@dataclass(frozen=True, kw_only=True)
class ProjectMissingMod:
    index_entry: File
    version_number: str


class ProjectMissingModMap(Map[Sha512, ProjectMissingMod]):
    @override
    @classmethod
    def _key(cls, item: ProjectMissingMod) -> Sha512:
        return item.index_entry.hashes.sha512


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


class ModMap(Map[ProjectID, Mod]):
    @override
    @classmethod
    def _key(cls, item: Mod) -> ProjectID:
        return item.project.project_id


class Modpack:
    def __init__(
        self,
        *,
        index: Index,
        mods: Collection[Mod],
        project_missing_mods: Collection[ProjectMissingMod],
        file_missing_mods: Collection[FileMissingMod],
        overrides: OverrideMap,
    ) -> None:
        super().__init__()
        self._index = index
        self._mods = ModMap(mods)
        self._project_missing_mods = ProjectMissingModMap(project_missing_mods)
        self._file_missing_mods = FileMissingModMap(file_missing_mods)
        self._overrides = overrides

    @property
    def index(self) -> Index:
        return self._index

    @property
    def mods(self) -> ModMap:
        return self._mods

    @property
    def project_missing_mods(self) -> ProjectMissingModMap:
        return self._project_missing_mods

    @property
    def file_missing_mods(self) -> FileMissingModMap:
        return self._file_missing_mods

    @property
    def overrides(self) -> OverrideMap:
        return self._overrides

    @staticmethod
    def load(m: Mrpack, db: ModDB) -> Modpack:
        mods = []
        project_missing_mods = []
        file_missing_mods = []

        for h, index_entry in m.index.files.items():
            file = db.file(h)
            if file is None:
                file_missing_mods.append(FileMissingMod(index_entry=index_entry))
                continue

            project_id = file.project_id
            project = db.project(project_id)
            if project is None:
                project_missing_mods.append(
                    ProjectMissingMod(
                        index_entry=index_entry,
                        version_number=file.version_number,
                    ),
                )
                continue

            game_versions: set[str] = set()
            for version_id in db.project_versions(project_id):
                version = db.version(version_id)
                if version and version.loaders & m.index.dependencies.loaders:
                    game_versions.update(version.game_versions)

            mods.append(
                Mod(
                    index_entry=index_entry,
                    project=project,
                    version_number=file.version_number,
                    game_versions=GameVersion.load_multiple(game_versions),
                ),
            )

        return Modpack(
            index=m.index,
            mods=mods,
            project_missing_mods=project_missing_mods,
            file_missing_mods=file_missing_mods,
            overrides=m.overrides,
        )

import binascii
from collections.abc import Mapping, Set
from dataclasses import dataclass

from frozendict import frozendict
from requests.utils import requote_uri

from mrpack_utils.moddb import ModDB
from mrpack_utils.mrpack import Mrpack
from mrpack_utils.types import ID, Env, GameVersion


class ModpackError(Exception):
    pass


@dataclass(frozen=True, kw_only=True)
class _ModStub:
    name: str
    slug: str
    env: Env
    mod_license: str
    source_url: str
    issues_url: str
    versions: Set[ID]


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
    def __init__(
        self,
        *,
        name: str,
        version: str,
        game_version: GameVersion,
        dependencies: Mapping[str, str],
        loaders: Set[str],
        unknown_dependencies: Set[str],
        mods: Mapping[ID, Mod],
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
    def mods(self) -> frozendict[ID, Mod]:
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
    def load(mrpack: Mrpack, db: ModDB) -> "Modpack":
        mod_stubs = {}
        for project in db.projects.values():
            try:
                mod_stubs[project.project_id] = _ModStub(
                    name=project.title,
                    slug=project.slug,
                    env=project.env,
                    mod_license=project.project_license,
                    source_url=project.source_url,
                    issues_url=project.issues_url,
                    versions=frozenset(
                        {
                            version
                            for version in db.versions
                            if db.versions[version].project_id == project.project_id
                        },
                    ),
                )
            except Exception as e:  # pragma: no cover
                raise ModpackError(f"Failed to load mod {project.title}: {e}") from e

        mods = {}
        missing_mods = set()
        for mod_hash in mrpack.index.files:
            if mod_hash in db.files:
                file = db.files[mod_hash]
                mod_id = file.project_id
                mod_stub = mod_stubs[mod_id]
                game_versions: set[str] = set()
                for version in mod_stub.versions:
                    if db.versions[version].loaders & mrpack.index.loaders:
                        game_versions.update(db.versions[version].game_versions)
                mods[mod_id] = Mod(
                    name=mod_stub.name,
                    slug=mod_stub.slug,
                    version=file.version_number,
                    original_env=mod_stub.env,
                    overridden_env=mrpack.index.files[mod_hash].env or mod_stub.env,
                    mod_license=mod_stub.mod_license,
                    source_url=mod_stub.source_url,
                    issues_url=mod_stub.issues_url,
                    game_versions=GameVersion.from_iterable(game_versions),
                )
            else:
                missing_mods.add(str(mrpack.index.files[mod_hash].path.parts[-1]))

        return Modpack(
            name=mrpack.index.name,
            version=mrpack.index.version,
            game_version=mrpack.index.game_version,
            dependencies={k: v for (k, v) in mrpack.index.dependencies.items() if k != "minecraft"},
            loaders=mrpack.index.loaders,
            unknown_dependencies=mrpack.index.unknown_dependencies,
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
        )

    @staticmethod
    def from_files(*files: str) -> "tuple[Modpack, ...]":
        mrpacks = [Mrpack.load(f) for f in files]
        db = ModDB.load(mrpacks, True)
        return tuple(Modpack.load(mrpack, db) for mrpack in mrpacks)

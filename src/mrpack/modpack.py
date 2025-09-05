import binascii
from collections.abc import Mapping, Set

from frozendict import frozendict
from requests.utils import requote_uri

from mrpack.moddb import ModDB
from mrpack.mrpack import Mrpack
from mrpack.types import Env, GameVersion, ProjectID


class ModpackError(Exception):
    pass


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
    def load(mrp: Mrpack, db: ModDB) -> "Modpack":
        mods = {}
        missing_mods = set()
        for mod_hash in mrp.index.files:
            if mod_hash in db.all_files:
                file = db.all_files[mod_hash]
                mod_id = file.project_id
                project = db.all_projects[mod_id]
                game_versions: set[str] = set()
                for version in db.project_versions(file.project_id):
                    if (
                        version in db.all_versions
                        and db.all_versions[version].loaders & mrp.index.dependencies.loaders
                    ):
                        game_versions.update(db.all_versions[version].game_versions)
                mods[mod_id] = Mod(
                    name=project.title,
                    slug=project.slug,
                    version=file.version_number,
                    original_env=project.env,
                    overridden_env=mrp.index.files[mod_hash].env or project.env,
                    mod_license=project.project_license,
                    source_url=project.source_url,
                    issues_url=project.issues_url,
                    game_versions=GameVersion.load_multiple(game_versions),
                )
            else:
                missing_mods.add(str(mrp.index.files[mod_hash].path.parts[-1]))

        return Modpack(
            name=mrp.index.name,
            version=mrp.index.version,
            game_version=mrp.index.dependencies.game_version,
            dependencies=mrp.index.dependencies.others,
            loaders=mrp.index.dependencies.loaders,
            unknown_dependencies=mrp.index.dependencies.unknown_dependencies,
            mods=mods,
            missing_mods=missing_mods,
            unknown_mods={
                str(p): f"{binascii.crc32(o.data):08x}"
                for (p, o) in mrp.overrides.items()
                if p.parts[1] == "mods"
            },
            other_files={
                str(p): f"{binascii.crc32(o.data):08x}"
                for (p, o) in mrp.overrides.items()
                if p.parts[1] != "mods"
            },
        )

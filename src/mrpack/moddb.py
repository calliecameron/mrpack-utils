from collections import defaultdict
from typing import TYPE_CHECKING

from frozendict import frozendict

from mrpack.api import (
    File,
    Project,
    Version,
    get_file_details,
    get_projects,
    get_versions,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from mrpack.mrpack import Mrpack
    from mrpack.types import ProjectID, Sha512, VersionID


class ModDB:
    def __init__(
        self,
        *,
        files: Mapping[Sha512, File],
        projects: Mapping[ProjectID, Project],
        versions: Mapping[VersionID, Version],
    ) -> None:
        super().__init__()
        self._files = frozendict(files)
        self._projects = frozendict(projects)
        self._versions = frozendict(versions)

        project_versions = defaultdict(set)
        for version in self._versions.values():
            project_versions[version.project_id].add(version.version_id)
        self._project_versions = frozendict(
            {k: frozenset(v) for (k, v) in project_versions.items()},
        )

    @property
    def all_files(self) -> frozendict[Sha512, File]:
        return self._files

    def file(self, sha512: Sha512) -> File | None:
        return self._files.get(sha512)

    @property
    def all_projects(self) -> frozendict[ProjectID, Project]:
        return self._projects

    def project(self, project_id: ProjectID) -> Project | None:
        return self._projects.get(project_id)

    @property
    def all_versions(self) -> frozendict[VersionID, Version]:
        return self._versions

    def version(self, version_id: VersionID) -> Version | None:
        return self._versions.get(version_id)

    @property
    def all_project_versions(self) -> frozendict[ProjectID, frozenset[VersionID]]:
        return self._project_versions

    def project_versions(self, project_id: ProjectID) -> frozenset[VersionID]:
        return self._project_versions.get(project_id, frozenset())

    @staticmethod
    def load(mrpacks: Collection[Mrpack], *, fetch_versions: bool) -> ModDB:
        hashes: set[Sha512] = set()
        loaders: set[str] = set()
        for mrp in mrpacks:
            hashes |= mrp.index.files.keys()
            loaders |= mrp.index.dependencies.loaders

        files = get_file_details(hashes)
        projects = get_projects({f.project_id for f in files.values()})

        versions: frozendict[VersionID, Version] = frozendict()
        if fetch_versions:
            versions = get_versions(projects.values(), loaders)

        return ModDB(
            files=files,
            projects=projects,
            versions=versions,
        )

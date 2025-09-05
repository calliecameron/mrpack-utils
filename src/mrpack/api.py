import sys
from collections.abc import Collection, Set
from dataclasses import dataclass
from typing import override

import jsonschema
import requests
from frozendict import frozendict
from requests.utils import requote_uri

from mrpack.types import Env, ProjectID, Requirement, Sha512, VersionID, make_json_schema


@dataclass(frozen=True, kw_only=True)
class File:
    sha512: Sha512
    project_id: ProjectID
    version_number: str


_GET_FILE_DETAILS_SCHEMA = make_json_schema(
    {
        "type": "object",
        "patternProperties": {
            ".*": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                    },
                    "version_number": {
                        "type": "string",
                    },
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "hashes": {
                                    "type": "object",
                                    "properties": {
                                        "sha512": {
                                            "type": "string",
                                        },
                                    },
                                    "required": [
                                        "sha512",
                                    ],
                                    "additionalProperties": True,
                                },
                            },
                            "required": [
                                "hashes",
                            ],
                            "additionalProperties": True,
                        },
                        "uniqueItems": True,
                    },
                },
                "required": [
                    "project_id",
                    "files",
                ],
                "additionalProperties": True,
            },
        },
        "additionalProperties": True,
    },
)


def get_file_details(hashes: Set[Sha512]) -> frozendict[Sha512, File]:
    if not hashes:
        return frozendict()

    response = requests.post(
        "https://api.modrinth.com/v2/version_files",
        json={
            "hashes": sorted(str(h) for h in hashes),
            "algorithm": "sha512",
        },
        timeout=10,
    )
    response.raise_for_status()
    j = response.json()
    jsonschema.validate(j, _GET_FILE_DETAILS_SCHEMA)

    out = {}
    for version in j.values():
        project_id = ProjectID(version["project_id"])
        version_number = version.get("version_number", "")
        for file in version["files"]:
            h = Sha512(file["hashes"]["sha512"])
            if h in out:
                raise ValueError(f"Duplicate hash in get_version_files '{h}'")
            out[h] = File(
                sha512=h,
                project_id=project_id,
                version_number=version_number,
            )
    return frozendict(out)


class Project:
    def __init__(
        self,
        *,
        project_id: ProjectID,
        slug: str,
        title: str,
        env: Env,
        project_license: str,
        source_url: str,
        issues_url: str,
    ) -> None:
        super().__init__()
        self._project_id = project_id
        self._slug = slug
        self._title = title
        self._env = env
        self._project_license = project_license
        self._source_url = requote_uri(source_url)
        self._issues_url = requote_uri(issues_url)

    @property
    def project_id(self) -> ProjectID:
        return self._project_id

    @property
    def slug(self) -> str:
        return self._slug

    @property
    def title(self) -> str:
        return self._title

    @property
    def env(self) -> Env:
        return self._env

    @property
    def project_license(self) -> str:
        return self._project_license

    @property
    def source_url(self) -> str:
        return self._source_url

    @property
    def issues_url(self) -> str:
        return self._issues_url

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Project):
            raise NotImplementedError
        return (
            self._project_id == other._project_id
            and self._slug == other._slug
            and self._title == other._title
            and self._env == other._env
            and self._project_license == other._project_license
            and self._source_url == other._source_url
            and self._issues_url == other._issues_url
        )

    @override
    def __hash__(self) -> int:
        return hash(
            (
                self._project_id,
                self._slug,
                self._title,
                self._env,
                self._project_license,
                self._source_url,
                self._issues_url,
            ),
        )


_GET_PROJECTS_SCHEMA = make_json_schema(
    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                },
                "slug": {
                    "type": "string",
                },
                "title": {
                    "type": "string",
                },
                "client_side": {
                    "enum": sorted(m.lower() for m in Requirement.__members__),
                },
                "server_side": {
                    "enum": sorted(m.lower() for m in Requirement.__members__),
                },
                "license": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "id",
                    ],
                    "additionalProperties": True,
                },
                "source_url": {
                    "type": ["string", "null"],
                },
                "issues_url": {
                    "type": ["string", "null"],
                },
            },
            "required": [
                "id",
                "slug",
                "title",
            ],
            "additionalProperties": True,
        },
        "uniqueItems": True,
    },
)


def get_projects(ids: Set[ProjectID]) -> frozendict[ProjectID, Project]:
    if not ids:
        return frozendict()

    response = requests.get(
        "https://api.modrinth.com/v2/projects",
        {
            "ids": "[" + ", ".join(sorted(f'"{project_id}"' for project_id in ids)) + "]",
        },
        timeout=10,
    )
    response.raise_for_status()
    j = response.json()
    jsonschema.validate(j, _GET_PROJECTS_SCHEMA)

    out = {}
    for project in j:
        project_id = ProjectID(project["id"])
        if project_id in out:
            raise ValueError(f"Duplicate project ID in get_projects '{project_id}'")
        out[project_id] = Project(
            project_id=project_id,
            slug=project["slug"],
            title=project["title"],
            env=Env(
                client=Requirement.from_str(project.get("client_side", "")),
                server=Requirement.from_str(project.get("server_side", "")),
            ),
            project_license="" if "license" not in project else project["license"]["id"],
            # Sometimes the API returns None for these - force them to be strings
            source_url=project.get("source_url", "") or "",
            issues_url=project.get("issues_url", "") or "",
        )

    return frozendict(out)


@dataclass(frozen=True, kw_only=True)
class Version:
    version_id: VersionID
    project_id: ProjectID
    loaders: Set[str]
    game_versions: Set[str]


_GET_VERSIONS_SCHEMA = make_json_schema(
    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                },
                "project_id": {
                    "type": "string",
                },
                "loaders": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "uniqueItems": True,
                },
                "game_versions": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "uniqueItems": True,
                },
            },
            "required": [
                "id",
                "project_id",
            ],
            "additionalProperties": True,
        },
        "uniqueItems": True,
    },
)


def get_versions(
    projects: Collection[Project],
    loaders: Set[str],
) -> frozendict[VersionID, Version]:
    if not projects or not loaders:
        return frozendict()

    loaders_param = "[" + ", ".join(f'"{loader}"' for loader in sorted(loaders)) + "]"
    out = {}

    for i, project in enumerate(sorted(projects, key=lambda p: p.title.lower())):
        sys.stderr.write(
            f"Fetching versions for project {i + 1} of {len(projects)}: {project.title}...\n",
        )
        response = requests.get(
            f"https://api.modrinth.com/v2/project/{project.project_id}/version",
            {
                "loaders": loaders_param,
            },
            timeout=10,
        )
        response.raise_for_status()
        j = response.json()
        jsonschema.validate(j, _GET_VERSIONS_SCHEMA)

        for version in j:
            version_id = VersionID(version["id"])
            if version_id in out:
                raise ValueError(f"Duplicate version ID in get_versions '{version_id}'")
            out[version_id] = Version(
                version_id=version_id,
                project_id=ProjectID(version["project_id"]),
                loaders=frozenset(version.get("loaders", [])),
                game_versions=frozenset(version.get("game_versions", [])),
            )

    return frozendict(out)

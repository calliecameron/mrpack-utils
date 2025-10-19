import jsonschema
import pytest
import requests_mock
from frozendict import frozendict

from mrpack.api import (
    File,
    Project,
    Version,
    get_file_details,
    get_projects,
    get_versions,
)
from mrpack.types import Env, ProjectID, Requirement, Sha512, VersionID
from tests import testdata

# ruff: noqa: S101


class TestGetFileDetails:
    def test_valid(self) -> None:
        with requests_mock.Mocker() as m:
            assert get_file_details(set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json=testdata.FILE_A0 | testdata.FILE_B0,
            )

            assert get_file_details(
                {
                    Sha512(
                        "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    Sha512(
                        "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                },
            ) == frozendict(
                {
                    Sha512(
                        "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): File(
                        sha512=Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ProjectID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): File(
                        sha512=Sha512(
                            "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ProjectID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): File(
                        sha512=Sha512(
                            "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ProjectID("b0000000"),
                        version_number="4.5.6",
                    ),
                },
            )

        # Returning nothing is valid
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={},
            )

            assert (
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )
                == frozendict()
            )

        # Returning an empty file list is valid
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "version_number": "1.2.3",
                        "files": [],
                        "foo": "bar",
                    },
                },
            )

            assert (
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )
                == frozendict()
            )

    def test_invalid(self) -> None:
        # No project ID
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
            with pytest.raises(jsonschema.ValidationError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )

        # No files
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                    },
                },
            )
            with pytest.raises(jsonschema.ValidationError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )

        # No hashes
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "files": [
                            {},
                        ],
                    },
                },
            )
            with pytest.raises(jsonschema.ValidationError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )

        # No sha512
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "files": [
                            {
                                "hashes": {},
                            },
                        ],
                    },
                },
            )
            with pytest.raises(jsonschema.ValidationError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )

        # Duplicate files
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
            with pytest.raises(jsonschema.ValidationError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )

        # Duplicate hashes
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "b0000000",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
            with pytest.raises(ValueError):
                get_file_details(
                    {
                        Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                    },
                )


class TestProject:
    def test_project(self) -> None:
        e = Env(
            client=Requirement.OPTIONAL,
            server=Requirement.REQUIRED,
        )
        p1 = Project(
            project_id=ProjectID("a0000000"),
            slug="a",
            title="A",
            env=e,
            project_license="MIT",
            source_url="S 1",
            issues_url="I 1",
        )

        assert p1.project_id == ProjectID("a0000000")
        assert p1.slug == "a"
        assert p1.title == "A"
        assert p1.env == e
        assert p1.project_license == "MIT"
        assert p1.source_url == "S%201"
        assert p1.issues_url == "I%201"

        p2 = Project(
            project_id=ProjectID("b0000000"),
            slug="b",
            title="B",
            env=e,
            project_license="MIT",
            source_url="S",
            issues_url="I",
        )

        assert p2.project_id == ProjectID("b0000000")
        assert p2.slug == "b"
        assert p2.title == "B"
        assert p2.env == e
        assert p2.project_license == "MIT"
        assert p2.source_url == "S"
        assert p2.issues_url == "I"

        assert p1 == p1  # noqa: PLR0124
        assert p1 != p2
        assert p1 != "foo"


class TestGetProjects:
    def test_valid(self) -> None:
        with requests_mock.Mocker() as m:
            assert get_projects(set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[
                    testdata.PROJECT_A,
                    testdata.PROJECT_B,
                ],
            )
            assert get_projects(
                {ProjectID("a0000000"), ProjectID("b0000000")},
            ) == frozendict(
                {
                    ProjectID("a0000000"): Project(
                        project_id=ProjectID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env(
                            client=Requirement.OPTIONAL,
                            server=Requirement.REQUIRED,
                        ),
                        project_license="MIT",
                        source_url="S%201",
                        issues_url="I%201",
                    ),
                    ProjectID("b0000000"): Project(
                        project_id=ProjectID("b0000000"),
                        slug="b",
                        title="B",
                        env=Env.unknown(),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                },
            )

        # Returning nothing is valid
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[],
            )
            assert (
                get_projects({ProjectID("a0000000"), ProjectID("b0000000")})
                == frozendict()
            )

        # Returning 'None' for source and issue URLs is valid
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                        "source_url": None,
                        "issues_url": None,
                    },
                ],
            )
            assert get_projects({ProjectID("a0000000")}) == frozendict(
                {
                    ProjectID("a0000000"): Project(
                        project_id=ProjectID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env.unknown(),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                },
            )

    def test_invalid(self) -> None:
        # No ID
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "title": "A",
                        "slug": "a",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_projects({ProjectID("a0000000")})

        # No title
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "slug": "a",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_projects({ProjectID("a0000000")})

        # No slug
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_projects({ProjectID("a0000000")})

        # No license ID
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                        "license": {},
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_projects({ProjectID("a0000000")})

        # Duplicate items
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                    },
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_projects({ProjectID("a0000000")})

        # Duplicate IDs
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                    },
                    {
                        "id": "a0000000",
                        "title": "B",
                        "slug": "b",
                    },
                ],
            )
            with pytest.raises(ValueError):
                get_projects({ProjectID("a0000000")})


class TestGetVersions:
    def test_valid(self) -> None:
        with requests_mock.Mocker() as m:
            assert get_versions(set(), set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    testdata.VERSION_A0,
                    testdata.VERSION_A1,
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    testdata.VERSION_B0,
                    testdata.VERSION_B1,
                ],
            )

            assert get_versions(
                {
                    Project(
                        project_id=ProjectID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env.unknown(),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                    Project(
                        project_id=ProjectID("b0000000"),
                        slug="b",
                        title="B",
                        env=Env.unknown(),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                },
                {
                    "minecraft",
                    "fabric",
                },
            ) == frozendict(
                {
                    VersionID("A0000000"): Version(
                        version_id=VersionID("A0000000"),
                        project_id=ProjectID("a0000000"),
                        loaders={"fabric"},
                        game_versions={"1.19.2"},
                    ),
                    VersionID("A1000000"): Version(
                        version_id=VersionID("A1000000"),
                        project_id=ProjectID("a0000000"),
                        loaders={"fabric", "minecraft"},
                        game_versions={"1.20"},
                    ),
                    VersionID("B0000000"): Version(
                        version_id=VersionID("B0000000"),
                        project_id=ProjectID("b0000000"),
                        loaders={"minecraft"},
                        game_versions={"1.19.4"},
                    ),
                    VersionID("B1000000"): Version(
                        version_id=VersionID("B1000000"),
                        project_id=ProjectID("b0000000"),
                        loaders=set({"forge"}),
                        game_versions=set({"1.20"}),
                    ),
                },
            )

        # Returning nothing is valid
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[],
            )
            assert (
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )
                == frozendict()
            )

    def test_invalid(self) -> None:
        # No ID
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "project_id": "a0000000",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

        # No project ID
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

        # Duplicate loaders
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                        "loaders": [
                            "minecraft",
                            "minecraft",
                        ],
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

        # Duplicate game versions
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                        "game_versions": [
                            "1.20",
                            "1.20",
                        ],
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

        # Duplicate items
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                    },
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                    },
                ],
            )
            with pytest.raises(jsonschema.ValidationError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

        # Duplicate IDs
        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                    },
                    {
                        "id": "A0000000",
                        "project_id": "b0000000",
                    },
                ],
            )
            with pytest.raises(ValueError):
                get_versions(
                    {
                        Project(
                            project_id=ProjectID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env.unknown(),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

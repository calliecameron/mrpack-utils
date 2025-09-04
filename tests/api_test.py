import jsonschema
import pytest
import requests_mock
from frozendict import frozendict

from mrpack_utils.api import File, Project, Version, get_file_details, get_projects, get_versions
from mrpack_utils.types import ID, Env, Requirement, Sha512

# ruff: noqa: PT011,S101


class TestGetFileDetails:
    def test_valid(self) -> None:
        assert get_file_details(set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "a0000000",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                    "foo": "bar",
                                },
                                "foo": "bar",
                            },
                            {
                                "hashes": {
                                    "sha512": "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                        "foo": "bar",
                    },
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "b0000000",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                        "bar": "baz",
                    },
                },
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
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): File(
                        sha512=Sha512(
                            "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): File(
                        sha512=Sha512(
                            "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("b0000000"),
                        version_number="4.5.6",
                    ),
                },
            )

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


class TestGetProjects:
    def test_valid(self) -> None:
        assert get_projects(set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "a0000000",
                        "title": "A",
                        "slug": "a",
                    },
                    {
                        "id": "b0000000",
                        "title": "B",
                        "slug": "b",
                        "client_side": "required",
                        "server_side": "optional",
                        "license": {
                            "id": "MIT",
                            "foo": "bar",
                        },
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                        "foo": "bar",
                    },
                ],
            )
            assert get_projects({ID("a0000000"), ID("b0000000")}) == frozendict(
                {
                    ID("a0000000"): Project(
                        project_id=ID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env(
                            client=Requirement.UNKNOWN,
                            server=Requirement.UNKNOWN,
                        ),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                    ID("b0000000"): Project(
                        project_id=ID("b0000000"),
                        slug="b",
                        title="B",
                        env=Env(
                            client=Requirement.REQUIRED,
                            server=Requirement.OPTIONAL,
                        ),
                        project_license="MIT",
                        source_url="example.com",
                        issues_url="example2.com",
                    ),
                },
            )

        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[],
            )
            assert get_projects({ID("a0000000"), ID("b0000000")}) == frozendict()

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
            assert get_projects({ID("a0000000")}) == frozendict(
                {
                    ID("a0000000"): Project(
                        project_id=ID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env(
                            client=Requirement.UNKNOWN,
                            server=Requirement.UNKNOWN,
                        ),
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
                get_projects({ID("a0000000")})

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
                get_projects({ID("a0000000")})

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
                get_projects({ID("a0000000")})

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
                get_projects({ID("a0000000")})

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
                get_projects({ID("a0000000")})

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
                get_projects({ID("a0000000")})


class TestGetVersions:
    def test_valid(self) -> None:
        assert get_versions(set(), set()) == frozendict()

        with requests_mock.Mocker() as m:
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                        "loaders": ["fabric"],
                        "game_versions": ["1.19.2"],
                        "foo": "bar",
                    },
                    {
                        "id": "A1000000",
                        "project_id": "a0000000",
                        "loaders": ["fabric", "minecraft"],
                        "game_versions": ["1.20"],
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "B0000000",
                        "project_id": "b0000000",
                        "loaders": ["minecraft"],
                        "game_versions": ["1.19.4"],
                    },
                    {
                        "id": "B1000000",
                        "project_id": "b0000000",
                    },
                ],
            )

            assert get_versions(
                {
                    Project(
                        project_id=ID("a0000000"),
                        slug="a",
                        title="A",
                        env=Env(
                            client=Requirement.UNKNOWN,
                            server=Requirement.UNKNOWN,
                        ),
                        project_license="",
                        source_url="",
                        issues_url="",
                    ),
                    Project(
                        project_id=ID("b0000000"),
                        slug="b",
                        title="B",
                        env=Env(
                            client=Requirement.UNKNOWN,
                            server=Requirement.UNKNOWN,
                        ),
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
                    ID("A0000000"): Version(
                        version_id=ID("A0000000"),
                        project_id=ID("a0000000"),
                        loaders={"fabric"},
                        game_versions={"1.19.2"},
                    ),
                    ID("A1000000"): Version(
                        version_id=ID("A1000000"),
                        project_id=ID("a0000000"),
                        loaders={"fabric", "minecraft"},
                        game_versions={"1.20"},
                    ),
                    ID("B0000000"): Version(
                        version_id=ID("B0000000"),
                        project_id=ID("b0000000"),
                        loaders={"minecraft"},
                        game_versions={"1.19.4"},
                    ),
                    ID("B1000000"): Version(
                        version_id=ID("B1000000"),
                        project_id=ID("b0000000"),
                        loaders=set(),
                        game_versions=set(),
                    ),
                },
            )

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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
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
                            project_id=ID("a0000000"),
                            slug="a",
                            title="A",
                            env=Env(
                                client=Requirement.UNKNOWN,
                                server=Requirement.UNKNOWN,
                            ),
                            project_license="",
                            source_url="",
                            issues_url="",
                        ),
                    },
                    {
                        "minecraft",
                    },
                )

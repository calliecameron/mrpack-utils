import requests_mock
from frozendict import frozendict

from mrpack_utils import api
from mrpack_utils.moddb import ModDB
from mrpack_utils.mrpack import File, Hashes, Index, Mrpack
from mrpack_utils.types import ID, Env, Requirement, Sha1, Sha512

# ruff: noqa: S101


class TestModDB:
    def test_load(self) -> None:
        mrpack1 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files={
                    File(
                        path="mods/a.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/b.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/c.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                },
                dependencies={
                    "minecraft": "1.19.4",
                    "foo": "1",
                    "fabric-loader": "2",
                },
            ),
            overrides=set(),
            client_overrides=set(),
            server_overrides=set(),
        )
        mrpack2 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="2",
                summary="",
                files={
                    File(
                        path="mods/a.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/b.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/c.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                },
                dependencies={
                    "minecraft": "1.19.4",
                    "foo": "2",
                },
            ),
            overrides=set(),
            client_overrides=set(),
            server_overrides=set(),
        )

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
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
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
                    },
                    "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "b0000000",
                        "version_number": "4.5.7",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
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
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "A0000000",
                        "project_id": "a0000000",
                        "loaders": ["fabric"],
                        "game_versions": ["1.19.2"],
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
                        "loaders": ["forge"],
                        "game_versions": ["1.20"],
                    },
                ],
            )
            db = ModDB.load([mrpack1, mrpack2], True)

            assert db.all_files == frozendict(
                {
                    Sha512(
                        "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("b0000000"),
                        version_number="4.5.6",
                    ),
                    Sha512(
                        "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("b0000000"),
                        version_number="4.5.7",
                    ),
                },
            )
            assert db.file(
                Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
            ) == api.File(
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ID("a0000000"),
                version_number="1.2.3",
            )
            assert (
                db.file(
                    Sha512(
                        "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                )
                is None
            )

            assert db.all_projects == frozendict(
                {
                    ID("a0000000"): api.Project(
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
                    ID("b0000000"): api.Project(
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
            )
            assert db.project(ID("a0000000")) == api.Project(
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
            )
            assert db.project(ID("c0000000")) is None

            assert db.all_versions == frozendict(
                {
                    ID("A0000000"): api.Version(
                        version_id=ID("A0000000"),
                        project_id=ID("a0000000"),
                        loaders={"fabric"},
                        game_versions={"1.19.2"},
                    ),
                    ID("A1000000"): api.Version(
                        version_id=ID("A1000000"),
                        project_id=ID("a0000000"),
                        loaders={"fabric", "minecraft"},
                        game_versions={"1.20"},
                    ),
                    ID("B0000000"): api.Version(
                        version_id=ID("B0000000"),
                        project_id=ID("b0000000"),
                        loaders={"minecraft"},
                        game_versions={"1.19.4"},
                    ),
                    ID("B1000000"): api.Version(
                        version_id=ID("B1000000"),
                        project_id=ID("b0000000"),
                        loaders={"forge"},
                        game_versions={"1.20"},
                    ),
                },
            )
            assert db.version(ID("A0000000")) == api.Version(
                version_id=ID("A0000000"),
                project_id=ID("a0000000"),
                loaders={"fabric"},
                game_versions={"1.19.2"},
            )
            assert db.version(ID("C0000000")) is None

            assert db.all_project_versions == frozendict(
                {
                    ID("a0000000"): frozenset(
                        {
                            ID("A0000000"),
                            ID("A1000000"),
                        },
                    ),
                    ID("b0000000"): frozenset(
                        {
                            ID("B0000000"),
                            ID("B1000000"),
                        },
                    ),
                },
            )
            assert db.project_versions(ID("a0000000")) == frozenset(
                {
                    ID("A0000000"),
                    ID("A1000000"),
                },
            )
            assert db.project_versions(ID("c0000000")) == frozenset()

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
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
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
                    },
                    "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "b0000000",
                        "version_number": "4.5.7",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
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
                    },
                ],
            )
            db = ModDB.load([mrpack1, mrpack2], False)

            assert db.all_files == frozendict(
                {
                    Sha512(
                        "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("a0000000"),
                        version_number="1.2.3",
                    ),
                    Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("b0000000"),
                        version_number="4.5.6",
                    ),
                    Sha512(
                        "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ): api.File(
                        sha512=Sha512(
                            "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                        ),
                        project_id=ID("b0000000"),
                        version_number="4.5.7",
                    ),
                },
            )
            assert db.file(
                Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
            ) == api.File(
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ID("a0000000"),
                version_number="1.2.3",
            )
            assert (
                db.file(
                    Sha512(
                        "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                )
                is None
            )

            assert db.all_projects == frozendict(
                {
                    ID("a0000000"): api.Project(
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
                    ID("b0000000"): api.Project(
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
            )
            assert db.project(ID("a0000000")) == api.Project(
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
            )
            assert db.project(ID("c0000000")) is None

            assert db.all_versions == frozendict()
            assert db.version(ID("A0000000")) is None

            assert db.all_project_versions == frozendict()
            assert db.project_versions(ID("A0000000")) == frozenset()

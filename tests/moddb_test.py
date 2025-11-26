import requests_mock
from frozendict import frozendict

from mrpack import api
from mrpack.index import Dependencies, File, Hashes, Index
from mrpack.moddb import ModDB
from mrpack.mrpack import Mrpack
from mrpack.types import (
    Env,
    GameVersion,
    ProjectID,
    Requirement,
    Sha1,
    Sha512,
    VersionID,
)
from tests import testdata

# ruff: noqa: S101


class TestModDB:
    def test_load(self) -> None:
        mrpack1 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files=[
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
                ],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={
                        "foo": "1",
                        "fabric-loader": "2",
                    },
                ),
            ),
            overrides=[],
        )
        mrpack2 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="2",
                summary="",
                files=[
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
                ],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={
                        "foo": "2",
                    },
                ),
            ),
            overrides=[],
        )

        # Fetching versions
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json=testdata.FILE_A0 | testdata.FILE_B0 | testdata.FILE_B1,
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[
                    testdata.PROJECT_A,
                    testdata.PROJECT_B,
                ],
            )
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
            db = ModDB.load([mrpack1, mrpack2], fetch_versions=True)

        assert db.all_files == {
            Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("a0000000"),
                version_number="1.2.3",
            ),
            Sha512(
                "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("a0000000"),
                version_number="1.2.3",
            ),
            Sha512(
                "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("b0000000"),
                version_number="4.5.6",
            ),
            Sha512(
                "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("b0000000"),
                version_number="4.5.7",
            ),
        }
        assert db.file(
            Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
        ) == api.File(
            sha512=Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
            project_id=ProjectID("a0000000"),
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

        assert db.all_projects == {
            ProjectID("a0000000"): api.Project(
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
            ProjectID("b0000000"): api.Project(
                project_id=ProjectID("b0000000"),
                slug="b",
                title="B",
                env=Env.unknown(),
                project_license="",
                source_url="",
                issues_url="",
            ),
        }
        assert db.project(ProjectID("a0000000")) == api.Project(
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
        )
        assert db.project(ProjectID("c0000000")) is None

        assert db.all_versions == {
            VersionID("A0000000"): api.Version(
                version_id=VersionID("A0000000"),
                project_id=ProjectID("a0000000"),
                loaders={"fabric"},
                game_versions={"1.19.2"},
            ),
            VersionID("A1000000"): api.Version(
                version_id=VersionID("A1000000"),
                project_id=ProjectID("a0000000"),
                loaders={"fabric", "minecraft"},
                game_versions={"1.20"},
            ),
            VersionID("B0000000"): api.Version(
                version_id=VersionID("B0000000"),
                project_id=ProjectID("b0000000"),
                loaders={"minecraft"},
                game_versions={"1.19.4"},
            ),
            VersionID("B1000000"): api.Version(
                version_id=VersionID("B1000000"),
                project_id=ProjectID("b0000000"),
                loaders={"forge"},
                game_versions={"1.20"},
            ),
        }
        assert db.version(VersionID("A0000000")) == api.Version(
            version_id=VersionID("A0000000"),
            project_id=ProjectID("a0000000"),
            loaders={"fabric"},
            game_versions={"1.19.2"},
        )
        assert db.version(VersionID("C0000000")) is None

        assert db.all_project_versions == frozendict(
            {
                ProjectID("a0000000"): frozenset(
                    {
                        VersionID("A0000000"),
                        VersionID("A1000000"),
                    },
                ),
                ProjectID("b0000000"): frozenset(
                    {
                        VersionID("B0000000"),
                        VersionID("B1000000"),
                    },
                ),
            },
        )
        assert db.project_versions(ProjectID("a0000000")) == frozenset(
            {
                VersionID("A0000000"),
                VersionID("A1000000"),
            },
        )
        assert db.project_versions(ProjectID("c0000000")) == frozenset()

        # Not fetching versions
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json=testdata.FILE_A0 | testdata.FILE_B0 | testdata.FILE_B1,
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
                complete_qs=True,
                json=[
                    testdata.PROJECT_A,
                    testdata.PROJECT_B,
                ],
            )
            db = ModDB.load([mrpack1, mrpack2], fetch_versions=False)

        assert db.all_files == {
            Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("a0000000"),
                version_number="1.2.3",
            ),
            Sha512(
                "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("a0000000"),
                version_number="1.2.3",
            ),
            Sha512(
                "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("b0000000"),
                version_number="4.5.6",
            ),
            Sha512(
                "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ): api.File(
                sha512=Sha512(
                    "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                project_id=ProjectID("b0000000"),
                version_number="4.5.7",
            ),
        }
        assert db.file(
            Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
        ) == api.File(
            sha512=Sha512(
                "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
            project_id=ProjectID("a0000000"),
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

        assert db.all_projects == {
            ProjectID("a0000000"): api.Project(
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
            ProjectID("b0000000"): api.Project(
                project_id=ProjectID("b0000000"),
                slug="b",
                title="B",
                env=Env.unknown(),
                project_license="",
                source_url="",
                issues_url="",
            ),
        }
        assert db.project(ProjectID("a0000000")) == api.Project(
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
        )
        assert db.project(ProjectID("c0000000")) is None

        assert db.all_versions == {}
        assert db.version(VersionID("A0000000")) is None

        assert db.all_project_versions == frozendict()
        assert db.project_versions(ProjectID("A0000000")) == frozenset()

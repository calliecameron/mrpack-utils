from pathlib import PurePath

from frozendict import frozendict

from mrpack import api
from mrpack.index import Dependencies, File, Hashes, Index
from mrpack.moddb import ModDB
from mrpack.modpack import FileMissingMod, Mod, Modpack, ProjectMissingMod
from mrpack.mrpack import Mrpack, Override
from mrpack.types import (
    Env,
    GameVersion,
    ProjectID,
    Requirement,
    Sha1,
    Sha512,
    VersionID,
)

# ruff: noqa: S101


class TestMod:
    def test_properties(self) -> None:
        f = File(
            path="mods/a.jar",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(
                client=Requirement.REQUIRED,
                server=Requirement.REQUIRED,
            ),
            downloads=set(),
            size=10,
        )
        p = api.Project(
            project_id=ProjectID("a0000000"),
            slug="foo bar",
            title="Foo",
            env=Env(
                client=Requirement.REQUIRED,
                server=Requirement.OPTIONAL,
            ),
            project_license="MIT",
            source_url="S 1",
            issues_url="I 1",
        )

        m = Mod(
            index_entry=f,
            project=p,
            version_number="1.2",
            game_versions=frozenset(
                {
                    GameVersion("1.20"),
                    GameVersion("1.19.4"),
                },
            ),
        )
        assert m.index_entry == f
        assert m.project == p
        assert m.version_number == "1.2"
        assert m.link == "https://modrinth.com/mod/foo%20bar"
        assert m.env == Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED)
        assert m.game_versions == frozenset(
            {
                GameVersion("1.20"),
                GameVersion("1.19.4"),
            },
        )
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))


class TestModpack:
    def test_load(self) -> None:
        f1 = File(
            path="mods/a.jar",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads=set(),
            size=10,
        )
        f2 = File(
            path="mods/b.jar",
            hashes=Hashes(
                sha1=Sha1("b000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads=set(),
            size=10,
        )
        f3 = File(
            path="mods/c.jar",
            hashes=Hashes(
                sha1=Sha1("c000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads=set(),
            size=10,
        )
        f4 = File(
            path="mods/d.jar",
            hashes=Hashes(
                sha1=Sha1("d000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads=set(),
            size=10,
        )

        i = Index(
            name="Test Modpack",
            version="1",
            summary="",
            files={
                f1,
                f2,
                f3,
                f4,
            },
            dependencies=Dependencies(
                game_version=GameVersion("1.19.4"),
                others={
                    "foo": "1",
                    "fabric-loader": "2",
                },
            ),
        )

        o1 = Override(
            path="overrides/mods/unknown.jar",
            data=b"foo\n",
        )
        o2 = Override(
            path="overrides/config/foo.txt",
            data=b"bar\n",
        )

        m = Mrpack(
            index=i,
            overrides={o1, o2},
        )

        p1 = api.Project(
            project_id=ProjectID("a0000000"),
            slug="a",
            title="A",
            env=Env.unknown(),
            project_license="",
            source_url="",
            issues_url="",
        )
        p2 = api.Project(
            project_id=ProjectID("b0000000"),
            slug="b",
            title="B",
            env=Env(
                client=Requirement.OPTIONAL,
                server=Requirement.OPTIONAL,
            ),
            project_license="MIT",
            source_url="example.com",
            issues_url="example2.com",
        )

        db = ModDB(
            files={
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
                    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ): api.File(
                    sha512=Sha512(
                        "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    project_id=ProjectID("b0000000"),
                    version_number="4.5.6",
                ),
                Sha512(
                    "d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ): api.File(
                    sha512=Sha512(
                        "d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    project_id=ProjectID("d0000000"),
                    version_number="1.0.0",
                ),
            },
            projects={
                ProjectID("a0000000"): p1,
                ProjectID("b0000000"): p2,
            },
            versions={
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
            },
        )

        modpack = Modpack.load(m, db)

        assert modpack.index == i

        mods = sorted(modpack.mods.values(), key=lambda m: m.project.title.lower())
        assert len(mods) == 2  # noqa: PLR2004

        assert mods[0].index_entry == f1
        assert mods[0].project == p1
        assert mods[0].version_number == "1.2.3"
        assert mods[0].link == "https://modrinth.com/mod/a"
        assert mods[0].env == Env(
            client=Requirement.REQUIRED,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].game_versions == frozenset(
            {
                GameVersion("1.19.2"),
                GameVersion("1.20"),
            },
        )
        assert mods[0].latest_game_version == GameVersion("1.20")

        assert mods[1].index_entry == f2
        assert mods[1].project == p2
        assert mods[1].version_number == "4.5.6"
        assert mods[1].link == "https://modrinth.com/mod/b"
        assert mods[1].env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[1].latest_game_version == GameVersion("1.19.4")

        assert modpack.project_missing_mods == frozenset(
            {ProjectMissingMod(index_entry=f4, version_number="1.0.0")},
        )
        assert modpack.file_missing_mods == frozenset(
            {FileMissingMod(index_entry=f3)},
        )

        assert modpack.overrides == frozendict(
            {
                PurePath("overrides", "mods", "unknown.jar"): o1,
                PurePath("overrides", "config", "foo.txt"): o2,
            },
        )

from frozendict import frozendict

from mrpack_utils import api
from mrpack_utils.index import Dependencies, File, Hashes, Index
from mrpack_utils.moddb import ModDB
from mrpack_utils.modpack import Mod, Modpack
from mrpack_utils.mrpack import Mrpack, Override
from mrpack_utils.types import Env, GameVersion, ProjectID, Requirement, Sha1, Sha512, VersionID

# ruff: noqa: S101


class TestMod:
    def test_properties(self) -> None:
        m = Mod(
            name="Foo",
            slug="foo bar",
            version="1.2",
            original_env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            mod_license="MIT",
            source_url="https://example.com/a b",
            issues_url="example2.com",
            game_versions=frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        assert m.name == "Foo"
        assert m.link == "https://modrinth.com/mod/foo%20bar"
        assert m.version == "1.2"
        assert m.original_env == Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL)
        assert m.overridden_env == Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED)
        assert m.mod_license == "MIT"
        assert m.source_url == "https://example.com/a%20b"
        assert m.issues_url == "example2.com"
        assert m.game_versions == frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))


class TestModpack:
    def test_load(self) -> None:
        mrpack = Mrpack(
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
                        env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
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
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={
                        "foo": "1",
                        "fabric-loader": "2",
                    },
                ),
            ),
            overrides={
                Override(
                    path="overrides/mods/unknown.jar",
                    data=b"foo\n",
                ),
                Override(
                    path="overrides/config/foo.txt",
                    data=b"bar\n",
                ),
            },
            client_overrides=set(),
            server_overrides=set(),
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
            },
            projects={
                ProjectID("a0000000"): api.Project(
                    project_id=ProjectID("a0000000"),
                    slug="a",
                    title="A",
                    env=Env.unknown(),
                    project_license="",
                    source_url="",
                    issues_url="",
                ),
                ProjectID("b0000000"): api.Project(
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
                ),
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

        modpack = Modpack.load(mrpack, db)

        assert modpack.name == "Test Modpack"
        assert modpack.version == "1"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"foo": "1", "fabric-loader": "2"})
        assert modpack.loaders == frozenset({"minecraft", "fabric"})
        assert modpack.unknown_dependencies == frozenset({"foo"})

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004

        assert mods[0].name == "A"
        assert mods[0].link == "https://modrinth.com/mod/a"
        assert mods[0].version == "1.2.3"
        assert mods[0].original_env == Env.unknown()
        assert mods[0].overridden_env == Env(
            client=Requirement.REQUIRED,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].mod_license == ""
        assert mods[0].source_url == ""
        assert mods[0].issues_url == ""
        assert mods[0].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[0].latest_game_version == GameVersion("1.20")

        assert mods[1].name == "B"
        assert mods[1].link == "https://modrinth.com/mod/b"
        assert mods[1].version == "4.5.6"
        assert mods[1].original_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].overridden_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].mod_license == "MIT"
        assert mods[1].source_url == "example.com"
        assert mods[1].issues_url == "example2.com"
        assert mods[1].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[1].latest_game_version == GameVersion("1.19.4")

        assert modpack.missing_mods == frozenset({"c.jar"})
        assert modpack.unknown_mods == frozendict({"overrides/mods/unknown.jar": "7e3265a8"})
        assert modpack.other_files == frozendict({"overrides/config/foo.txt": "04a2b3e9"})

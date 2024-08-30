import pytest
import requests_mock
from frozendict import frozendict

from mrpack_utils.mods import (
    Env,
    GameVersion,
    Mod,
    Modpack,
    ModpackError,
    Requirement,
    _MrpackFile,
)


class TestRequirement:
    def test_from_str(self) -> None:
        assert Requirement.from_str("") == Requirement.UNKNOWN
        assert Requirement.from_str("unknown") == Requirement.UNKNOWN
        assert Requirement.from_str("required") == Requirement.REQUIRED
        assert Requirement.from_str("optional") == Requirement.OPTIONAL
        assert Requirement.from_str("unsupported") == Requirement.UNSUPPORTED
        with pytest.raises(ValueError):
            Requirement.from_str("foo")


class TestEnv:
    def test_from_dict(self) -> None:
        e = Env.from_dict({"client": "required", "server": "optional"})
        assert e.client == Requirement.REQUIRED
        assert e.server == Requirement.OPTIONAL

        with pytest.raises(ValueError):
            Env.from_dict({"client": "required"})
        with pytest.raises(ValueError):
            Env.from_dict({"client": "required", "server": "foo"})


class TestGameVersion:
    def test_version(self) -> None:
        assert str(GameVersion("1.20.1")) == "1.20.1"
        assert str(GameVersion("1.19")) == "1.19"
        with pytest.raises(ValueError):
            GameVersion("1")
        with pytest.raises(ValueError):
            GameVersion("a")
        with pytest.raises(ValueError):
            GameVersion("19.2-dev")

    def test_eq(self) -> None:
        assert GameVersion("1.19.4") == GameVersion("1.19.4")
        assert GameVersion("1.19.4") != GameVersion("1.20")
        with pytest.raises(NotImplementedError):
            assert GameVersion("1.20") == "1.20"

    def test_hash(self) -> None:
        assert hash(GameVersion("1.19.4")) == hash(GameVersion("1.19.4"))
        assert hash(GameVersion("1.19.4")) != hash(GameVersion("1.20"))

    def test_lt(self) -> None:
        assert GameVersion("1.19.4") < GameVersion("1.20")
        assert GameVersion("1.2") < GameVersion("1.10")
        assert GameVersion("1.20") < GameVersion("1.20.1")
        assert GameVersion("1.20") > GameVersion("1.19.4")
        with pytest.raises(NotImplementedError):
            assert GameVersion("1.20") < "1.20"

    def test_from_list(self) -> None:
        assert GameVersion.from_list(["1.19", "1.20-dev", "1.18.4", "1.19", "foo"]) == frozenset(
            [GameVersion("1.19"), GameVersion("1.18.4")],
        )


class TestMrpackFile:
    def test_from_file(self) -> None:
        m = _MrpackFile.from_file("testdata/test.mrpack")
        assert m.name == "Test Modpack"
        assert m.version == "1.1"
        assert m.game_version == GameVersion("1.19.4")
        assert m.dependencies == frozendict({"fabric-loader": "0.16", "foo": "1"})
        assert m.mod_hashes == frozenset(["abcd", "fedc", "pqrs"])
        assert m.mod_jars == frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"})
        assert m.mod_envs == frozendict(
            {
                "abcd": Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            },
        )
        assert m.unknown_mods == frozendict(
            {
                "client-overrides/mods/baz-1.0.0.jar": "a2c6f513",
                "client-overrides/mods/foo-1.2.3.jar": "d6902afc",
                "overrides/mods/foo-1.2.3.jar": "d6902afc",
                "server-overrides/mods/bar-1.0.0.jar": "7123eea6",
            },
        )
        assert m.other_files == frozendict(
            {
                "overrides/config/foo.txt": "7e3265a8",
                "server-overrides/config/bar.txt": "04a2b3e9",
            },
        )

        with pytest.raises(ModpackError):
            _MrpackFile.from_file("testdata/modrinth.index.json")


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
        mrpack1 = _MrpackFile(
            name="Test Modpack",
            version="1",
            game_version=GameVersion("1.19.4"),
            dependencies=frozendict({"foo": "1"}),
            mod_hashes=frozenset(["abcd", "fedc", "pqrs"]),
            mod_jars=frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"}),
            mod_envs=frozendict(
                {"abcd": Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL)},
            ),
            unknown_mods=frozendict({"overrides/mods/unknown.jar": "a"}),
            other_files=frozendict({"overrides/config/foo.txt": "b"}),
        )
        mrpack2 = _MrpackFile(
            name="Test Modpack",
            version="2",
            game_version=GameVersion("1.19.4"),
            dependencies=frozendict({"foo": "2"}),
            mod_hashes=frozenset(["abcd", "lmno", "pqrs"]),
            mod_jars=frozendict({"abcd": "foo.jar", "lmno": "bar.jar", "pqrs": "baz.jar"}),
            mod_envs=frozendict(
                {"abcd": Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL)},
            ),
            unknown_mods=frozendict({"overrides/mods/unknown.jar": "c"}),
            other_files=frozendict({"overrides/config/foo.txt": "d"}),
        )

        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "baz",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd",
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "wxyz",
                                },
                            },
                        ],
                    },
                    "fedc": {
                        "project_id": "quux",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc",
                                },
                            },
                        ],
                    },
                    "lmno": {
                        "project_id": "quux",
                        "version_number": "4.5.7",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "lmno",
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["baz", "quux"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                    },
                    {
                        "id": "quux",
                        "title": "Bar",
                        "slug": "bar",
                        "game_versions": ["1.19.4"],
                        "client_side": "optional",
                        "server_side": "optional",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                ],
            )
            modpacks = Modpack._load(mrpack1, mrpack2)  # noqa: SLF001

        assert len(modpacks) == 2  # noqa: PLR2004

        modpack = modpacks[0]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "1"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"foo": "1"})

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].version == "4.5.6"
        assert mods[0].original_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].overridden_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].mod_license == "MIT"
        assert mods[0].source_url == "example.com"
        assert mods[0].issues_url == "example2.com"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[0].latest_game_version == GameVersion("1.19.4")

        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].version == "1.2.3"
        assert mods[1].original_env == Env(
            client=Requirement.UNKNOWN,
            server=Requirement.UNKNOWN,
        )
        assert mods[1].overridden_env == Env(
            client=Requirement.REQUIRED,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].mod_license == ""
        assert mods[1].source_url == ""
        assert mods[1].issues_url == ""
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[1].latest_game_version == GameVersion("1.20")

        assert modpack.missing_mods == frozenset({"baz.jar"})
        assert modpack.unknown_mods == frozendict({"overrides/mods/unknown.jar": "a"})
        assert modpack.other_files == frozendict({"overrides/config/foo.txt": "b"})

        modpack = modpacks[1]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "2"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"foo": "2"})

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].version == "4.5.7"
        assert mods[0].original_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].overridden_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].mod_license == "MIT"
        assert mods[0].source_url == "example.com"
        assert mods[0].issues_url == "example2.com"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[0].latest_game_version == GameVersion("1.19.4")

        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].version == "1.2.3"
        assert mods[1].original_env == Env(
            client=Requirement.UNKNOWN,
            server=Requirement.UNKNOWN,
        )
        assert mods[1].overridden_env == Env(
            client=Requirement.REQUIRED,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].mod_license == ""
        assert mods[1].source_url == ""
        assert mods[1].issues_url == ""
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[1].latest_game_version == GameVersion("1.20")

        assert modpack.missing_mods == frozenset({"baz.jar"})
        assert modpack.unknown_mods == frozendict({"overrides/mods/unknown.jar": "c"})
        assert modpack.other_files == frozendict({"overrides/config/foo.txt": "d"})

    def test_from_files(self) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "foo",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd",
                                },
                            },
                        ],
                    },
                    "fedc": {
                        "project_id": "bar",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc",
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["bar", "foo"]',
                complete_qs=True,
                json=[
                    {
                        "id": "foo",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                    },
                    {
                        "id": "bar",
                        "title": "Bar",
                        "slug": "bar",
                        "game_versions": ["1.19.4"],
                        "client_side": "optional",
                        "server_side": "optional",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                ],
            )
            (modpack,) = Modpack.from_files("testdata/test.mrpack")

        assert modpack.name == "Test Modpack"
        assert modpack.version == "1.1"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"fabric-loader": "0.16", "foo": "1"})

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004

        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].version == "4.5.6"
        assert mods[0].original_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].overridden_env == Env(
            client=Requirement.OPTIONAL,
            server=Requirement.OPTIONAL,
        )
        assert mods[0].mod_license == "MIT"
        assert mods[0].source_url == "example.com"
        assert mods[0].issues_url == "example2.com"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[0].latest_game_version == GameVersion("1.19.4")

        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].version == "1.2.3"
        assert mods[1].original_env == Env(
            client=Requirement.UNKNOWN,
            server=Requirement.UNKNOWN,
        )
        assert mods[1].overridden_env == Env(
            client=Requirement.REQUIRED,
            server=Requirement.OPTIONAL,
        )
        assert mods[1].mod_license == ""
        assert mods[1].source_url == ""
        assert mods[1].issues_url == ""
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[1].latest_game_version == GameVersion("1.20")

        assert modpack.missing_mods == frozenset({"baz.jar"})
        assert modpack.unknown_mods == frozendict(
            {
                "client-overrides/mods/baz-1.0.0.jar": "a2c6f513",
                "client-overrides/mods/foo-1.2.3.jar": "d6902afc",
                "overrides/mods/foo-1.2.3.jar": "d6902afc",
                "server-overrides/mods/bar-1.0.0.jar": "7123eea6",
            },
        )
        assert modpack.other_files == frozendict(
            {
                "overrides/config/foo.txt": "7e3265a8",
                "server-overrides/config/bar.txt": "04a2b3e9",
            },
        )

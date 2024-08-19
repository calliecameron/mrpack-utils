import pytest
import requests_mock
from frozendict import frozendict

from compatibility import (
    Env,
    GameVersion,
    InstalledMod,
    Mod,
    Modpack,
    ModpackError,
    MrpackFile,
    Requirement,
    check_compatibility,
    make_table,
    write_csv,
    write_incompatible,
    write_missing,
    write_table,
    write_unknown,
)


class TestRequirement:
    def test_from_str(self) -> None:
        assert Requirement.from_str("") == Requirement.UNKNOWN
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
        m = MrpackFile.from_file("testdata/test.mrpack")
        assert m.name == "Test Modpack"
        assert m.version == "1.1"
        assert m.game_version == GameVersion("1.19.4")
        assert m.mod_hashes == frozenset(["abcd", "fedc", "pqrs"])
        assert m.mod_jars == frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"})
        assert m.mod_envs == frozendict(
            {
                "abcd": Env(Requirement.REQUIRED, Requirement.OPTIONAL),
            },
        )
        assert m.unknown_mods == frozenset(["foo-1.2.3.jar", "bar-1.0.0.jar", "baz-1.0.0.jar"])

        with pytest.raises(ModpackError):
            MrpackFile.from_file("testdata/modrinth.index.json")


class TestMod:
    def test_properties(self) -> None:
        m = Mod(
            "Foo",
            "foo",
            Env(Requirement.REQUIRED, Requirement.OPTIONAL),
            "MIT",
            "example.com",
            "example2.com",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        assert m.name == "Foo"
        assert m.link == "https://modrinth.com/mod/foo"
        assert m.env == Env(Requirement.REQUIRED, Requirement.OPTIONAL)
        assert m.mod_license == "MIT"
        assert m.source_url == "example.com"
        assert m.issues_url == "example2.com"
        assert m.game_versions == frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))


class TestInstalledMod:
    def test_properties(self) -> None:
        m = InstalledMod(
            Mod(
                "Foo",
                "foo",
                Env(Requirement.REQUIRED, Requirement.OPTIONAL),
                "MIT",
                "example.com",
                "example2.com",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
            "1.2",
            Env(Requirement.REQUIRED, Requirement.REQUIRED),
        )
        assert m.name == "Foo"
        assert m.link == "https://modrinth.com/mod/foo"
        assert m.version == "1.2"
        assert m.original_env == Env(Requirement.REQUIRED, Requirement.OPTIONAL)
        assert m.overridden_env == Env(Requirement.REQUIRED, Requirement.REQUIRED)
        assert m.mod_license == "MIT"
        assert m.source_url == "example.com"
        assert m.issues_url == "example2.com"
        assert m.game_versions == frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))


class TestModpack:
    def test_load(self) -> None:
        mrpack1 = MrpackFile(
            "Test Modpack",
            "1",
            GameVersion("1.19.4"),
            frozenset(["abcd", "fedc", "pqrs"]),
            frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"}),
            frozendict({"abcd": Env(Requirement.REQUIRED, Requirement.OPTIONAL)}),
            frozenset(["unknown.jar"]),
        )
        mrpack2 = MrpackFile(
            "Test Modpack",
            "2",
            GameVersion("1.19.4"),
            frozenset(["abcd", "lmno", "pqrs"]),
            frozendict({"abcd": "foo.jar", "lmno": "bar.jar", "pqrs": "baz.jar"}),
            frozendict({"abcd": Env(Requirement.REQUIRED, Requirement.OPTIONAL)}),
            frozenset(["unknown.jar"]),
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
                        "client": "optional",
                        "server": "optional",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                ],
            )
            modpacks = Modpack.load(mrpack1, mrpack2)

        assert len(modpacks) == 2  # noqa: PLR2004

        modpack = modpacks[0]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "1"
        assert modpack.game_version == GameVersion("1.19.4")

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].version == "4.5.6"
        assert mods[0].original_env == Env(Requirement.OPTIONAL, Requirement.OPTIONAL)
        assert mods[0].overridden_env == Env(Requirement.OPTIONAL, Requirement.OPTIONAL)
        assert mods[0].mod_license == "MIT"
        assert mods[0].source_url == "example.com"
        assert mods[0].issues_url == "example2.com"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[0].latest_game_version == GameVersion("1.19.4")

        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].version == "1.2.3"
        assert mods[1].original_env == Env(Requirement.UNKNOWN, Requirement.UNKNOWN)
        assert mods[1].overridden_env == Env(Requirement.REQUIRED, Requirement.OPTIONAL)
        assert mods[1].mod_license == ""
        assert mods[1].source_url == ""
        assert mods[1].issues_url == ""
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[1].latest_game_version == GameVersion("1.20")

        assert modpack.missing_mods == frozenset({"baz.jar"})
        assert modpack.unknown_mods == frozenset({"unknown.jar"})

        modpack = modpacks[1]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "2"
        assert modpack.game_version == GameVersion("1.19.4")

        mods = sorted(modpack.mods.values(), key=lambda m: m.name.lower())
        assert len(mods) == 2  # noqa: PLR2004
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].version == "4.5.7"
        assert mods[0].original_env == Env(Requirement.OPTIONAL, Requirement.OPTIONAL)
        assert mods[0].overridden_env == Env(Requirement.OPTIONAL, Requirement.OPTIONAL)
        assert mods[0].mod_license == "MIT"
        assert mods[0].source_url == "example.com"
        assert mods[0].issues_url == "example2.com"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[0].latest_game_version == GameVersion("1.19.4")

        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].version == "1.2.3"
        assert mods[1].original_env == Env(Requirement.UNKNOWN, Requirement.UNKNOWN)
        assert mods[1].overridden_env == Env(Requirement.REQUIRED, Requirement.OPTIONAL)
        assert mods[1].mod_license == ""
        assert mods[1].source_url == ""
        assert mods[1].issues_url == ""
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])
        assert mods[1].latest_game_version == GameVersion("1.20")

        assert modpack.missing_mods == frozenset({"baz.jar"})
        assert modpack.unknown_mods == frozenset({"unknown.jar"})


def test_make_table() -> None:
    foo = InstalledMod(
        Mod(
            "Foo",
            "foo",
            Env(Requirement.OPTIONAL, Requirement.OPTIONAL),
            "MIT",
            "example.com",
            "example2.com",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ),
        "1.2.3",
        Env(Requirement.REQUIRED, Requirement.OPTIONAL),
    )
    bar = InstalledMod(
        Mod(
            "Bar",
            "bar",
            Env(Requirement.REQUIRED, Requirement.REQUIRED),
            "GPL",
            "",
            "",
            frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
        ),
        "4.5.6",
        Env(Requirement.REQUIRED, Requirement.OPTIONAL),
    )
    modpack = Modpack(
        "Test Modpack",
        "1",
        GameVersion("1.19.4"),
        {"abcd": foo, "fedc": bar},
        frozenset(),
        frozenset(),
    )
    table, incompatible = make_table(
        modpack,
        frozenset([GameVersion("1.19.4"), GameVersion("1.20")]),
    )

    assert table == [
        (
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "1.19.4",
            "1.20",
        ),
        (
            "Bar",
            "https://modrinth.com/mod/bar",
            "4.5.6",
            "required",
            "optional",
            "1.19.4",
            "yes",
            "no",
        ),
        (
            "Foo",
            "https://modrinth.com/mod/foo",
            "1.2.3",
            "required",
            "optional",
            "1.20",
            "yes",
            "yes",
        ),
    ]
    assert incompatible == {
        GameVersion("1.19.4"): frozenset(),
        GameVersion("1.20"): frozenset([bar]),
    }


def test_write_csv(capsys: pytest.CaptureFixture[str]) -> None:
    table = [
        (
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "1.19.4",
            "1.20",
        ),
        (
            "Bar",
            "https://modrinth.com/mod/bar",
            "4.5.6",
            "required",
            "optional",
            "1.19.4",
            "yes",
            "no",
        ),
        (
            "Foo",
            "https://modrinth.com/mod/foo",
            "1.2.3",
            "required",
            "optional",
            "1.20",
            "yes",
            "yes",
        ),
    ]
    write_csv(table)
    assert (
        capsys.readouterr().out
        == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,4.5.6,required,optional,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,yes,yes\r
"""
    )


def test_write_table(capsys: pytest.CaptureFixture[str]) -> None:
    table = [
        (
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "1.19.4",
            "1.20",
        ),
        (
            "Bar",
            "https://modrinth.com/mod/bar",
            "4.5.6",
            "required",
            "optional",
            "1.19.4",
            "yes",
            "no",
        ),
        (
            "Foo",
            "https://modrinth.com/mod/foo",
            "1.2.3",
            "required",
            "optional",
            "1.20",
            "yes",
            "yes",
        ),
    ]
    write_table(table)
    assert (
        capsys.readouterr().out
        == """| Name   | Link                         | Installed version   | On client   | On server   | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|---------------------|-------------|-------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 4.5.6               | required    | optional    | 1.19.4                | yes      | no     |
| Foo    | https://modrinth.com/mod/foo | 1.2.3               | required    | optional    | 1.20                  | yes      | yes    |
"""  # noqa: E501
    )


def test_write_missing(capsys: pytest.CaptureFixture[str]) -> None:
    write_missing(frozenset())
    assert capsys.readouterr().out == ""

    write_missing(frozenset(["foo", "bar"]))
    assert (
        capsys.readouterr().out
        == """
Mods supposed to be on Modrinth, but not found:
  bar
  foo
"""
    )


def test_write_unknown(capsys: pytest.CaptureFixture[str]) -> None:
    write_unknown(frozenset())
    assert capsys.readouterr().out == ""

    write_unknown(frozenset(["foo", "bar"]))
    assert (
        capsys.readouterr().out
        == """
Unknown mods (probably from CurseForge) - must be checked manually:
  bar
  foo
"""
    )


def test_write_incompatible(capsys: pytest.CaptureFixture[str]) -> None:
    foo = InstalledMod(
        Mod(
            "Foo",
            "foo",
            Env(Requirement.REQUIRED, Requirement.REQUIRED),
            "MIT",
            "example.com",
            "example2.com",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ),
        "1.2.3",
        Env(Requirement.REQUIRED, Requirement.OPTIONAL),
    )
    bar = InstalledMod(
        Mod(
            "Bar",
            "bar",
            Env(Requirement.REQUIRED, Requirement.UNSUPPORTED),
            "",
            "",
            "",
            frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
        ),
        "4.5.6",
        Env(Requirement.REQUIRED, Requirement.OPTIONAL),
    )

    incompatible = {
        GameVersion("1.19.4"): frozenset(),
        GameVersion("1.20"): frozenset([bar]),
        GameVersion("1.18"): frozenset([foo, bar]),
    }

    write_incompatible(
        2,
        frozenset([GameVersion("1.19.4"), GameVersion("1.20"), GameVersion("1.18")]),
        GameVersion("1.19.4"),
        incompatible,
    )

    assert (
        capsys.readouterr().out
        == """
Modpack game version: 1.19.4

For version 1.18:
  2 out of 2 mods are incompatible with this version:
    Bar
    Foo

For version 1.19.4:
  All mods are compatible with this version

For version 1.20:
  1 out of 2 mods are incompatible with this version:
    Bar
"""
    )


def test_check_compatibility(capsys: pytest.CaptureFixture[str]) -> None:
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
                    "client": "optional",
                    "server": "required",
                },
                {
                    "id": "quux",
                    "title": "Bar",
                    "slug": "bar",
                    "game_versions": ["1.19.4"],
                },
            ],
        )
        check_compatibility(["1.20"], "testdata/test.mrpack", True)
        assert (
            capsys.readouterr().out
            == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,4.5.6,unknown,unknown,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,no,yes\r
"""
        )

        check_compatibility(["1.20"], "testdata/test.mrpack", False)
        assert (
            capsys.readouterr().out
            == """| Name   | Link                         | Installed version   | On client   | On server   | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|---------------------|-------------|-------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 4.5.6               | unknown     | unknown     | 1.19.4                | yes      | no     |
| Foo    | https://modrinth.com/mod/foo | 1.2.3               | required    | optional    | 1.20                  | no       | yes    |

Mods supposed to be on Modrinth, but not found:
  baz.jar

Unknown mods (probably from CurseForge) - must be checked manually:
  bar-1.0.0.jar
  baz-1.0.0.jar
  foo-1.2.3.jar

Modpack game version: 1.19.4

For version 1.19.4:
  1 out of 2 mods are incompatible with this version:
    Foo

For version 1.20:
  1 out of 2 mods are incompatible with this version:
    Bar
"""  # noqa: E501
        )

import pytest
import requests_mock
from frozendict import frozendict

from compatibility import (
    GameVersion,
    Mod,
    Modpack,
    ModpackError,
    check_compatibility,
    make_table,
    write_csv,
    write_incompatible,
    write_missing,
    write_table,
    write_unknown,
)


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


class TestMod:
    def test_properties(self) -> None:
        m = Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        assert m.name == "Foo"
        assert m.link == "https://modrinth.com/mod/foo"
        assert m.installed_version == "1.2.3"
        assert m.client == "required"
        assert m.server == ""
        assert m.game_versions == frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))

    def test_eq(self) -> None:
        # Only ID matters
        assert Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ) == Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        assert Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ) == Mod(
            "1234",
            "Bar",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        assert Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ) != Mod(
            "1235",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        with pytest.raises(NotImplementedError):
            assert (
                Mod(
                    "1234",
                    "Foo",
                    "foo",
                    "1.2.3",
                    "required",
                    "",
                    frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
                )
                == "foo"
            )

    def test_hash(self) -> None:
        # Only ID matters
        assert hash(
            Mod(
                "1234",
                "Foo",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        ) == hash(
            Mod(
                "1234",
                "Foo",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        )
        assert hash(
            Mod(
                "1234",
                "Foo",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        ) == hash(
            Mod(
                "1234",
                "Bar",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        )
        assert hash(
            Mod(
                "1234",
                "Foo",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        ) != hash(
            Mod(
                "1235",
                "Foo",
                "foo",
                "1.2.3",
                "required",
                "",
                frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
            ),
        )

    def test_lt(self) -> None:
        # Only name matters, case insensitively
        assert Mod(
            "1234",
            "bar",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        ) < Mod(
            "1234",
            "Foo",
            "foo",
            "1.2.3",
            "required",
            "",
            frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        with pytest.raises(NotImplementedError):
            assert (
                Mod(
                    "1234",
                    "Foo",
                    "foo",
                    "1.2.3",
                    "required",
                    "",
                    frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
                )
                < "foo"
            )


class TestModpack:
    def test_from_file(self) -> None:
        m = Modpack.from_file("testdata/test.mrpack")
        assert m.mod_hashes == frozenset(["abcd", "fedc", "pqrs"])
        assert m.mod_jars == frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"})
        assert m.mod_envs == frozendict(
            {"abcd": frozendict({"client": "required", "server": "optional"})},
        )
        assert m.game_version == GameVersion("1.19.4")
        assert m.unknown_mods == frozenset(["foo-1.2.3.jar", "bar-1.0.0.jar", "baz-1.0.0.jar"])

        with pytest.raises(ModpackError):
            Modpack.from_file("testdata/modrinth.index.json")

    def test_load_mods(self) -> None:
        modpack = Modpack(
            frozenset(["abcd", "fedc", "pqrs"]),
            frozendict({"abcd": "foo.jar", "fedc": "bar.jar", "pqrs": "baz.jar"}),
            {"abcd": {"client": "required", "server": "optional"}},
            GameVersion("1.19.4"),
            frozenset(),
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
                    },
                ],
            )
            raw_mods, missing_mods = modpack.load_mods()

        mods = sorted(raw_mods)
        assert len(mods) == 2  # noqa: PLR2004
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].installed_version == "4.5.6"
        assert mods[0].client == ""
        assert mods[0].server == ""
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].installed_version == "1.2.3"
        assert mods[1].client == "required"
        assert mods[1].server == "optional"
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])

        assert missing_mods == frozenset({"baz.jar"})


def test_make_table() -> None:
    foo = Mod(
        "abcd",
        "Foo",
        "foo",
        "1.2.3",
        "required",
        "optional",
        frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
    )
    bar = Mod(
        "fedc",
        "Bar",
        "bar",
        "4.5.6",
        "required",
        "",
        frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
    )
    mods = frozenset([foo, bar])
    table, incompatible = make_table(mods, frozenset([GameVersion("1.19.4"), GameVersion("1.20")]))

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
        ("Bar", "https://modrinth.com/mod/bar", "4.5.6", "required", "", "1.19.4", "yes", "no"),
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
        ("Foo", "https://modrinth.com/mod/foo", "1.2.3", "required", "", "1.20", "yes", "yes"),
    ]
    write_csv(table)
    assert (
        capsys.readouterr().out
        == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,4.5.6,required,optional,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.2.3,required,,1.20,yes,yes\r
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
        ("Foo", "https://modrinth.com/mod/foo", "1.2.3", "required", "", "1.20", "yes", "yes"),
    ]
    write_table(table)
    assert (
        capsys.readouterr().out
        == """| Name   | Link                         | Installed version   | On client   | On server   | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|---------------------|-------------|-------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 4.5.6               | required    | optional    | 1.19.4                | yes      | no     |
| Foo    | https://modrinth.com/mod/foo | 1.2.3               | required    |             | 1.20                  | yes      | yes    |
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
    foo = Mod(
        "abcd",
        "Foo",
        "foo",
        "1.2.3",
        "required",
        "optional",
        frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
    )
    bar = Mod(
        "fedc",
        "Bar",
        "bar",
        "4.5.6",
        "required",
        "",
        frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
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
                {"id": "baz", "title": "Foo", "slug": "foo", "game_versions": ["1.19.2", "1.20"]},
                {"id": "quux", "title": "Bar", "slug": "bar", "game_versions": ["1.19.4"]},
            ],
        )
        check_compatibility(["1.20"], "testdata/test.mrpack", True)
        assert (
            capsys.readouterr().out
            == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,4.5.6,,,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,no,yes\r
"""
        )

        check_compatibility(["1.20"], "testdata/test.mrpack", False)
        assert (
            capsys.readouterr().out
            == """| Name   | Link                         | Installed version   | On client   | On server   | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|---------------------|-------------|-------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 4.5.6               |             |             | 1.19.4                | yes      | no     |
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

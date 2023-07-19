import pytest
import requests_mock

from compatibility import (
    GameVersion,
    Mod,
    Modpack,
    ModpackException,
    check_compatibility,
    make_table,
    write_csv,
    write_incompatible,
    write_table,
)

# pylint: disable=disallowed-name
# flake8: noqa


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
            GameVersion("1.20") == "1.20"  # pylint: disable=expression-not-assigned

    def test_hash(self) -> None:
        assert hash(GameVersion("1.19.4")) == hash(GameVersion("1.19.4"))
        assert hash(GameVersion("1.19.4")) != hash(GameVersion("1.20"))

    def test_lt(self) -> None:
        assert GameVersion("1.19.4") < GameVersion("1.20")
        assert GameVersion("1.2") < GameVersion("1.10")
        assert GameVersion("1.20") < GameVersion("1.20.1")
        assert GameVersion("1.20") > GameVersion("1.19.4")
        with pytest.raises(NotImplementedError):
            GameVersion("1.20") < "1.20"  # pylint: disable=expression-not-assigned

    def test_from_list(self) -> None:
        assert GameVersion.from_list(["1.19", "1.20-dev", "1.18.4", "1.19", "foo"]) == frozenset(
            [GameVersion("1.19"), GameVersion("1.18.4")]
        )


class TestMod:
    def test_properties(self) -> None:
        m = Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        assert m.name == "Foo"
        assert m.link == "https://modrinth.com/mod/foo"
        assert m.game_versions == frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        assert m.latest_game_version == GameVersion("1.20")
        assert m.compatible_with(GameVersion("1.19.4"))
        assert m.compatible_with(GameVersion("1.20"))
        assert not m.compatible_with(GameVersion("1.20.1"))

    def test_eq(self) -> None:
        # Only ID matters
        assert Mod(
            "1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        ) == Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        assert Mod(
            "1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        ) == Mod("1234", "Bar", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        assert Mod(
            "1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        ) != Mod("1235", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        with pytest.raises(NotImplementedError):
            Mod(  # pylint: disable=expression-not-assigned
                "1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
            ) == "foo"

    def test_hash(self) -> None:
        # Only ID matters
        assert hash(
            Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        ) == hash(
            Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        )
        assert hash(
            Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        ) == hash(
            Mod("1234", "Bar", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        )
        assert hash(
            Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        ) != hash(
            Mod("1235", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        )

    def test_lt(self) -> None:
        # Only name matters, case insensitively
        assert Mod(
            "1234", "bar", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
        ) < Mod("1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
        with pytest.raises(NotImplementedError):
            Mod(  # pylint: disable=expression-not-assigned
                "1234", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")])
            ) < "foo"


class TestModpack:
    def test_from_file(self) -> None:
        m = Modpack.from_file("testdata/test.mrpack")
        assert m.mod_hashes == frozenset(["abcd", "fedc"])
        assert m.game_version == GameVersion("1.19.4")

        with pytest.raises(ModpackException):
            Modpack.from_file("testdata/modrinth.index.json")

    def test_load_mods(self) -> None:
        modpack = Modpack(frozenset(["abcd", "fedc"]), GameVersion("1.19.4"))
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "foo",
                    },
                    "fedc": {
                        "project_id": "bar",
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["bar", "foo"]',
                complete_qs=True,
                json=[
                    {
                        "id": "abcd",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                    },
                    {"id": "fedc", "title": "Bar", "slug": "bar", "game_versions": ["1.19.4"]},
                ],
            )
            mods = sorted(modpack.load_mods())

        assert len(mods) == 2
        assert mods[0].name == "Bar"
        assert mods[0].link == "https://modrinth.com/mod/bar"
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4")])
        assert mods[1].name == "Foo"
        assert mods[1].link == "https://modrinth.com/mod/foo"
        assert mods[1].game_versions == frozenset([GameVersion("1.19.2"), GameVersion("1.20")])


def test_make_table() -> None:
    foo = Mod("abcd", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
    bar = Mod("fedc", "Bar", "bar", frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]))
    mods = frozenset([foo, bar])
    table, incompatible = make_table(mods, frozenset([GameVersion("1.19.4"), GameVersion("1.20")]))

    assert table == [
        ("Name", "Link", "Latest game version", "1.19.4", "1.20"),
        ("Bar", "https://modrinth.com/mod/bar", "1.19.4", "yes", "no"),
        ("Foo", "https://modrinth.com/mod/foo", "1.20", "yes", "yes"),
    ]
    assert incompatible == {
        GameVersion("1.19.4"): frozenset(),
        GameVersion("1.20"): frozenset([bar]),
    }


def test_write_csv(capsys: pytest.CaptureFixture[str]) -> None:
    table = [
        ("Name", "Link", "Latest game version", "1.19.4", "1.20"),
        ("Bar", "https://modrinth.com/mod/bar", "1.19.4", "yes", "no"),
        ("Foo", "https://modrinth.com/mod/foo", "1.20", "yes", "yes"),
    ]
    write_csv(table)
    assert (
        capsys.readouterr().out
        == """Name,Link,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.20,yes,yes\r
"""
    )


def test_write_table(capsys: pytest.CaptureFixture[str]) -> None:
    table = [
        ("Name", "Link", "Latest game version", "1.19.4", "1.20"),
        ("Bar", "https://modrinth.com/mod/bar", "1.19.4", "yes", "no"),
        ("Foo", "https://modrinth.com/mod/foo", "1.20", "yes", "yes"),
    ]
    write_table(table)
    assert (
        capsys.readouterr().out
        == """| Name   | Link                         | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 1.19.4                | yes      | no     |
| Foo    | https://modrinth.com/mod/foo | 1.20                  | yes      | yes    |
"""
    )


def test_write_incompatible(capsys: pytest.CaptureFixture[str]) -> None:
    foo = Mod("abcd", "Foo", "foo", frozenset([GameVersion("1.20"), GameVersion("1.19.4")]))
    bar = Mod("fedc", "Bar", "bar", frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]))

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
                    "project_id": "foo",
                },
                "fedc": {
                    "project_id": "bar",
                },
            },
        )
        m.get(
            'https://api.modrinth.com/v2/projects?ids=["bar", "foo"]',
            complete_qs=True,
            json=[
                {"id": "abcd", "title": "Foo", "slug": "foo", "game_versions": ["1.19.2", "1.20"]},
                {"id": "fedc", "title": "Bar", "slug": "bar", "game_versions": ["1.19.4"]},
            ],
        )
        check_compatibility(["1.20"], "testdata/test.mrpack", True)
        assert (
            capsys.readouterr().out
            == """Name,Link,Latest game version,1.19.4,1.20\r
Bar,https://modrinth.com/mod/bar,1.19.4,yes,no\r
Foo,https://modrinth.com/mod/foo,1.20,no,yes\r
"""
        )

        check_compatibility(["1.20"], "testdata/test.mrpack", False)
        assert (
            capsys.readouterr().out
            # pylint: disable=line-too-long
            == """| Name   | Link                         | Latest game version   | 1.19.4   | 1.20   |
|--------|------------------------------|-----------------------|----------|--------|
| Bar    | https://modrinth.com/mod/bar | 1.19.4                | yes      | no     |
| Foo    | https://modrinth.com/mod/foo | 1.20                  | no       | yes    |

Modpack game version: 1.19.4

For version 1.19.4:
  1 out of 2 mods are incompatible with this version:
    Foo

For version 1.20:
  1 out of 2 mods are incompatible with this version:
    Bar
"""
        )

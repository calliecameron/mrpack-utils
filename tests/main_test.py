import pytest
import requests_mock

from mrpack_utils.main import (
    check_compatibility,
    make_table,
)
from mrpack_utils.mods import (
    Env,
    GameVersion,
    Mod,
    Modpack,
    Requirement,
)


def test_make_table() -> None:
    foo = Mod(
        name="Foo",
        slug="foo",
        version="1.2.3",
        original_env=Env(client=Requirement.OPTIONAL, server=Requirement.OPTIONAL),
        overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
        mod_license="MIT",
        source_url="example.com",
        issues_url="example2.com",
        game_versions=frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
    )
    bar = Mod(
        name="Bar",
        slug="bar",
        version="4.5.6",
        original_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
        overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
        mod_license="GPL",
        source_url="",
        issues_url="",
        game_versions=frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
    )
    modpack = Modpack(
        name="Test Modpack",
        version="1",
        game_version=GameVersion("1.19.4"),
        mods={"abcd": foo, "fedc": bar},
        missing_mods=frozenset(),
        unknown_mods=frozenset(),
    )
    table, incompatible = make_table(
        modpack,
        frozenset([GameVersion("1.19.4"), GameVersion("1.20")]),
    )

    assert table.data == [
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
            == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20
Bar,https://modrinth.com/mod/bar,4.5.6,unknown,unknown,1.19.4,yes,no
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,no,yes
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

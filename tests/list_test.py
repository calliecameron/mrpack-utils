import requests_mock

from mrpack_utils.commands.list import (
    _make_table,
    run,
)
from mrpack_utils.mods import (
    Env,
    GameVersion,
    Mod,
    Modpack,
    Requirement,
)
from mrpack_utils.output import IncompatibleMods, List, Set, Table


class TestList:
    def test_make_table(self) -> None:
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
            dependencies={"foo": "1", "fabric-loader": "0.16"},
            mods={"abcd": foo, "fedc": bar},
            missing_mods=frozenset(),
            unknown_mods={},
            other_files={},
        )
        table, incompatible = _make_table(
            modpack,
            frozenset([GameVersion("1.19.4"), GameVersion("1.20")]),
        )

        assert table.data == (
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
        )
        assert incompatible == {
            GameVersion("1.19.4"): frozenset(),
            GameVersion("1.20"): frozenset([bar]),
        }

    def test_run(self) -> None:
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
            assert run("testdata/test.mrpack", frozenset([GameVersion("1.20")])) == (
                Table(
                    [
                        [
                            "Name",
                            "Link",
                            "Installed version",
                            "On client",
                            "On server",
                            "Latest game version",
                            "1.19.4",
                            "1.20",
                        ],
                        [
                            "Bar",
                            "https://modrinth.com/mod/bar",
                            "4.5.6",
                            "unknown",
                            "unknown",
                            "1.19.4",
                            "yes",
                            "no",
                        ],
                        [
                            "Foo",
                            "https://modrinth.com/mod/foo",
                            "1.2.3",
                            "required",
                            "optional",
                            "1.20",
                            "no",
                            "yes",
                        ],
                    ],
                ),
                Set(
                    "Mods supposed to be on Modrinth, but not found",
                    {"baz.jar"},
                ),
                Set(
                    "Unknown mods (probably from CurseForge) - must be checked manually",
                    {"bar-1.0.0.jar", "baz-1.0.0.jar", "foo-1.2.3.jar"},
                ),
                List(["Modpack game version: 1.19.4"]),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.19.4",
                    mods={"Foo"},
                ),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.20",
                    mods={"Bar"},
                ),
            )

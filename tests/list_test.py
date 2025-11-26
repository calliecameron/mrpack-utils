import requests_mock

from mrpack.api import Project
from mrpack.commands.list import (
    _empty_row,
    _headers,
    _modpack_data,
    _mods,
    _other_files,
    _unknown_mods,
    run,
)
from mrpack.index import Dependencies, File, Hashes, Index
from mrpack.modpack import Mod, Modpack
from mrpack.mrpack import Override, OverrideMap
from mrpack.output import IncompatibleMods, MissingMods, Table, UnknownDependencies
from mrpack.types import Env, GameVersion, ProjectID, Requirement, Sha1, Sha512
from tests import testdata

# ruff: noqa: S101


class TestList:
    def test_headers(self) -> None:
        assert _headers(set(), dev=False) == [
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
        ]

        assert _headers({GameVersion("1.20"), GameVersion("1.19")}, dev=False) == [
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "1.19",
            "1.20",
        ]

        assert _headers(set(), dev=True) == [
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "License",
            "Modrinth client",
            "Modrinth server",
            "Source",
            "Issues",
        ]

        assert _headers({GameVersion("1.20"), GameVersion("1.19")}, dev=True) == [
            "Name",
            "Link",
            "Installed version",
            "On client",
            "On server",
            "Latest game version",
            "1.19",
            "1.20",
            "License",
            "Modrinth client",
            "Modrinth server",
            "Source",
            "Issues",
        ]

    def test_empty_row(self) -> None:
        assert _empty_row(["a", "b", "c"]) == ["", "", ""]

    def test_modpack_data(self) -> None:
        modpack = Modpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files=set(),
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={"Foo": "1", "fabric-loader": "0.16"},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )
        assert _modpack_data(modpack, _headers({GameVersion("1.19.2")}, dev=False)) == [
            ["modpack: Test Modpack", "", "1", "", "", "", ""],
            ["minecraft", "", "1.19.4", "", "", "", ""],
            ["fabric-loader", "", "0.16", "", "", "", ""],
            ["Foo", "", "1", "", "", "", ""],
        ]

    def test_mods(self) -> None:
        foo = Mod(
            index_entry=File(
                path="a",
                hashes=Hashes(
                    sha1=Sha1("a000000000000000000000000000000000000000"),
                    sha512=Sha512(
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    others={},
                ),
                env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
                downloads=set(),
                size=10,
            ),
            project=Project(
                project_id=ProjectID("a0000000"),
                slug="foo",
                title="Foo",
                env=Env(client=Requirement.OPTIONAL, server=Requirement.OPTIONAL),
                project_license="MIT",
                source_url="example.com",
                issues_url="example2.com",
            ),
            version_number="1.2.3",
            game_versions=frozenset([GameVersion("1.20"), GameVersion("1.19.4")]),
        )
        bar = Mod(
            index_entry=File(
                path="b",
                hashes=Hashes(
                    sha1=Sha1("b000000000000000000000000000000000000000"),
                    sha512=Sha512(
                        "b000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    others={},
                ),
                env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
                downloads=set(),
                size=10,
            ),
            project=Project(
                project_id=ProjectID("b0000000"),
                slug="bar",
                title="Bar",
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                project_license="GPL",
                source_url="",
                issues_url="",
            ),
            version_number="4.5.6",
            game_versions=frozenset([GameVersion("1.19.4"), GameVersion("1.19.2")]),
        )
        modpack = Modpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={"foo": "1", "fabric-loader": "0.16"},
                ),
            ),
            mods=[foo, bar],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )

        mods, incompatible = _mods(
            modpack,
            frozenset([GameVersion("1.19.4"), GameVersion("1.20")]),
            dev=False,
        )
        assert mods == [
            [
                "Bar",
                "https://modrinth.com/mod/bar",
                "4.5.6",
                "required",
                "optional",
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
                "yes",
                "yes",
            ],
        ]
        assert incompatible == {
            GameVersion("1.19.4"): frozenset(),
            GameVersion("1.20"): frozenset([bar]),
        }

        mods, incompatible = _mods(
            modpack,
            frozenset([GameVersion("1.19.4"), GameVersion("1.20")]),
            dev=True,
        )
        assert mods == [
            [
                "Bar",
                "https://modrinth.com/mod/bar",
                "4.5.6",
                "required",
                "optional",
                "1.19.4",
                "yes",
                "no",
                "GPL",
                "required",
                "required",
                "",
                "",
            ],
            [
                "Foo",
                "https://modrinth.com/mod/foo",
                "1.2.3",
                "required",
                "optional",
                "1.20",
                "yes",
                "yes",
                "MIT",
                "optional",
                "optional",
                "example.com",
                "example2.com",
            ],
        ]
        assert incompatible == {
            GameVersion("1.19.4"): frozenset(),
            GameVersion("1.20"): frozenset([bar]),
        }

    def test_unknown_mods(self) -> None:
        modpack = Modpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(
                [
                    Override(
                        path="overrides/mods/Foo",
                        data=b"foo\n",
                    ),
                    Override(
                        path="overrides/mods/bar",
                        data=b"bar\n",
                    ),
                    Override(
                        path="overrides/config/baz",
                        data=b"baz\n",
                    ),
                ],
            ),
        )

        assert _unknown_mods(modpack, {GameVersion("1.19.2")}, dev=False) == [
            [
                "overrides/mods/bar",
                "unknown - probably CurseForge",
                "04a2b3e9",
                "unknown",
                "unknown",
                "unknown",
                "check manually",
            ],
            [
                "overrides/mods/Foo",
                "unknown - probably CurseForge",
                "7e3265a8",
                "unknown",
                "unknown",
                "unknown",
                "check manually",
            ],
        ]

        assert _unknown_mods(modpack, {GameVersion("1.19.2")}, dev=True) == [
            [
                "overrides/mods/bar",
                "unknown - probably CurseForge",
                "04a2b3e9",
                "unknown",
                "unknown",
                "unknown",
                "check manually",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "overrides/mods/Foo",
                "unknown - probably CurseForge",
                "7e3265a8",
                "unknown",
                "unknown",
                "unknown",
                "check manually",
                "",
                "",
                "",
                "",
                "",
            ],
        ]

    def test_other_files(self) -> None:
        modpack = Modpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(
                [
                    Override(
                        path="overrides/config/Foo",
                        data=b"foo\n",
                    ),
                    Override(
                        path="overrides/config/bar",
                        data=b"bar\n",
                    ),
                    Override(
                        path="overrides/mods/baz",
                        data=b"baz\n",
                    ),
                ],
            ),
        )

        assert _other_files(modpack, _headers({GameVersion("1.19.2")}, dev=False)) == [
            ["overrides/config/bar", "non-mod file", "04a2b3e9", "", "", "", ""],
            ["overrides/config/Foo", "non-mod file", "7e3265a8", "", "", "", ""],
        ]

    def test_run_normal(self) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_list_calls(m)
            assert run(
                "testdata/test1.mrpack",
                frozenset([GameVersion("1.20")]),
                dev=False,
            ) == (
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
                            "modpack: Test Modpack",
                            "",
                            "1.1",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "minecraft",
                            "",
                            "1.19.4",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "fabric-loader",
                            "",
                            "0.16",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "foo",
                            "",
                            "1",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "A",
                            "https://modrinth.com/mod/a",
                            "1.2.3",
                            "required",
                            "optional",
                            "1.20",
                            "no",
                            "yes",
                        ],
                        [
                            "B",
                            "https://modrinth.com/mod/b",
                            "4.5.6",
                            "unknown",
                            "unknown",
                            "1.19.4",
                            "yes",
                            "no",
                        ],
                        [
                            "client-overrides/mods/baz-1.0.0.jar",
                            "unknown - probably CurseForge",
                            "a2c6f513",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                        ],
                        [
                            "client-overrides/mods/foo-1.2.3.jar",
                            "unknown - probably CurseForge",
                            "d6902afc",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                        ],
                        [
                            "overrides/mods/foo-1.2.3.jar",
                            "unknown - probably CurseForge",
                            "d6902afc",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                        ],
                        [
                            "server-overrides/mods/bar-1.0.0.jar",
                            "unknown - probably CurseForge",
                            "7123eea6",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                        ],
                        [
                            "overrides/config/foo.txt",
                            "non-mod file",
                            "7e3265a8",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "server-overrides/config/bar.txt",
                            "non-mod file",
                            "04a2b3e9",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                    ],
                ),
                UnknownDependencies(
                    {"foo"},
                ),
                MissingMods(
                    {"c.jar"},
                ),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.19.4",
                    mods={"A"},
                    curseforge_warning=True,
                ),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.20",
                    mods={"B"},
                    curseforge_warning=True,
                ),
            )

    def test_run_dev(self) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_list_calls(m)
            assert run(
                "testdata/test1.mrpack",
                frozenset([GameVersion("1.20")]),
                dev=True,
            ) == (
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
                            "License",
                            "Modrinth client",
                            "Modrinth server",
                            "Source",
                            "Issues",
                        ],
                        [
                            "modpack: Test Modpack",
                            "",
                            "1.1",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "minecraft",
                            "",
                            "1.19.4",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "fabric-loader",
                            "",
                            "0.16",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "foo",
                            "",
                            "1",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "A",
                            "https://modrinth.com/mod/a",
                            "1.2.3",
                            "required",
                            "optional",
                            "1.20",
                            "no",
                            "yes",
                            "MIT",
                            "optional",
                            "required",
                            "S%201",
                            "I%201",
                        ],
                        [
                            "B",
                            "https://modrinth.com/mod/b",
                            "4.5.6",
                            "unknown",
                            "unknown",
                            "1.19.4",
                            "yes",
                            "no",
                            "",
                            "unknown",
                            "unknown",
                            "",
                            "",
                        ],
                        [
                            "client-overrides/mods/baz-1.0.0.jar",
                            "unknown - probably CurseForge",
                            "a2c6f513",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "client-overrides/mods/foo-1.2.3.jar",
                            "unknown - probably CurseForge",
                            "d6902afc",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "overrides/mods/foo-1.2.3.jar",
                            "unknown - probably CurseForge",
                            "d6902afc",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "server-overrides/mods/bar-1.0.0.jar",
                            "unknown - probably CurseForge",
                            "7123eea6",
                            "unknown",
                            "unknown",
                            "unknown",
                            "check manually",
                            "check manually",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "overrides/config/foo.txt",
                            "non-mod file",
                            "7e3265a8",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "server-overrides/config/bar.txt",
                            "non-mod file",
                            "04a2b3e9",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                    ],
                ),
                UnknownDependencies(
                    {"foo"},
                ),
                MissingMods(
                    {"c.jar"},
                ),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.19.4",
                    mods={"A"},
                    curseforge_warning=True,
                ),
                IncompatibleMods(
                    num_mods=2,
                    game_version="1.20",
                    mods={"B"},
                    curseforge_warning=True,
                ),
            )

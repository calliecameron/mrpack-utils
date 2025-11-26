import requests_mock

from mrpack.api import Project
from mrpack.commands.diff import (
    _diff,
    _modpack_data,
    _mods,
    _other_files,
    _unknown_mods,
    run,
)
from mrpack.index import Dependencies, File, Hashes, Index
from mrpack.modpack import Mod, Modpack
from mrpack.mrpack import Override, OverrideMap
from mrpack.output import MissingMods, Table, UnknownDependencies
from mrpack.types import Env, GameVersion, ProjectID, Requirement, Sha1, Sha512
from tests import testdata

# ruff: noqa: S101


class TestDiff:
    def test_diff(self) -> None:
        assert _diff({}, {}) == []
        assert _diff(
            {
                "A": "1",
                "b": "1",
                "C": "1",
                "d": "1",
                "E": "1",
            },
            {
                "A": "1",
                "b": "2",
                "C": "2",
                "f": "1",
                "G": "1",
            },
        ) == [
            ("b", "1", "2"),
            ("C", "1", "2"),
            ("f", "", "1"),
            ("G", "", "1"),
            ("d", "1", ""),
            ("E", "1", ""),
        ]

    def test_modpack_data(self) -> None:
        modpack1 = Modpack(
            index=Index(
                name="Test 1",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.2"),
                    others={"A": "1", "B": "1"},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )
        modpack2 = Modpack(
            index=Index(
                name="Test 2",
                version="2",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.4"),
                    others={"A": "2", "C": "1"},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )

        assert _modpack_data(modpack1, modpack1) == []
        assert _modpack_data(modpack1, modpack2) == [
            ("modpack name", "Test 1", "Test 2"),
            ("modpack version", "1", "2"),
            ("minecraft", "1.19.2", "1.19.4"),
            ("A", "1", "2"),
            ("C", "", "1"),
            ("B", "1", ""),
        ]

    def test_mods(self) -> None:
        mod1_v1 = Mod(
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
                slug="a",
                title="A",
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                project_license="",
                source_url="",
                issues_url="",
            ),
            version_number="1",
            game_versions=frozenset([GameVersion("1.19.2")]),
        )
        mod1_v2 = Mod(
            index_entry=File(
                path="a",
                hashes=Hashes(
                    sha1=Sha1("a100000000000000000000000000000000000000"),
                    sha512=Sha512(
                        "a100000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    others={},
                ),
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                downloads=set(),
                size=10,
            ),
            project=Project(
                project_id=ProjectID("a0000000"),
                slug="a",
                title="A",
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                project_license="",
                source_url="",
                issues_url="",
            ),
            version_number="2",
            game_versions=frozenset([GameVersion("1.19.2")]),
        )
        mod2 = Mod(
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
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                downloads=set(),
                size=10,
            ),
            project=Project(
                project_id=ProjectID("b0000000"),
                slug="b",
                title="B",
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                project_license="",
                source_url="",
                issues_url="",
            ),
            version_number="1",
            game_versions=frozenset([GameVersion("1.19.2")]),
        )
        mod3 = Mod(
            index_entry=File(
                path="c",
                hashes=Hashes(
                    sha1=Sha1("c000000000000000000000000000000000000000"),
                    sha512=Sha512(
                        "c000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    others={},
                ),
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                downloads=set(),
                size=10,
            ),
            project=Project(
                project_id=ProjectID("c0000000"),
                slug="c",
                title="C",
                env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
                project_license="",
                source_url="",
                issues_url="",
            ),
            version_number="1",
            game_versions=frozenset([GameVersion("1.19.2")]),
        )

        modpack1 = Modpack(
            index=Index(
                name="Test",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.2"),
                    others={},
                ),
            ),
            mods=[mod1_v1, mod2],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )
        modpack2 = Modpack(
            index=Index(
                name="Test",
                version="2",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.2"),
                    others={},
                ),
            ),
            mods=[mod1_v2, mod3],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(),
        )

        assert _mods(modpack1, modpack1) == []
        assert _mods(modpack1, modpack2) == [
            ("A", "1", "2"),
            ("C", "", "1"),
            ("B", "1", ""),
        ]

    def test_unknown_mods(self) -> None:
        modpack1 = Modpack(
            index=Index(
                name="Test 1",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.2"),
                    others={},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(
                [
                    Override(
                        path="overrides/mods/A",
                        data=b"foo\n",
                    ),
                    Override(
                        path="overrides/mods/B",
                        data=b"bar\n",
                    ),
                    Override(
                        path="overrides/config/Z",
                        data=b"quux\n",
                    ),
                ],
            ),
        )
        modpack2 = Modpack(
            index=Index(
                name="Test 2",
                version="2",
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
                        path="overrides/mods/A",
                        data=b"foo1\n",
                    ),
                    Override(
                        path="overrides/mods/C",
                        data=b"baz\n",
                    ),
                    Override(
                        path="overrides/config/Z",
                        data=b"quux\n",
                    ),
                ],
            ),
        )

        assert _unknown_mods(modpack1, modpack1) == []
        assert _unknown_mods(modpack1, modpack2) == [
            ("overrides/mods/A", "7e3265a8", "d616f014"),
            ("overrides/mods/C", "", "cc7b39e1"),
            ("overrides/mods/B", "04a2b3e9", ""),
        ]

    def test_other_files(self) -> None:
        modpack1 = Modpack(
            index=Index(
                name="Test 1",
                version="1",
                summary="",
                files=[],
                dependencies=Dependencies(
                    game_version=GameVersion("1.19.2"),
                    others={},
                ),
            ),
            mods=[],
            project_missing_mods=[],
            file_missing_mods=[],
            overrides=OverrideMap(
                [
                    Override(
                        path="overrides/config/A",
                        data=b"foo\n",
                    ),
                    Override(
                        path="overrides/config/B",
                        data=b"bar\n",
                    ),
                    Override(
                        path="overrides/mods/Z",
                        data=b"quux\n",
                    ),
                ],
            ),
        )
        modpack2 = Modpack(
            index=Index(
                name="Test 2",
                version="2",
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
                        path="overrides/config/A",
                        data=b"foo1\n",
                    ),
                    Override(
                        path="overrides/config/C",
                        data=b"baz\n",
                    ),
                    Override(
                        path="overrides/mods/Z",
                        data=b"quux\n",
                    ),
                ],
            ),
        )

        assert _other_files(modpack1, modpack1) == []
        assert _other_files(modpack1, modpack2) == [
            ("overrides/config/A", "7e3265a8", "d616f014"),
            ("overrides/config/C", "", "cc7b39e1"),
            ("overrides/config/B", "04a2b3e9", ""),
        ]

    def test_run(self) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_test2_diff_calls(m)

            assert run("testdata/test1.mrpack", "testdata/test2.mrpack") == (
                Table(
                    [
                        ("Name", "Old", "New"),
                        ("modpack version", "1.1", "1.2"),
                        ("fabric-loader", "0.16", "0.17"),
                        ("foo", "1", "2"),
                        ("A", "1.2.3", "1.2.4"),
                        ("D", "", "1.0.0"),
                        ("B", "4.5.6", ""),
                        ("client-overrides/mods/baz-1.0.0.jar", "a2c6f513", "d59e8961"),
                        ("overrides/mods/foo-1.2.4.jar", "", "99d1bc3b"),
                        ("overrides/mods/foo-1.2.3.jar", "d6902afc", ""),
                        ("server-overrides/config/bar.txt", "04a2b3e9", "a472c297"),
                        ("overrides/config/baz.txt", "", "cc7b39e1"),
                        ("overrides/config/foo.txt", "7e3265a8", ""),
                    ],
                ),
                UnknownDependencies({"foo"}),
                MissingMods({"c.jar"}),
            )

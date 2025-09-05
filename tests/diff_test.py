import requests_mock

from mrpack_utils.commands.diff import (
    _diff,
    _modpack_data,
    _mods,
    _other_files,
    _unknown_mods,
    run,
)
from mrpack_utils.modpack import Mod, Modpack
from mrpack_utils.output import MissingMods, Table, UnknownDependencies
from mrpack_utils.types import Env, GameVersion, ProjectID, Requirement

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
            name="Test 1",
            version="1",
            game_version=GameVersion("1.19.2"),
            dependencies={
                "A": "1",
                "B": "1",
            },
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={},
            other_files={},
        )
        modpack2 = Modpack(
            name="Test 2",
            version="2",
            game_version=GameVersion("1.19.4"),
            dependencies={
                "A": "2",
                "C": "1",
            },
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={},
            other_files={},
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
        mod1_1 = Mod(
            name="A",
            slug="A",
            version="1",
            original_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            mod_license="",
            source_url="",
            issues_url="",
            game_versions={GameVersion("1.19.2")},
        )
        mod1_2 = Mod(
            name="A",
            slug="A",
            version="2",
            original_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            mod_license="",
            source_url="",
            issues_url="",
            game_versions={GameVersion("1.19.2")},
        )
        mod2 = Mod(
            name="B",
            slug="B",
            version="1",
            original_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            mod_license="",
            source_url="",
            issues_url="",
            game_versions={GameVersion("1.19.2")},
        )
        mod3 = Mod(
            name="C",
            slug="C",
            version="1",
            original_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            overridden_env=Env(client=Requirement.REQUIRED, server=Requirement.REQUIRED),
            mod_license="",
            source_url="",
            issues_url="",
            game_versions={GameVersion("1.19.2")},
        )

        modpack1 = Modpack(
            name="Test",
            version="1",
            game_version=GameVersion("1.19.2"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={ProjectID("A0000000"): mod1_1, ProjectID("B0000000"): mod2},
            missing_mods=set(),
            unknown_mods={},
            other_files={},
        )
        modpack2 = Modpack(
            name="Test",
            version="2",
            game_version=GameVersion("1.19.2"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={ProjectID("A0000000"): mod1_2, ProjectID("C0000000"): mod3},
            missing_mods=set(),
            unknown_mods={},
            other_files={},
        )

        assert _mods(modpack1, modpack1) == []
        assert _mods(modpack1, modpack2) == [
            ("A", "1", "2"),
            ("C", "", "1"),
            ("B", "1", ""),
        ]

    def test_unknown_mods(self) -> None:
        modpack1 = Modpack(
            name="Test 1",
            version="1",
            game_version=GameVersion("1.19.2"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={
                "A": "1",
                "B": "1",
            },
            other_files={},
        )
        modpack2 = Modpack(
            name="Test 2",
            version="2",
            game_version=GameVersion("1.19.4"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={
                "A": "2",
                "C": "1",
            },
            other_files={},
        )

        assert _unknown_mods(modpack1, modpack1) == []
        assert _unknown_mods(modpack1, modpack2) == [
            ("A", "1", "2"),
            ("C", "", "1"),
            ("B", "1", ""),
        ]

    def test_other_files(self) -> None:
        modpack1 = Modpack(
            name="Test 1",
            version="1",
            game_version=GameVersion("1.19.2"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={},
            other_files={
                "A": "1",
                "B": "1",
            },
        )
        modpack2 = Modpack(
            name="Test 2",
            version="2",
            game_version=GameVersion("1.19.4"),
            dependencies={},
            loaders=set(),
            unknown_dependencies=set(),
            mods={},
            missing_mods=set(),
            unknown_mods={},
            other_files={
                "A": "2",
                "C": "1",
            },
        )

        assert _other_files(modpack1, modpack1) == []
        assert _other_files(modpack1, modpack2) == [
            ("A", "1", "2"),
            ("C", "", "1"),
            ("B", "1", ""),
        ]

    def test_run(self) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "baz00000",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "cccc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                    "abcd2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "baz00000",
                        "version_number": "1.2.4",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "cccc2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                    "fedc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "quux0000",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                    "bbbb0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "blah0000",
                        "version_number": "1.0.0",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "bbbb0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["baz00000", "blah0000", "quux0000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz00000",
                        "title": "Foo",
                        "slug": "foo",
                        "client_side": "optional",
                        "server_side": "required",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                    {
                        "id": "blah0000",
                        "title": "Quux",
                        "slug": "quux",
                    },
                    {
                        "id": "quux0000",
                        "title": "Bar",
                        "slug": "bar",
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/baz00000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "AA000000",
                        "project_id": "baz00000",
                        "loaders": ["fabric"],
                        "game_versions": ["1.19.2"],
                    },
                    {
                        "id": "BB000000",
                        "project_id": "baz00000",
                        "loaders": ["fabric", "minecraft"],
                        "game_versions": ["1.20"],
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/blah0000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "CC000000",
                        "project_id": "blah0000",
                        "loaders": ["minecraft"],
                        "game_versions": ["1.19.4"],
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/quux0000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "DD000000",
                        "project_id": "quux0000",
                        "loaders": ["fabric"],
                        "game_versions": ["1.19.4"],
                    },
                ],
            )

            assert run("testdata/test1.mrpack", "testdata/test2.mrpack") == (
                Table(
                    [
                        ("Name", "Old", "New"),
                        ("modpack version", "1.1", "1.2"),
                        ("fabric-loader", "0.16", "0.17"),
                        ("foo", "1", "2"),
                        ("Foo", "1.2.3", "1.2.4"),
                        ("Quux", "", "1.0.0"),
                        ("Bar", "4.5.6", ""),
                        ("client-overrides/mods/baz-1.0.0.jar", "a2c6f513", "d59e8961"),
                        ("overrides/mods/foo-1.2.4.jar", "", "99d1bc3b"),
                        ("overrides/mods/foo-1.2.3.jar", "d6902afc", ""),
                        ("server-overrides/config/bar.txt", "04a2b3e9", "a472c297"),
                        ("overrides/config/baz.txt", "", "cc7b39e1"),
                        ("overrides/config/foo.txt", "7e3265a8", ""),
                    ],
                ),
                UnknownDependencies({"foo"}),
                MissingMods({"baz.jar"}),
            )

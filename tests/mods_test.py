import requests_mock
from frozendict import frozendict

from mrpack_utils.mods import Mod, Modpack
from mrpack_utils.mrpack import File, Hashes, Index, Mrpack, Override
from mrpack_utils.types import Env, GameVersion, Requirement, Sha1, Sha512

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
        mrpack1 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="1",
                summary="",
                files={
                    File(
                        path="mods/foo.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/bar.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "fedc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/baz.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "dcba0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                },
                dependencies=frozendict(
                    {
                        "minecraft": "1.19.4",
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
        mrpack2 = Mrpack(
            index=Index(
                name="Test Modpack",
                version="2",
                summary="",
                files={
                    File(
                        path="mods/foo.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/bar.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "bbbb0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                    File(
                        path="mods/baz.jar",
                        hashes=Hashes(
                            sha1=Sha1("0000000000000000000000000000000000000000"),
                            sha512=Sha512(
                                "dcba0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            ),
                            others={},
                        ),
                        env=None,
                        downloads=set(),
                        size=10,
                    ),
                },
                dependencies=frozendict(
                    {
                        "minecraft": "1.19.4",
                        "foo": "2",
                        "fabric-loader": "3",
                        "forge": "1",
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
                        "project_id": "quux0000",
                        "version_number": "4.5.7",
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
                'https://api.modrinth.com/v2/projects?ids=["baz00000", "quux0000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz00000",
                        "title": "Foo",
                        "slug": "foo",
                    },
                    {
                        "id": "quux0000",
                        "title": "Bar",
                        "slug": "bar",
                        "client_side": "optional",
                        "server_side": "optional",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/baz00000/version?loaders=["fabric", "forge", '
                '"minecraft"]',
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
                'https://api.modrinth.com/v2/project/quux0000/version?loaders=["fabric", "forge", '
                '"minecraft"]',
                complete_qs=True,
                json=[
                    {
                        "id": "CC000000",
                        "project_id": "quux0000",
                        "loaders": ["minecraft"],
                        "game_versions": ["1.19.4"],
                    },
                    {
                        "id": "DD000000",
                        "project_id": "quux0000",
                        "loaders": ["forge"],
                        "game_versions": ["1.20"],
                    },
                ],
            )
            modpacks = Modpack._load(mrpack1, mrpack2)  # noqa: SLF001

        assert len(modpacks) == 2  # noqa: PLR2004

        modpack = modpacks[0]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "1"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"foo": "1", "fabric-loader": "2"})
        assert modpack.loaders == frozenset({"minecraft", "fabric"})
        assert modpack.unknown_dependencies == frozenset({"foo"})

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
        assert modpack.unknown_mods == frozendict({"overrides/mods/unknown.jar": "7e3265a8"})
        assert modpack.other_files == frozendict({"overrides/config/foo.txt": "04a2b3e9"})

        modpack = modpacks[1]
        assert modpack.name == "Test Modpack"
        assert modpack.version == "2"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"foo": "2", "fabric-loader": "3", "forge": "1"})
        assert modpack.loaders == frozenset({"minecraft", "fabric", "forge"})
        assert modpack.unknown_dependencies == frozenset({"foo"})

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
        assert mods[0].game_versions == frozenset([GameVersion("1.19.4"), GameVersion("1.20")])
        assert mods[0].latest_game_version == GameVersion("1.20")

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
        assert modpack.unknown_mods == frozendict({"overrides/mods/unknown.jar": "7e3265a8"})
        assert modpack.other_files == frozendict({"overrides/config/foo.txt": "04a2b3e9"})

    def test_from_files(self) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "foo00000",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                    "fedc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
                        "project_id": "bar00000",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["bar00000", "foo00000"]',
                complete_qs=True,
                json=[
                    {
                        "id": "foo00000",
                        "title": "Foo",
                        "slug": "foo",
                    },
                    {
                        "id": "bar00000",
                        "title": "Bar",
                        "slug": "bar",
                        "client_side": "optional",
                        "server_side": "optional",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/foo00000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "AA000000",
                        "project_id": "foo00000",
                        "loaders": ["fabric"],
                        "game_versions": ["1.19.2"],
                    },
                    {
                        "id": "BB000000",
                        "project_id": "foo00000",
                        "loaders": ["fabric", "minecraft"],
                        "game_versions": ["1.20"],
                    },
                ],
            )
            m.get(
                'https://api.modrinth.com/v2/project/bar00000/version?loaders=["fabric", "minecraft"]',  # noqa: E501
                complete_qs=True,
                json=[
                    {
                        "id": "CC000000",
                        "project_id": "bar00000",
                        "loaders": ["minecraft"],
                        "game_versions": ["1.19.4"],
                    },
                ],
            )
            (modpack,) = Modpack.from_files("testdata/test1.mrpack")

        assert modpack.name == "Test Modpack"
        assert modpack.version == "1.1"
        assert modpack.game_version == GameVersion("1.19.4")
        assert modpack.dependencies == frozendict({"fabric-loader": "0.16", "foo": "1"})
        assert modpack.loaders == frozenset({"minecraft", "fabric"})
        assert modpack.unknown_dependencies == frozenset({"foo"})

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

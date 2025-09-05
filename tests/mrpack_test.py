from pathlib import PurePath

import pytest
from frozendict import frozendict

from mrpack_utils.index import Dependencies, File, Hashes, Index
from mrpack_utils.mrpack import Mrpack, MrpackError, Override
from mrpack_utils.types import Env, GameVersion, Requirement, Sha1, Sha512

# ruff: noqa: PT011, S101


class TestOverride:
    def test_valid(self) -> None:
        o1 = Override(
            path="a/b",
            data=b"foo\n",
        )

        assert o1.path == PurePath("a", "b")
        assert o1.data == b"foo\n"
        assert o1.hash == Sha512(
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470"
            "ddc2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
        )
        assert o1.is_text
        assert o1.text() == "foo\n"

        o2 = Override(
            path="a/b",
            data=b"foo\0\n",
        )

        assert o2.path == PurePath("a", "b")
        assert o2.data == b"foo\0\n"
        assert o2.hash == Sha512(
            "7c8601a05c7dee925d3dee3a2c663a4ebd3683053207aaff04c8bb58aac1c3c6"
            "64451c82a7e6799c983e1470f6ce1b6e8d96b358371923184b8bdad23a8a94e4",
        )
        assert not o2.is_text
        with pytest.raises(ValueError):
            o2.text()

        assert o1 == o1  # noqa: PLR0124
        assert o1 != o2
        with pytest.raises(NotImplementedError):
            assert o1 == "foo"

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Override(
                path="a/../b",
                data=b"foo\n",
            )


class TestMrpack:
    def test_init(self) -> None:
        f1 = File(
            path="a/b",
            hashes=Hashes(
                sha1=Sha1("f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"),
                sha512=Sha512(
                    "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470dd"
                    "c2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"foo", "bar"},
            size=10,
        )
        f2 = File(
            path="c/d",
            hashes=Hashes(
                sha1=Sha1("a1d2d2f924e986ac86fdf7b36c94bcdf32beec15"),
                sha512=Sha512(
                    "acf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470dd"
                    "c2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.UNSUPPORTED),
            downloads={"foo", "bar"},
            size=20,
        )
        i = Index(
            name="Test Modpack",
            version="1.0",
            summary="foo",
            files={f1, f2},
            dependencies=Dependencies(
                game_version=GameVersion("1.20.1"),
                others={"foo": "2"},
            ),
        )

        o1 = Override(path="overrides/a", data=b"foo\n")
        o2 = Override(path="overrides/b", data=b"bar\n")
        o3 = Override(path="overrides/a", data=b"baz\n")

        co1 = Override(path="client-overrides/a", data=b"foo\n")
        co2 = Override(path="client-overrides/b", data=b"bar\n")
        co3 = Override(path="client-overrides/a", data=b"baz\n")

        so1 = Override(path="server-overrides/a", data=b"foo\n")
        so2 = Override(path="server-overrides/b", data=b"bar\n")
        so3 = Override(path="server-overrides/a", data=b"baz\n")

        m = Mrpack(
            index=i,
            overrides={o1, o2},
            client_overrides={co1, co2},
            server_overrides={so1, so2},
        )

        assert m.index == i
        assert m.overrides == frozendict(
            {
                PurePath("overrides", "a"): o1,
                PurePath("overrides", "b"): o2,
            },
        )
        assert m.client_overrides == frozendict(
            {
                PurePath("client-overrides", "a"): co1,
                PurePath("client-overrides", "b"): co2,
            },
        )
        assert m.server_overrides == frozendict(
            {
                PurePath("server-overrides", "a"): so1,
                PurePath("server-overrides", "b"): so2,
            },
        )

        # Bad override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides={o1, co2},
                client_overrides=set(),
                server_overrides=set(),
            )
        # Duplicate override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides={o1, o3},
                client_overrides=set(),
                server_overrides=set(),
            )
        # Bad client override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides=set(),
                client_overrides={co1, o2},
                server_overrides=set(),
            )
        # Duplicate client override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides=set(),
                client_overrides={co1, co3},
                server_overrides=set(),
            )
        # Bad server override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides=set(),
                client_overrides=set(),
                server_overrides={so1, o2},
            )
        # Duplicate server override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides=set(),
                client_overrides=set(),
                server_overrides={so1, so3},
            )

    def test_from_file_valid(self) -> None:
        m = Mrpack.from_file("testdata/test1.mrpack")

        f1 = File(
            path="mods/foo.jar",
            hashes=Hashes(
                sha1=Sha1("0000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "abcd00000000000000000000000000000000000000000000000000000000000000"
                    "00000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"abcd"},
            size=10,
        )
        f2 = File(
            path="mods/bar.jar",
            hashes=Hashes(
                sha1=Sha1("0000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "fedc00000000000000000000000000000000000000000000000000000000000000"
                    "00000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads={"fedc"},
            size=20,
        )
        f3 = File(
            path="mods/baz.jar",
            hashes=Hashes(
                sha1=Sha1("0000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "dcba00000000000000000000000000000000000000000000000000000000000000"
                    "00000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads={"dcba"},
            size=30,
        )
        i = Index(
            name="Test Modpack",
            version="1.1",
            summary="First test modpack",
            files={f1, f2, f3},
            dependencies=Dependencies(
                game_version=GameVersion("1.19.4"),
                others={
                    "fabric-loader": "0.16",
                    "foo": "1",
                },
            ),
        )

        o1 = Override(path="overrides/config/foo.txt", data=b"foo\n")
        o2 = Override(path="overrides/mods/foo-1.2.3.jar", data=b"foo-1.2.3\n")

        co1 = Override(path="client-overrides/mods/baz-1.0.0.jar", data=b"baz-1.0.0\n")
        co2 = Override(path="client-overrides/mods/foo-1.2.3.jar", data=b"foo-1.2.3\n")

        so1 = Override(path="server-overrides/config/bar.txt", data=b"bar\n")
        so2 = Override(path="server-overrides/mods/bar-1.0.0.jar", data=b"bar-1.0.0\n")

        assert m.index == i
        assert m.overrides == frozendict(
            {
                PurePath("overrides", "config", "foo.txt"): o1,
                PurePath("overrides", "mods", "foo-1.2.3.jar"): o2,
            },
        )
        assert m.client_overrides == frozendict(
            {
                PurePath("client-overrides", "mods", "baz-1.0.0.jar"): co1,
                PurePath("client-overrides", "mods", "foo-1.2.3.jar"): co2,
            },
        )
        assert m.server_overrides == frozendict(
            {
                PurePath("server-overrides", "config", "bar.txt"): so1,
                PurePath("server-overrides", "mods", "bar-1.0.0.jar"): so2,
            },
        )

    def test_from_file_invalid(self) -> None:
        # Not a zip file
        with pytest.raises(MrpackError):
            Mrpack.from_file("testdata/modrinth.index.json")
        # File in invalid location
        with pytest.raises(MrpackError):
            Mrpack.from_file("testdata/bad1.mrpack")

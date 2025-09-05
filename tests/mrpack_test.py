from pathlib import PurePath

import pytest
from frozendict import frozendict

from mrpack.index import Dependencies, File, Hashes, Index
from mrpack.mrpack import Mrpack, MrpackError, Override, OverrideType
from mrpack.types import Env, GameVersion, Requirement, Sha1, Sha512

# ruff: noqa: PT011, S101


class TestOverrideType:
    def test_override_type(self) -> None:
        assert OverrideType.from_prefix("overrides") == OverrideType.GENERAL
        assert OverrideType.from_prefix("client-overrides") == OverrideType.CLIENT
        assert OverrideType.from_prefix("server-overrides") == OverrideType.SERVER
        with pytest.raises(ValueError):
            OverrideType.from_prefix("foo")


class TestOverride:
    def test_valid(self) -> None:
        o1 = Override(
            path="overrides/a",
            data=b"foo\n",
        )

        assert o1.path == PurePath("overrides", "a")
        assert o1.type == OverrideType.GENERAL
        assert o1.data == b"foo\n"
        assert o1.hash == Sha512(
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470"
            "ddc2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
        )
        assert o1.is_text
        assert o1.text() == "foo\n"

        o2 = Override(
            path="client-overrides/a",
            data=b"foo\0\n",
        )

        assert o2.path == PurePath("client-overrides", "a")
        assert o2.type == OverrideType.CLIENT
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
        # Invalid path
        with pytest.raises(ValueError):
            Override(
                path="overrides/../a",
                data=b"foo\n",
            )
        # Path too short
        with pytest.raises(ValueError):
            Override(
                path="a",
                data=b"foo\n",
            )
        # Not in a prefix
        with pytest.raises(ValueError):
            Override(
                path="a/b",
                data=b"foo\n",
            )


class TestMrpack:
    def test_init(self) -> None:
        f1 = File(
            path="mods/a",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"A1", "A2"},
            size=10,
        )
        f2 = File(
            path="mods/b",
            hashes=Hashes(
                sha1=Sha1("b000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "b000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.UNSUPPORTED),
            downloads={"B1", "B2"},
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
        o2 = Override(path="client-overrides/a", data=b"bar\n")
        o3 = Override(path="overrides/a", data=b"baz\n")

        m = Mrpack(
            index=i,
            overrides={o1, o2},
        )

        assert m.index == i
        assert m.overrides == frozendict(
            {
                PurePath("overrides", "a"): o1,
                PurePath("client-overrides", "a"): o2,
            },
        )

        # Duplicate override path
        with pytest.raises(ValueError):
            Mrpack(
                index=i,
                overrides={o1, o3},
            )

    def test_from_file_valid(self) -> None:
        m = Mrpack.from_file("testdata/test1.mrpack")

        f1 = File(
            path="mods/a.jar",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"A"},
            size=10,
        )
        f2 = File(
            path="mods/b.jar",
            hashes=Hashes(
                sha1=Sha1("b000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "b000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads={"B"},
            size=20,
        )
        f3 = File(
            path="mods/c.jar",
            hashes=Hashes(
                sha1=Sha1("c000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "c000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads={"C"},
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
        o3 = Override(path="client-overrides/mods/baz-1.0.0.jar", data=b"baz-1.0.0\n")
        o4 = Override(path="client-overrides/mods/foo-1.2.3.jar", data=b"foo-1.2.3\n")
        o5 = Override(path="server-overrides/config/bar.txt", data=b"bar\n")
        o6 = Override(path="server-overrides/mods/bar-1.0.0.jar", data=b"bar-1.0.0\n")

        assert m.index == i
        assert m.overrides == frozendict(
            {
                PurePath("overrides", "config", "foo.txt"): o1,
                PurePath("overrides", "mods", "foo-1.2.3.jar"): o2,
                PurePath("client-overrides", "mods", "baz-1.0.0.jar"): o3,
                PurePath("client-overrides", "mods", "foo-1.2.3.jar"): o4,
                PurePath("server-overrides", "config", "bar.txt"): o5,
                PurePath("server-overrides", "mods", "bar-1.0.0.jar"): o6,
            },
        )

    def test_from_file_invalid(self) -> None:
        # Not a zip file
        with pytest.raises(MrpackError):
            Mrpack.from_file("testdata/modrinth.index.json")
        # Override in invalid location
        with pytest.raises(MrpackError):
            Mrpack.from_file("testdata/bad1.mrpack")

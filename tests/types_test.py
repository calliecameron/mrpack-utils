from pathlib import PurePath

import jsonschema
import pytest

from mrpack.types import (
    Env,
    GameVersion,
    ProjectID,
    Requirement,
    Sha1,
    Sha512,
    VersionID,
    validated_path,
)

# ruff: noqa: PT011,S101


class TestValidatedPath:
    def test_validated_path(self) -> None:
        assert validated_path("a") == PurePath("a")
        assert validated_path("a/b") == PurePath("a", "b")
        assert validated_path("a/./b") == PurePath("a", "b")
        with pytest.raises(ValueError):
            validated_path("")
        with pytest.raises(ValueError):
            validated_path("/a")
        with pytest.raises(ValueError):
            validated_path("C:/a")
        with pytest.raises(ValueError):
            validated_path("C:\\a")
        with pytest.raises(ValueError):
            validated_path("//a")
        with pytest.raises(ValueError):
            validated_path("a/../b")


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

    def test_load_multiple(self) -> None:
        assert GameVersion.load_multiple(
            ["1.19", "1.20-dev", "1.18.4", "1.19", "foo"],
        ) == frozenset(
            [GameVersion("1.19"), GameVersion("1.18.4")],
        )


class TestRequirement:
    def test_from_str(self) -> None:
        assert Requirement.from_str("") == Requirement.UNKNOWN
        assert Requirement.from_str("unknown") == Requirement.UNKNOWN
        assert Requirement.from_str("required") == Requirement.REQUIRED
        assert Requirement.from_str("optional") == Requirement.OPTIONAL
        assert Requirement.from_str("unsupported") == Requirement.UNSUPPORTED
        with pytest.raises(ValueError):
            Requirement.from_str("foo")

    def test_from_json(self) -> None:
        with pytest.raises(jsonschema.ValidationError):
            Requirement.from_json("")
        with pytest.raises(jsonschema.ValidationError):
            Requirement.from_json("unknown")
        assert Requirement.from_json("required") == Requirement.REQUIRED
        assert Requirement.from_json("optional") == Requirement.OPTIONAL
        assert Requirement.from_json("unsupported") == Requirement.UNSUPPORTED
        with pytest.raises(jsonschema.ValidationError):
            Requirement.from_json("foo")


class TestEnv:
    def test_from_json(self) -> None:
        e = Env.from_json({"client": "required", "server": "optional"})
        assert e.client == Requirement.REQUIRED
        assert e.server == Requirement.OPTIONAL

        with pytest.raises(jsonschema.ValidationError):
            Env.from_json({"client": "required"})
        with pytest.raises(jsonschema.ValidationError):
            Env.from_json({"client": "required", "server": "foo"})
        with pytest.raises(jsonschema.ValidationError):
            Env.from_json({"client": "required", "server": "optional", "foo": "bar"})

    def test_unknown(self) -> None:
        e = Env.unknown()
        assert e.client == Requirement.UNKNOWN
        assert e.server == Requirement.UNKNOWN


class TestSha1:
    def test_valid(self) -> None:
        h1 = Sha1("f1d2d2f924e986ac86fdf7b36c94bcdf32beec15")
        h2 = Sha1("F1d2d2f924e986ac86fdf7b36c94bcdf32beec15")
        h3 = Sha1.from_data(b"foo\n")

        assert str(h1) == "f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"
        assert str(h2) == "f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"
        assert str(h3) == "f1d2d2f924e986ac86fdf7b36c94bcdf32beec15"
        assert h1 == h2
        assert h1 == h3
        assert h2 == h3
        assert hash(h1) == hash(h2)
        assert hash(h1) == hash(h3)
        assert hash(h2) == hash(h3)
        assert h1 < Sha1("ff00000000000000000000000000000000000000")

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Sha1("foo")
        with pytest.raises(NotImplementedError):
            assert Sha1.from_data(b"foo\n") == b"foo\n"
        with pytest.raises(NotImplementedError):
            assert Sha1.from_data(b"foo\n") < b"foo\n"


class TestSha512:
    def test_valid(self) -> None:
        h1 = Sha512(
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470dd"
            "c2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
        )
        h2 = Sha512(
            "0Cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470dd"
            "c2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6",
        )
        h3 = Sha512.from_data(b"foo\n")

        assert str(h1) == (
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470"
            "ddc2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6"
        )
        assert str(h2) == (
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470"
            "ddc2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6"
        )
        assert str(h3) == (
            "0cf9180a764aba863a67b6d72f0918bc131c6772642cb2dce5a34f0a702f9470"
            "ddc2bf125c12198b1995c233c34b4afd346c54a2334c350a948a51b6e8b4e6b6"
        )
        assert h1 == h2
        assert h1 == h3
        assert h2 == h3
        assert hash(h1) == hash(h2)
        assert hash(h1) == hash(h3)
        assert hash(h2) == hash(h3)
        assert h1 < Sha512(
            "ff0000000000000000000000000000000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000000",
        )

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Sha512("foo")
        with pytest.raises(NotImplementedError):
            assert Sha512.from_data(b"foo\n") == b"foo\n"
        with pytest.raises(NotImplementedError):
            assert Sha512.from_data(b"foo\n") < b"foo\n"


class TestID:
    def test_valid(self) -> None:
        p1 = ProjectID("foobarba")
        assert str(p1) == "foobarba"

        p2 = ProjectID("zquuxyay")
        assert str(p2) == "zquuxyay"

        assert p1 == p1  # noqa: PLR0124
        assert p1 != p2
        with pytest.raises(NotImplementedError):
            assert p1 == "foobarba"

        assert p1 < p2
        with pytest.raises(NotImplementedError):
            assert p1 < "foo"

        v1 = VersionID("foobarba")
        assert str(v1) == "foobarba"

        v2 = VersionID("zquuxyay")
        assert str(v2) == "zquuxyay"

        assert v1 == v1  # noqa: PLR0124
        assert v1 != v2
        with pytest.raises(NotImplementedError):
            assert v1 == "foobarba"

        assert v1 < v2
        with pytest.raises(NotImplementedError):
            assert v1 < "foo"

        with pytest.raises(NotImplementedError):
            assert p1 == v1
        with pytest.raises(NotImplementedError):
            assert p1 < v1

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            ProjectID("foo")
        with pytest.raises(ValueError):
            VersionID("foo")

import pytest

from mrcheck import GameVersion, Mod


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

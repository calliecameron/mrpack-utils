from mrpack_utils.output import IncompatibleMods, List, Set, Table


class TestList:
    def test_render(self) -> None:
        assert List([]).render() == ""
        assert List(["a", "c", "b"]).render() == "a\nc\nb"


class TestSet:
    def test_render(self) -> None:
        assert Set("foo", frozenset([])).render() == ""
        assert (
            Set("foo", frozenset(["a", "c", "b"])).render()
            == """foo:
  a
  b
  c"""
        )


class TestTable:
    def test_render(self) -> None:
        assert (
            Table(
                [
                    ["A", "B"],
                ],
            ).render()
            == """| A   | B   |
|-----|-----|"""
        )

        assert (
            Table(
                [
                    ["A", "B"],
                    ["a", "b"],
                    ["c", "d"],
                ],
            ).render()
            == """| A   | B   |
|-----|-----|
| a   | b   |
| c   | d   |"""
        )

    def test_render_csv(self) -> None:
        assert (
            Table(
                [
                    ["A", "B"],
                ],
            ).render_csv()
            == "A,B"
        )

        assert (
            Table(
                [
                    ["A", "B"],
                    ["a", "b"],
                    ["c", "d"],
                ],
            ).render_csv()
            == """A,B
a,b
c,d"""
        )


class TestIncompatibleMods:
    def test_render(self) -> None:
        assert (
            IncompatibleMods(
                num_mods=10,
                game_version="1.19.2",
                mods=frozenset(),
            ).render()
            == """For version 1.19.2:
  All mods are compatible with this version"""
        )

        assert (
            IncompatibleMods(
                num_mods=10,
                game_version="1.19.2",
                mods=frozenset({"B", "A"}),
            ).render()
            == """For version 1.19.2:
  2 out of 10 mods are incompatible with this version:
    A
    B"""
        )

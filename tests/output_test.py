from mrpack_utils.output import IncompatibleMods, List, Set, Table, render, render_csv

# ruff: noqa: E741


class TestList:
    def test_render(self) -> None:
        l = List([])
        assert l.data == ()
        assert l.render() == ""

        l = List(["a", "c", "b"])
        assert l.data == ("a", "c", "b")
        assert l.render() == "a\nc\nb"


class TestSet:
    def test_render(self) -> None:
        s = Set("foo", set())
        assert s.title == "foo"
        assert s.data == frozenset()
        assert s.render() == ""

        s = Set("foo", {"a", "c", "b"})
        assert s.title == "foo"
        assert s.data == frozenset(["a", "b", "c"])
        assert (
            s.render()
            == """foo:
  a
  b
  c"""
        )


class TestTable:
    def test_render(self) -> None:
        t = Table(
            [
                ["A", "B"],
            ],
        )
        assert t.data == (("A", "B"),)
        assert (
            t.render()
            == """| A   | B   |
|-----|-----|"""
        )
        assert t.render_csv() == "A,B"

        t = Table(
            [
                ["A", "B"],
                ["a", "b"],
                ["c", "d"],
            ],
        )
        assert t.data == (
            ("A", "B"),
            ("a", "b"),
            ("c", "d"),
        )
        assert (
            t.render()
            == """| A   | B   |
|-----|-----|
| a   | b   |
| c   | d   |"""
        )
        assert (
            t.render_csv()
            == """A,B
a,b
c,d"""
        )


class TestIncompatibleMods:
    def test_render(self) -> None:
        i = IncompatibleMods(
            num_mods=10,
            game_version="1.19.2",
            mods=set(),
        )
        assert i.num_mods == 10  # noqa: PLR2004
        assert i.game_version == "1.19.2"
        assert i.mods == frozenset()
        assert (
            i.render()
            == """For version 1.19.2:
  All Modrinth mods are compatible with this version (CurseForge mods must be checked manually)"""
        )

        i = IncompatibleMods(
            num_mods=10,
            game_version="1.19.2",
            mods={"B", "A"},
        )
        assert i.num_mods == 10  # noqa: PLR2004
        assert i.game_version == "1.19.2"
        assert i.mods == frozenset(["A", "B"])
        assert (
            i.render()
            == """For version 1.19.2:
  2 out of 10 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    A
    B"""  # noqa: E501
        )


class TestRender:
    def test_render(self) -> None:
        data = [
            List(["a", "c", "b"]),
            IncompatibleMods(
                num_mods=10,
                game_version="1.19.2",
                mods={"B", "A"},
            ),
            Set("foo", set()),
            Set("foo", {"a", "c", "b"}),
            Table(
                [
                    ["A", "B"],
                    ["a", "b"],
                    ["c", "d"],
                ],
            ),
        ]

        assert render([]) == ""
        assert (
            render(data)
            == """a
c
b

For version 1.19.2:
  2 out of 10 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    A
    B

foo:
  a
  b
  c

| A   | B   |
|-----|-----|
| a   | b   |
| c   | d   |"""  # noqa: E501
        )

        assert render_csv([]) == ""
        assert (
            render_csv(data)
            == """A,B
a,b
c,d"""
        )

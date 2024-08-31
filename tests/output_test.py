from mrpack_utils.output import IncompatibleMods, MissingMods, Table, render, render_csv

# ruff: noqa: E741


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


class TestMissingMods:
    def test_render(self) -> None:
        m = MissingMods(set())
        assert m.mods == frozenset()
        assert m.render() == ""

        m = MissingMods({"a", "c", "b"})
        assert m.mods == frozenset(["a", "b", "c"])
        assert (
            m.render()
            == """Mods supposed to be on Modrinth, but not found:
  a
  b
  c"""
        )


class TestIncompatibleMods:
    def test_render_normal(self) -> None:
        i = IncompatibleMods(
            num_mods=10,
            game_version="1.19.2",
            mods=set(),
            curseforge_warning=False,
        )
        assert i.num_mods == 10  # noqa: PLR2004
        assert i.game_version == "1.19.2"
        assert i.mods == frozenset()
        assert (
            i.render()
            == """For version 1.19.2:
  All mods are compatible with this version"""
        )

        i = IncompatibleMods(
            num_mods=10,
            game_version="1.19.2",
            mods={"B", "A"},
            curseforge_warning=False,
        )
        assert i.num_mods == 10  # noqa: PLR2004
        assert i.game_version == "1.19.2"
        assert i.mods == frozenset(["A", "B"])
        assert (
            i.render()
            == """For version 1.19.2:
  2 out of 10 mods are incompatible with this version:
    A
    B"""
        )

    def test_render_warning(self) -> None:
        i = IncompatibleMods(
            num_mods=10,
            game_version="1.19.2",
            mods=set(),
            curseforge_warning=True,
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
            curseforge_warning=True,
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
            IncompatibleMods(
                num_mods=10,
                game_version="1.19.2",
                mods={"B", "A"},
                curseforge_warning=False,
            ),
            MissingMods(set()),
            MissingMods({"a", "c", "b"}),
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
            == """For version 1.19.2:
  2 out of 10 mods are incompatible with this version:
    A
    B

Mods supposed to be on Modrinth, but not found:
  a
  b
  c

| A   | B   |
|-----|-----|
| a   | b   |
| c   | d   |"""
        )

        assert render_csv([]) == ""
        assert (
            render_csv(data)
            == """A,B
a,b
c,d"""
        )

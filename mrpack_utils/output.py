import csv
import io
from abc import ABC, abstractmethod
from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

import tabulate


class Element(ABC):
    @abstractmethod
    def render(self) -> str:  # pragma nocover
        raise NotImplementedError


@dataclass(frozen=True)
class List(Element):
    data: Sequence[str]

    def render(self) -> str:
        return "\n".join(self.data)


@dataclass(frozen=True)
class Set(Element):
    title: str
    data: AbstractSet[str]

    def render(self) -> str:
        out = []
        if self.data:
            out.append(f"{self.title}:")
            out += ["  " + item for item in sorted(self.data, key=lambda i: i.lower())]
        return "\n".join(out)


@dataclass(frozen=True)
class Table(Element):
    data: Sequence[Sequence[str]]

    def render(self) -> str:
        return tabulate.tabulate(self.data, headers="firstrow", tablefmt="github")

    def render_csv(self) -> str:
        with io.StringIO() as f:
            csv.writer(f, lineterminator="\n").writerows(self.data)
            return f.getvalue().rstrip()


@dataclass(frozen=True, kw_only=True)
class IncompatibleMods(Element):
    num_mods: int
    game_version: str
    mods: AbstractSet[str]

    def render(self) -> str:
        out = []
        out.append(f"For version {self.game_version}:")
        if self.mods:
            out.append(
                f"  {len(self.mods)} out of {self.num_mods} mods are incompatible with this "
                "version:",
            )
            out += ["    " + mod for mod in sorted(self.mods, key=lambda m: m.lower())]
        else:
            out.append("  All mods are compatible with this version")
        return "\n".join(out)

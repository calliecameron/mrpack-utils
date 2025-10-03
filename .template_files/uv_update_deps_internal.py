import json
import os.path
import subprocess
import sys
import tomllib
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, Sequence, Set
from dataclasses import dataclass
from typing import override

from frozendict import frozendict
from packaging import requirements


@dataclass(frozen=True, kw_only=True)
class Package:
    name: str
    extras: frozenset[str]

    @override
    def __str__(self) -> str:
        return self.name + (f"[{','.join(sorted(self.extras))}]" if self.extras else "")


class Location(ABC):
    @abstractmethod
    def arg(self) -> str:
        raise NotImplementedError

    @override
    def __str__(self) -> str:
        return self.arg()


class Main(Location):
    @override
    def arg(self) -> str:
        return ""


class Group(Location):
    def __init__(self, group: str) -> None:
        super().__init__()
        self._group = group

    @override
    def arg(self) -> str:
        return f"--group={self._group}"


class Extra(Location):
    def __init__(self, extra: str) -> None:
        super().__init__()
        self._extra = extra

    @override
    def arg(self) -> str:
        return f"--optional={self._extra}"


class UV:
    @staticmethod
    def _uv(*args: str) -> str:
        return subprocess.run(
            ["uv"] + [arg for arg in args if arg],
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout

    @staticmethod
    def _list(*, outdated: bool) -> frozendict[str, str]:
        extra_args = []
        if outdated:
            extra_args = ["--outdated"]

        j = json.loads(UV._uv("pip", "list", "--format=json", *extra_args))

        return frozendict({p["name"]: p["version"] for p in j})

    @staticmethod
    def list_outdated() -> frozenset[str]:
        return frozenset(UV._list(outdated=True).keys())

    @staticmethod
    def list_versions() -> frozendict[str, str]:
        return UV._list(outdated=False)

    @staticmethod
    def remove(location: Location, p: Package) -> None:
        UV._uv("remove", "--frozen", location.arg(), p.name)

    @staticmethod
    def _add(location: Location, *args: str) -> None:
        UV._uv("add", "--frozen", location.arg(), *args)

    @staticmethod
    def add_raw(location: Location, p: Package) -> None:
        UV._add(location, "--raw", str(p))

    @staticmethod
    def add_version(location: Location, p: Package, version: str) -> None:
        UV._add(location, f"{p}=={version}")

    @staticmethod
    def sync() -> None:
        UV._uv("sync", "--all-extras", "--all-groups", "--upgrade")


@dataclass(frozen=True, kw_only=True)
class Packages:
    main: frozenset[Package]
    groups: frozendict[str, frozenset[Package]]
    extras: frozendict[str, frozenset[Package]]

    def all_names(self) -> frozenset[str]:
        out = set({p.name for p in self.main})
        for ps in self.groups.values():
            out.update({p.name for p in ps})
        for ps in self.extras.values():
            out.update({p.name for p in ps})
        return frozenset(out)

    def __iter__(self) -> Iterator[tuple[Location, Package]]:
        for p in sorted(self.main, key=str):
            yield (Main(), p)
        for g, ps in sorted(self.groups.items()):
            for p in sorted(ps, key=str):
                yield (Group(g), p)
        for g, ps in sorted(self.extras.items()):
            for p in sorted(ps, key=str):
                yield (Extra(g), p)

    def filter(self, names: Set[str]) -> "Packages":
        def _filter(
            groups: frozendict[str, frozenset[Package]],
        ) -> frozendict[str, frozenset[Package]]:
            return frozendict(
                {
                    g: frozenset(p for p in ps if p.name in names)
                    for (g, ps) in groups.items()
                },
            )

        return Packages(
            main=frozenset(p for p in self.main if p.name in names),
            groups=_filter(self.groups),
            extras=_filter(self.extras),
        )


def top_level_packages() -> Packages:
    def _extract_name(dep: str) -> Package:
        r = requirements.Requirement(dep)
        return Package(name=r.name, extras=frozenset(r.extras))

    def _extract_deps(
        data: Mapping[str, Sequence[str]],
    ) -> frozendict[str, frozenset[Package]]:
        return frozendict(
            {
                group: frozenset(_extract_name(dep) for dep in deps)
                for (group, deps) in data.items()
            },
        )

    with open("pyproject.toml", mode="rb") as f:
        data = tomllib.load(f)

    return Packages(
        main=frozenset(_extract_name(r) for r in data["project"]["dependencies"]),
        groups=_extract_deps(data.get("dependency-groups", {})),
        extras=_extract_deps(data["project"].get("optional-dependencies", {})),
    )


def main() -> None:
    if not os.path.exists("pyproject.toml"):
        sys.stderr.write("Must be run in the root of the project")
        sys.exit(1)

    top_level = top_level_packages()
    outdated = top_level.filter(UV.list_outdated())

    for location, p in outdated:
        UV.remove(location, p)

    for location, p in outdated:
        UV.add_raw(location, p)

    UV.sync()

    versions = UV.list_versions()

    for location, p in outdated:
        UV.add_version(location, p, versions[p.name])

    UV.sync()


if __name__ == "__main__":
    main()

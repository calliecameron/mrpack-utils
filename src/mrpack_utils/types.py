import contextlib
import functools
import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol, Self, override

import jsonschema
from frozendict import frozendict


def make_json_schema(fragment: Mapping[str, Any]) -> frozendict[str, Any]:
    d = dict(fragment)
    d["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return frozendict(d)


@functools.total_ordering
class GameVersion:
    def __init__(self, version: str) -> None:
        super().__init__()
        match = re.fullmatch(r"[0-9]+\.[0-9]+(\.[0-9]+)?", version)
        if match is None:
            raise ValueError("Not a valid game version: " + version)
        self._version = tuple(int(segment) for segment in version.split("."))

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version == other._version

    @override
    def __hash__(self) -> int:
        return hash(self._version)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version < other._version

    @override
    def __repr__(self) -> str:
        return ".".join(str(segment) for segment in self._version)

    @staticmethod
    def from_iterable(versions: Iterable[str]) -> "frozenset[GameVersion]":
        # We deliberately skip over any versions that don't parse
        out = set()
        for version in versions:
            with contextlib.suppress(ValueError):
                out.add(GameVersion(version))
        return frozenset(out)


class Requirement(Enum):
    UNKNOWN = auto()
    REQUIRED = auto()
    OPTIONAL = auto()
    UNSUPPORTED = auto()

    @staticmethod
    def schema_fragment() -> frozendict[str, Any]:
        return frozendict(
            {
                "enum": [
                    Requirement.REQUIRED.name.lower(),
                    Requirement.OPTIONAL.name.lower(),
                    Requirement.UNSUPPORTED.name.lower(),
                ],
            },
        )

    @staticmethod
    def _schema() -> frozendict[str, Any]:
        return make_json_schema(Requirement.schema_fragment())

    @staticmethod
    def load(s: str) -> "Requirement":
        jsonschema.validate(s, Requirement._schema())
        return Requirement.from_str(s)

    @staticmethod
    def from_str(s: str) -> "Requirement":
        if not s:
            return Requirement.UNKNOWN
        valid = {v.lower() for v in Requirement.__members__}
        if s not in valid:
            raise ValueError(f"Requirement value must be one of [{sorted(valid)}], got '{s}'")
        return Requirement[s.upper()]


@dataclass(frozen=True, kw_only=True)
class Env:
    SCHEMA_FRAGMENT = frozendict(
        {
            "type": "object",
            "properties": {
                "client": Requirement.schema_fragment(),
                "server": Requirement.schema_fragment(),
            },
            "required": [
                "client",
                "server",
            ],
            "additionalProperties": False,
        },
    )

    _SCHEMA = make_json_schema(SCHEMA_FRAGMENT)

    client: Requirement
    server: Requirement

    @staticmethod
    def load(env: Mapping[str, str]) -> "Env":
        jsonschema.validate(env, Env._SCHEMA)
        return Env(
            client=Requirement.load(env["client"]),
            server=Requirement.load(env["server"]),
        )


class _HashFn(Protocol):
    @property
    def digest_size(self) -> int: ...
    def update(self, data: bytes) -> None: ...
    def hexdigest(self) -> str: ...


@functools.total_ordering
class _Hash(ABC):
    def __init__(self, h: str) -> None:
        super().__init__()
        h = h.lower()
        if len(h) != self._hash_len() or re.fullmatch(r"[0-9a-f]+", h) is None:
            raise ValueError(
                f"'{h}' is not a valid {self.__class__.__name__} hash ({self._hash_len()} "
                "hex digits)",
            )
        self._hash = h

    @classmethod
    @abstractmethod
    def _hash_fn(cls) -> _HashFn:
        raise NotImplementedError  # pragma: no cover

    def _hash_len(self) -> int:
        return self._hash_fn().digest_size * 2

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._hash == other._hash

    @override
    def __hash__(self) -> int:
        return hash(self._hash)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._hash < other._hash

    @override
    def __repr__(self) -> str:
        return self._hash

    @classmethod
    def from_data(cls, data: bytes) -> Self:
        fn = cls._hash_fn()
        fn.update(data)
        return cls(fn.hexdigest())


class Sha1(_Hash):
    @override
    @classmethod
    def _hash_fn(cls) -> _HashFn:
        return hashlib.sha1()  # noqa: S324


class Sha512(_Hash):
    @override
    @classmethod
    def _hash_fn(cls) -> _HashFn:
        return hashlib.sha512()


@functools.total_ordering
class _ID:
    def __init__(self, i: str) -> None:
        super().__init__()
        if len(i) != 8:  # noqa: PLR2004
            raise ValueError(f"'{i}' is not a valid ID (8-digit string)")
        self._id = i

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._id == other._id

    @override
    def __hash__(self) -> int:
        return hash(self._id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._id < other._id

    @override
    def __repr__(self) -> str:
        return self._id


class ProjectID(_ID):
    pass


class VersionID(_ID):
    pass

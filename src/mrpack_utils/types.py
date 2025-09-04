import contextlib
import functools
import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol, Self, override


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
    def from_str(s: str) -> "Requirement":
        if not s or s == "unknown":
            return Requirement.UNKNOWN
        if s == "required":
            return Requirement.REQUIRED
        if s == "optional":
            return Requirement.OPTIONAL
        if s == "unsupported":
            return Requirement.UNSUPPORTED
        raise ValueError(
            "Requirement value must be one of {required, optional, unsupported}, got '" + s + "'",
        )


@dataclass(frozen=True, kw_only=True)
class Env:
    client: Requirement
    server: Requirement

    @staticmethod
    def load(env: Mapping[str, str]) -> "Env":
        if env.keys() != frozenset(["client", "server"]):
            raise ValueError("Env must have keys {client, server}, got " + str(env.keys()))
        return Env(
            client=Requirement.from_str(env["client"]),
            server=Requirement.from_str(env["server"]),
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

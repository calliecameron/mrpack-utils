import contextlib
import functools
import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum, auto
from typing import Self, override


@functools.total_ordering
class GameVersion:
    def __init__(self, version: str) -> None:
        super().__init__()
        match = re.fullmatch(r"[0-9]+\.[0-9]+(\.[0-9]+)?", version)
        if match is None:
            raise ValueError("Not a valid game version: " + version)
        self._version = tuple(int(segment) for segment in version.split("."))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version == other._version

    def __hash__(self) -> int:
        return hash(self._version)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GameVersion):
            raise NotImplementedError
        return self._version < other._version

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
    def _hexdigest(cls, data: bytes) -> str:
        raise NotImplementedError  # pragma: no cover

    @classmethod
    @abstractmethod
    def _digest_size(cls) -> int:
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _hash_len(cls) -> int:
        return cls._digest_size() * 2

    @override
    def __str__(self) -> str:
        return self._hash

    @override
    def __repr__(self) -> str:
        return str(self)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._hash == other._hash

    @override
    def __hash__(self) -> int:
        return hash(self._hash)

    @classmethod
    def from_data(cls, data: bytes) -> Self:
        return cls(cls._hexdigest(data))


class Sha1(_Hash):
    @override
    @classmethod
    def _hexdigest(cls, data: bytes) -> str:
        return hashlib.sha1(data).hexdigest()  # noqa: S324

    @override
    @classmethod
    def _digest_size(cls) -> int:
        return hashlib.sha1().digest_size  # noqa: S324


class Sha512(_Hash):
    @override
    @classmethod
    def _hexdigest(cls, data: bytes) -> str:
        return hashlib.sha512(data).hexdigest()

    @override
    @classmethod
    def _digest_size(cls) -> int:
        return hashlib.sha512().digest_size

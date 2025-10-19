from typing import TYPE_CHECKING, Any, override

import jsonschema
from frozendict import frozendict

from mrpack.types import (
    Env,
    GameVersion,
    Sha1,
    Sha512,
    make_json_schema,
    validated_path,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Set
    from pathlib import PurePath


class Hashes:
    SCHEMA_FRAGMENT = frozendict(
        {
            "type": "object",
            "properties": {
                "sha1": {
                    "type": "string",
                },
                "sha512": {
                    "type": "string",
                },
            },
            "patternProperties": {
                ".*": {
                    "type": "string",
                },
            },
            "required": [
                "sha1",
                "sha512",
            ],
            "additionalProperties": True,
        },
    )

    _SCHEMA = make_json_schema(SCHEMA_FRAGMENT)

    def __init__(
        self,
        *,
        sha1: Sha1,
        sha512: Sha512,
        others: Mapping[str, str],
    ) -> None:
        super().__init__()
        self._sha1 = sha1
        self._sha512 = sha512
        if "sha1" in others or "sha512" in others:
            raise ValueError(
                "'sha1' and 'sha512' must not be in 'others'; they have dedicated args",
            )
        self._others = frozendict(others)

    @property
    def sha1(self) -> Sha1:
        return self._sha1

    @property
    def sha512(self) -> Sha512:
        return self._sha512

    @property
    def others(self) -> frozendict[str, str]:
        return self._others

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hashes):
            return NotImplemented
        return (
            self._sha1 == other._sha1
            and self._sha512 == other._sha512
            and self._others == other._others
        )

    @override
    def __hash__(self) -> int:
        return hash((self._sha1, self._sha512, self._others))

    @staticmethod
    def from_json(data: Mapping[str, str]) -> Hashes:
        jsonschema.validate(data, Hashes._SCHEMA)
        others = {k: v for (k, v) in data.items() if k not in {"sha1", "sha512"}}
        return Hashes(
            sha1=Sha1(data["sha1"]),
            sha512=Sha512(data["sha512"]),
            others=others,
        )


class File:
    SCHEMA_FRAGMENT = frozendict(
        {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                },
                "hashes": Hashes.SCHEMA_FRAGMENT,
                "env": Env.SCHEMA_FRAGMENT,
                "downloads": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "uniqueItems": True,
                },
                "fileSize": {
                    "type": "integer",
                    "exclusiveMinimum": 0,
                },
            },
            "required": [
                "path",
                "hashes",
                "downloads",
                "fileSize",
            ],
            "additionalProperties": False,
        },
    )

    _SCHEMA = make_json_schema(SCHEMA_FRAGMENT)

    def __init__(
        self,
        *,
        path: str,
        hashes: Hashes,
        env: Env | None,
        downloads: Set[str],
        size: int,
    ) -> None:
        super().__init__()
        self._path = validated_path(path)
        self._hashes = hashes
        self._env = env
        self._downloads = frozenset(downloads)
        if size <= 0:
            raise ValueError(f"'size' must be positive, got {size}")
        self._size = size

    @property
    def path(self) -> PurePath:
        return self._path

    @property
    def hashes(self) -> Hashes:
        return self._hashes

    @property
    def env(self) -> Env | None:
        return self._env

    @property
    def downloads(self) -> frozenset[str]:
        return self._downloads

    @property
    def size(self) -> int:
        return self._size

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, File):
            return NotImplemented
        return (
            self._path == other._path
            and self._hashes == other._hashes
            and self._env == other._env
            and self._downloads == other._downloads
            and self._size == other._size
        )

    @override
    def __hash__(self) -> int:
        return hash((self._path, self._hashes, self._env, self._downloads, self._size))

    @staticmethod
    def from_json(data: Mapping[str, Any]) -> File:
        jsonschema.validate(data, File._SCHEMA)
        return File(
            path=data["path"],
            hashes=Hashes.from_json(data["hashes"]),
            env=Env.from_json(data["env"]) if "env" in data else None,
            downloads=frozenset(data["downloads"]),
            size=data["fileSize"],
        )


class Dependencies:  # noqa: PLW1641
    _LOADERS = frozendict(
        {
            "minecraft": "minecraft",
            "forge": "forge",
            "neoforge": "neoforge",
            "fabric-loader": "fabric",
            "quilt-loader": "quilt",
        },
    )

    SCHEMA_FRAGMENT = frozendict(
        {
            "type": "object",
            "properties": {
                "minecraft": {
                    "type": "string",
                },
            },
            "patternProperties": {
                ".*": {
                    "type": "string",
                },
            },
            "required": [
                "minecraft",
            ],
            "additionalProperties": True,
        },
    )

    _SCHEMA = make_json_schema(SCHEMA_FRAGMENT)

    def __init__(self, *, game_version: GameVersion, others: Mapping[str, str]) -> None:
        super().__init__()
        self._game_version = game_version
        if "minecraft" in others:
            raise ValueError(
                "'minecraft' must not be in 'others'; it has a dedicated arg",
            )
        self._others = frozendict(others)

        self._unknown_dependencies = frozenset(
            self._others - Dependencies._LOADERS.keys(),
        )
        self._loaders = frozenset(
            {"minecraft"}
            | {
                Dependencies._LOADERS[d]
                for d in self._others
                if d in Dependencies._LOADERS
            },
        )

    @property
    def game_version(self) -> GameVersion:
        return self._game_version

    @property
    def others(self) -> frozendict[str, str]:
        return self._others

    @property
    def unknown_dependencies(self) -> frozenset[str]:
        return self._unknown_dependencies

    @property
    def loaders(self) -> frozenset[str]:
        return self._loaders

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dependencies):
            return NotImplemented
        return (
            self._game_version == other._game_version and self._others == other._others
        )

    @staticmethod
    def from_json(data: Mapping[str, str]) -> Dependencies:
        jsonschema.validate(data, Dependencies._SCHEMA)
        others = {k: v for (k, v) in data.items() if k != "minecraft"}
        return Dependencies(
            game_version=GameVersion(data["minecraft"]),
            others=others,
        )


class Index:  # noqa: PLW1641
    _FORMAT_VERSION = 1
    _GAME = "minecraft"
    _SCHEMA = make_json_schema(
        {
            "type": "object",
            "properties": {
                "formatVersion": {
                    "const": _FORMAT_VERSION,
                },
                "game": {
                    "const": _GAME,
                },
                "versionId": {
                    "type": "string",
                },
                "name": {
                    "type": "string",
                },
                "summary": {
                    "type": "string",
                },
                "files": {
                    "type": "array",
                    "items": File.SCHEMA_FRAGMENT,
                    "uniqueItems": True,
                },
                "dependencies": Dependencies.SCHEMA_FRAGMENT,
            },
            "required": [
                "formatVersion",
                "game",
                "versionId",
                "name",
                "files",
                "dependencies",
            ],
            "additionalProperties": False,
        },
    )

    def __init__(
        self,
        *,
        name: str,
        version: str,
        summary: str,
        files: Set[File],
        dependencies: Dependencies,
    ) -> None:
        super().__init__()
        self._name = name
        self._version = version
        self._summary = summary

        fs = {}
        for file in files:
            if file.hashes.sha512 in fs:
                raise ValueError(f"Duplicate file SHA512 '{file.hashes.sha512}'")
            fs[file.hashes.sha512] = file
        self._files = frozendict(fs)
        self._dependencies = dependencies

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def files(self) -> frozendict[Sha512, File]:
        return self._files

    @property
    def dependencies(self) -> Dependencies:
        return self._dependencies

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Index):
            return NotImplemented
        return (
            self._name == other._name
            and self._version == other._version
            and self._summary == other._summary
            and self._files == other._files
            and self._dependencies == other._dependencies
        )

    @staticmethod
    def from_json(data: Mapping[str, Any]) -> Index:
        jsonschema.validate(data, Index._SCHEMA)
        files = {File.from_json(file) for file in data["files"]}
        return Index(
            name=data["name"],
            version=data["versionId"],
            summary=data.get("summary", ""),
            files=files,
            dependencies=Dependencies.from_json(data["dependencies"]),
        )

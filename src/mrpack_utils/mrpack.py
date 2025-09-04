import json
import zipfile
from collections.abc import Mapping, Set
from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, override

import jsonschema
from frozendict import frozendict

from mrpack_utils.types import Env, GameVersion, Sha1, Sha512, make_json_schema


class MrpackError(Exception):
    pass


def _validated_path(path: str) -> PurePath:
    pp = PurePosixPath(path)
    wp = PureWindowsPath(path)
    p = PurePath(path)
    if (
        pp.is_absolute()
        or not pp.parts
        or wp.is_absolute()
        or not wp.parts
        or "." in p.parts
        or ".." in p.parts
    ):
        raise ValueError(f"Invalid path '{path}'; must be relative and not contain '.' or '..'")
    return p


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

    def __init__(self, *, sha1: Sha1, sha512: Sha512, others: Mapping[str, str]) -> None:
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
            raise NotImplementedError
        return (
            self._sha1 == other._sha1
            and self._sha512 == other._sha512
            and self._others == other._others
        )

    @override
    def __hash__(self) -> int:
        return hash((self._sha1, self._sha512, self._others))

    @staticmethod
    def load(data: Mapping[str, str]) -> "Hashes":
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
        self._path = _validated_path(path)
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
            raise NotImplementedError
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
    def load(data: Mapping[str, Any]) -> "File":
        jsonschema.validate(data, File._SCHEMA)
        return File(
            path=data["path"],
            hashes=Hashes.load(data["hashes"]),
            env=Env.load(data["env"]) if "env" in data else None,
            downloads=frozenset(data["downloads"]),
            size=data["fileSize"],
        )


class Index:  # noqa: PLW1641
    _LOADERS = frozendict(
        {
            "minecraft": "minecraft",
            "forge": "forge",
            "neoforge": "neoforge",
            "fabric-loader": "fabric",
            "quilt-loader": "quilt",
        },
    )

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
                "dependencies": {
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
        dependencies: Mapping[str, str],
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

        self._dependencies = frozendict(dependencies)
        self._known_dependencies = frozenset(self._dependencies & Index._LOADERS.keys())
        self._unknown_dependencies = frozenset(self._dependencies - Index._LOADERS.keys())

        if "minecraft" not in self._dependencies:
            raise ValueError("Missing 'minecraft' dependency")
        self._game_version = GameVersion(self._dependencies["minecraft"])

        self._loaders = frozenset(
            {Index._LOADERS[d] for d in self._dependencies if d in Index._LOADERS},
        )

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
    def dependencies(self) -> frozendict[str, str]:
        return self._dependencies

    @property
    def known_dependencies(self) -> frozenset[str]:
        return self._known_dependencies

    @property
    def unknown_dependencies(self) -> frozenset[str]:
        return self._unknown_dependencies

    @property
    def game_version(self) -> GameVersion:
        return self._game_version

    @property
    def loaders(self) -> frozenset[str]:
        return self._loaders

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Index):
            raise NotImplementedError
        return (
            self._name == other._name
            and self._version == other._version
            and self._summary == other._summary
            and self._files == other._files
            and self._dependencies == other._dependencies
        )

    @staticmethod
    def load(data: Mapping[str, Any]) -> "Index":
        jsonschema.validate(data, Index._SCHEMA)
        files = {File.load(file) for file in data["files"]}
        return Index(
            name=data["name"],
            version=data["versionId"],
            summary=data.get("summary", ""),
            files=files,
            dependencies=data["dependencies"],
        )


class Override:
    def __init__(self, *, path: str, data: bytes) -> None:
        super().__init__()
        self._path = _validated_path(path)
        self._data = data
        self._hash = Sha512.from_data(data)
        # This is the same check 'diff' uses to detect binary files
        self._is_text = b"\0" not in data

    @property
    def path(self) -> PurePath:
        return self._path

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def hash(self) -> Sha512:
        return self._hash

    @property
    def is_text(self) -> bool:
        return self._is_text

    def text(self) -> str:
        if not self._is_text:
            raise ValueError("Tried to decode non-text data")
        return self._data.decode()

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Override):
            raise NotImplementedError
        return self._path == other._path and self._data == other._data

    @override
    def __hash__(self) -> int:
        return hash((self._path, self._data))


class Mrpack:
    _OVERRIDES_PREFIX = "overrides"
    _CLIENT_OVERRIDES_PREFIX = "client-overrides"
    _SERVER_OVERRIDES_PREFIX = "server-overrides"
    _INDEX_FILENAME = "modrinth.index.json"

    def __init__(
        self,
        *,
        index: Index,
        overrides: Set[Override],
        client_overrides: Set[Override],
        server_overrides: Set[Override],
    ) -> None:
        super().__init__()
        self._index = index

        def _validate_overrides(
            os: Set[Override],
            name: str,
            prefix: str,
        ) -> frozendict[PurePath, Override]:
            out = {}
            for o in os:
                if o.path.parts[0] != prefix:
                    raise ValueError(
                        f"{name.capitalize()} must have a path starting with '{prefix}'; got "
                        f"'{o.path}",
                    )
                if o.path in out:
                    raise ValueError(f"Duplicate {name} path '{o.path}")
                out[o.path] = o
            return frozendict(out)

        self._overrides = _validate_overrides(
            overrides,
            "override",
            Mrpack._OVERRIDES_PREFIX,
        )
        self._client_overrides = _validate_overrides(
            client_overrides,
            "client override",
            Mrpack._CLIENT_OVERRIDES_PREFIX,
        )
        self._server_overrides = _validate_overrides(
            server_overrides,
            "server override",
            Mrpack._SERVER_OVERRIDES_PREFIX,
        )

    @property
    def index(self) -> Index:
        return self._index

    @property
    def overrides(self) -> frozendict[PurePath, Override]:
        return self._overrides

    @property
    def client_overrides(self) -> frozendict[PurePath, Override]:
        return self._client_overrides

    @property
    def server_overrides(self) -> frozendict[PurePath, Override]:
        return self._server_overrides

    @staticmethod
    def load(filename: str) -> "Mrpack":
        try:
            with zipfile.ZipFile(filename) as z:
                bad_file = z.testzip()
                if bad_file:
                    raise ValueError(f"Found bad file in zip: {bad_file}")  # pragma: no cover

                with z.open(Mrpack._INDEX_FILENAME) as f:
                    j = json.load(f)
                index = Index.load(j)

                overrides: set[Override] = set()
                client_overrides: set[Override] = set()
                server_overrides: set[Override] = set()

                for entry in z.infolist():
                    if entry.filename != Mrpack._INDEX_FILENAME and not entry.is_dir():
                        path = _validated_path(entry.filename)
                        if path.parts[0] == Mrpack._OVERRIDES_PREFIX:
                            target = overrides
                        elif path.parts[0] == Mrpack._CLIENT_OVERRIDES_PREFIX:
                            target = client_overrides
                        elif path.parts[0] == Mrpack._SERVER_OVERRIDES_PREFIX:
                            target = server_overrides
                        else:
                            raise ValueError(
                                f"File with invalid path '{entry.filename}'; must be in "
                                f"{Mrpack._OVERRIDES_PREFIX}, {Mrpack._CLIENT_OVERRIDES_PREFIX} "
                                f"or {Mrpack._SERVER_OVERRIDES_PREFIX}",
                            )
                        target.add(Override(path=entry.filename, data=z.read(entry)))

            return Mrpack(
                index=index,
                overrides=overrides,
                client_overrides=client_overrides,
                server_overrides=server_overrides,
            )
        except Exception as e:
            raise MrpackError("Failed to load mrpack file: " + str(e)) from e

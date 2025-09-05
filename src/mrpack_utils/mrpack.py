import json
import zipfile
from collections.abc import Set
from pathlib import PurePath
from typing import override

from frozendict import frozendict

from mrpack_utils.index import Index
from mrpack_utils.types import Sha512, validated_path


class MrpackError(Exception):
    pass


class Override:
    def __init__(self, *, path: str, data: bytes) -> None:
        super().__init__()
        self._path = validated_path(path)
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
                        path = validated_path(entry.filename)
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

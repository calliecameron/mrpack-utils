import json
import zipfile
from enum import Enum, auto
from typing import TYPE_CHECKING, override

from frozendict import frozendict

from mrpack.index import Index
from mrpack.types import Sha512, validated_path

if TYPE_CHECKING:
    from collections.abc import Set
    from pathlib import PurePath


class MrpackError(Exception):
    pass


class OverrideType(Enum):
    GENERAL = auto()
    CLIENT = auto()
    SERVER = auto()

    @staticmethod
    def from_prefix(prefix: str) -> OverrideType:
        general_prefix = "overrides"
        client_prefix = "client-overrides"
        server_prefix = "server-overrides"

        if prefix == general_prefix:
            return OverrideType.GENERAL
        if prefix == client_prefix:
            return OverrideType.CLIENT
        if prefix == server_prefix:
            return OverrideType.SERVER
        raise ValueError(
            f"Invalid override prefix '{prefix}'; must be one of [{general_prefix}, "
            f"{client_prefix}, {server_prefix}]",
        )


class Override:
    def __init__(self, *, path: str, data: bytes) -> None:
        super().__init__()
        self._path = validated_path(path)
        if len(self._path.parts) < 2:  # noqa: PLR2004
            raise ValueError(f"Override must be in a subfolder; got '{self._path}'")
        self._type = OverrideType.from_prefix(self._path.parts[0])

        self._data = data
        self._hash = Sha512.from_data(data)
        # This is the same check 'diff' uses to detect binary files
        self._is_text = b"\0" not in data

    @property
    def path(self) -> PurePath:
        return self._path

    @property
    def type(self) -> OverrideType:
        return self._type

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
            return NotImplemented
        return self._path == other._path and self._data == other._data

    @override
    def __hash__(self) -> int:
        return hash((self._path, self._data))


class Mrpack:
    _INDEX_FILENAME = "modrinth.index.json"

    def __init__(
        self,
        *,
        index: Index,
        overrides: Set[Override],
    ) -> None:
        super().__init__()
        self._index = index

        out = {}
        for o in overrides:
            if o.path in out:
                raise ValueError(f"Duplicate override path '{o.path}")
            out[o.path] = o
        self._overrides = frozendict(out)

    @property
    def index(self) -> Index:
        return self._index

    @property
    def overrides(self) -> frozendict[PurePath, Override]:
        return self._overrides

    @staticmethod
    def from_file(filename: str) -> Mrpack:
        try:
            with zipfile.ZipFile(filename) as z:
                bad_file = z.testzip()
                if bad_file:
                    raise ValueError(
                        f"Found bad file in zip: {bad_file}",
                    )  # pragma: no cover

                with z.open(Mrpack._INDEX_FILENAME) as f:
                    j = json.load(f)
                index = Index.from_json(j)

                overrides: set[Override] = set()
                for entry in z.infolist():
                    if entry.filename != Mrpack._INDEX_FILENAME and not entry.is_dir():
                        overrides.add(Override(path=entry.filename, data=z.read(entry)))

            return Mrpack(
                index=index,
                overrides=overrides,
            )
        except Exception as e:
            raise MrpackError("Failed to load mrpack file: " + str(e)) from e

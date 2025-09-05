from pathlib import PurePath

import jsonschema
import pytest
from frozendict import frozendict

from mrpack_utils.index import File, Hashes, Index
from mrpack_utils.types import Env, GameVersion, Requirement, Sha1, Sha512

# ruff: noqa: PT011, S101


class TestHashes:
    def test_init(self) -> None:
        h = Hashes(
            sha1=Sha1("a000000000000000000000000000000000000000"),
            sha512=Sha512(
                "a000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000000",
            ),
            others={"foo": "bar"},
        )
        assert h.sha1 == Sha1("a000000000000000000000000000000000000000")
        assert h.sha512 == Sha512(
            "a000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000000",
        )
        assert h.others == frozendict({"foo": "bar"})

        with pytest.raises(ValueError):
            Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={
                    "foo": "bar",
                    "sha1": "a000000000000000000000000000000000000000",
                },
            )

        with pytest.raises(ValueError):
            Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={
                    "foo": "bar",
                    "sha512": (
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    ),
                },
            )

    def test_from_json_valid(self) -> None:
        h1 = Hashes.from_json(
            {
                "sha1": "a000000000000000000000000000000000000000",
                "sha512": (
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
        )
        assert h1.sha1 == Sha1("a000000000000000000000000000000000000000")
        assert h1.sha512 == Sha512(
            "a000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000000",
        )
        assert h1.others == frozendict({})

        h2 = Hashes.from_json(
            {
                "sha1": "a000000000000000000000000000000000000000",
                "sha512": (
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
                "foo": "bar",
            },
        )
        assert h2.sha1 == Sha1("a000000000000000000000000000000000000000")
        assert h2.sha512 == Sha512(
            "a000000000000000000000000000000000000000000000000000000000000000"
            "0000000000000000000000000000000000000000000000000000000000000000",
        )
        assert h2.others == frozendict({"foo": "bar"})

        assert h1 == h1  # noqa: PLR0124
        assert h1 != h2
        with pytest.raises(NotImplementedError):
            assert h1 == "foo"

    def test_from_json_invalid(self) -> None:
        # No sha1
        with pytest.raises(jsonschema.ValidationError):
            Hashes.from_json(
                {
                    "sha512": (
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    ),
                    "foo": "bar",
                },
            )
        # No sha512
        with pytest.raises(jsonschema.ValidationError):
            Hashes.from_json(
                {
                    "sha1": "a000000000000000000000000000000000000000",
                    "foo": "bar",
                },
            )
        # Invalid sha1
        with pytest.raises(ValueError):
            Hashes.from_json(
                {
                    "sha1": "a",
                    "sha512": (
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    ),
                    "foo": "bar",
                },
            )
        # Invalid sha512
        with pytest.raises(ValueError):
            Hashes.from_json(
                {
                    "sha1": "a000000000000000000000000000000000000000",
                    "sha512": "a",
                    "foo": "bar",
                },
            )


class TestFile:
    def test_init(self) -> None:
        f1 = File(
            path="a/b",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"foo", "bar"},
            size=10,
        )

        assert f1.path == PurePath("a", "b")
        assert f1.hashes == Hashes(
            sha1=Sha1("a000000000000000000000000000000000000000"),
            sha512=Sha512(
                "a000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000000",
            ),
            others={},
        )
        assert f1.env == Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL)
        assert f1.downloads == frozenset({"foo", "bar"})
        assert f1.size == 10  # noqa: PLR2004

        f2 = File(
            path="a/b",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=None,
            downloads={"foo", "bar"},
            size=10,
        )

        assert f2.path == PurePath("a", "b")
        assert f2.hashes == Hashes(
            sha1=Sha1("a000000000000000000000000000000000000000"),
            sha512=Sha512(
                "a000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000000",
            ),
            others={},
        )
        assert f2.env is None
        assert f2.downloads == frozenset({"foo", "bar"})
        assert f2.size == 10  # noqa: PLR2004

        assert f1 == f1  # noqa: PLR0124
        assert f1 != f2
        with pytest.raises(NotImplementedError):
            assert f1 == "foo"

        # Bad size
        with pytest.raises(ValueError):
            File(
                path="a/b",
                hashes=Hashes(
                    sha1=Sha1("a000000000000000000000000000000000000000"),
                    sha512=Sha512(
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000",
                    ),
                    others={},
                ),
                env=None,
                downloads=set(),
                size=-1,
            )

    def test_from_json_valid(self) -> None:
        f1 = File.from_json(
            {
                "path": "a/b",
                "hashes": {
                    "sha1": "a000000000000000000000000000000000000000",
                    "sha512": (
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    ),
                },
                "env": {
                    "client": "required",
                    "server": "optional",
                },
                "downloads": [
                    "bar",
                    "foo",
                ],
                "fileSize": 10,
            },
        )

        assert f1.path == PurePath("a", "b")
        assert f1.hashes == Hashes(
            sha1=Sha1("a000000000000000000000000000000000000000"),
            sha512=Sha512(
                "a000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000000",
            ),
            others={},
        )
        assert f1.env == Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL)
        assert f1.downloads == frozenset({"foo", "bar"})
        assert f1.size == 10  # noqa: PLR2004

        f2 = File.from_json(
            {
                "path": "a/b",
                "hashes": {
                    "sha1": "a000000000000000000000000000000000000000",
                    "sha512": (
                        "a000000000000000000000000000000000000000000000000000000000000000"
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    ),
                },
                "downloads": [
                    "bar",
                    "foo",
                ],
                "fileSize": 10,
            },
        )

        assert f2.path == PurePath("a", "b")
        assert f2.hashes == Hashes(
            sha1=Sha1("a000000000000000000000000000000000000000"),
            sha512=Sha512(
                "a000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000000",
            ),
            others={},
        )
        assert f2.env is None
        assert f2.downloads == frozenset({"foo", "bar"})
        assert f2.size == 10  # noqa: PLR2004

        assert f1 != f2

    def test_from_json_invalid(self) -> None:
        # No path
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                    "fileSize": 10,
                },
            )
        # Invalid path
        with pytest.raises(ValueError):
            File.from_json(
                {
                    "path": "a/../b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                    "fileSize": 10,
                },
            )
        # No hashes
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                    "fileSize": 10,
                },
            )
        # No downloads
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "fileSize": 10,
                },
            )
        # Duplicate downloads
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                        "bar",
                    ],
                    "fileSize": 10,
                },
            )
        # No file size
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                },
            )
        # Bad file size
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                    "fileSize": 0,
                },
            )
        # Extra key
        with pytest.raises(jsonschema.ValidationError):
            File.from_json(
                {
                    "path": "a/b",
                    "hashes": {
                        "sha1": "a000000000000000000000000000000000000000",
                        "sha512": (
                            "a000000000000000000000000000000000000000000000000000000000000000"
                            "0000000000000000000000000000000000000000000000000000000000000000"
                        ),
                    },
                    "env": {
                        "client": "required",
                        "server": "optional",
                    },
                    "downloads": [
                        "bar",
                        "foo",
                    ],
                    "fileSize": 10,
                    "foo": "bar",
                },
            )


class TestIndex:
    def test_init(self) -> None:
        f1 = File(
            path="a/b",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.OPTIONAL),
            downloads={"foo", "bar"},
            size=10,
        )
        f2 = File(
            path="c/d",
            hashes=Hashes(
                sha1=Sha1("b000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "b000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.UNSUPPORTED),
            downloads={"foo", "bar"},
            size=20,
        )
        f2_f1_hash = File(
            path="c/d",
            hashes=Hashes(
                sha1=Sha1("a000000000000000000000000000000000000000"),
                sha512=Sha512(
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ),
                others={},
            ),
            env=Env(client=Requirement.REQUIRED, server=Requirement.UNSUPPORTED),
            downloads={"foo", "bar"},
            size=20,
        )

        i = Index(
            name="Test Modpack",
            version="1.0",
            summary="foo",
            files={f1, f2},
            dependencies={
                "minecraft": "1.20.1",
                "fabric-loader": "0.16",
                "foo": "2",
            },
        )

        assert i.name == "Test Modpack"
        assert i.version == "1.0"
        assert i.summary == "foo"
        assert i.files == frozendict({f1.hashes.sha512: f1, f2.hashes.sha512: f2})
        assert i.dependencies == frozendict(
            {"minecraft": "1.20.1", "foo": "2", "fabric-loader": "0.16"},
        )
        assert i.known_dependencies == frozenset({"minecraft", "fabric-loader"})
        assert i.unknown_dependencies == frozenset({"foo"})
        assert i.game_version == GameVersion("1.20.1")
        assert i.loaders == frozenset({"minecraft", "fabric"})

        # Duplicate hashes
        with pytest.raises(ValueError):
            Index(
                name="Test Modpack",
                version="1.0",
                summary="foo",
                files={f1, f2_f1_hash},
                dependencies={"minecraft": "1.20.1", "foo": "2"},
            )

        # No minecraft dependency
        with pytest.raises(ValueError):
            Index(
                name="Test Modpack",
                version="1.0",
                summary="foo",
                files={f1, f2},
                dependencies={"foo": "2"},
            )

    def test_from_json_valid(self) -> None:
        f1_raw = {
            "path": "a/b",
            "hashes": {
                "sha1": "a000000000000000000000000000000000000000",
                "sha512": (
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
            "downloads": [
                "foo",
                "bar",
            ],
            "fileSize": 10,
        }
        f1 = File.from_json(f1_raw)

        f2_raw = {
            "path": "c/d",
            "hashes": {
                "sha1": "b000000000000000000000000000000000000000",
                "sha512": (
                    "b000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
            "downloads": [
                "foo",
                "bar",
            ],
            "fileSize": 20,
        }
        f2 = File.from_json(f2_raw)

        i1 = Index.from_json(
            {
                "formatVersion": 1,
                "game": "minecraft",
                "versionId": "1.0",
                "name": "Test Modpack",
                "summary": "foo",
                "files": [
                    f1_raw,
                    f2_raw,
                ],
                "dependencies": {
                    "minecraft": "1.20.1",
                    "foo": "2",
                    "fabric-loader": "0.16",
                },
            },
        )

        assert i1.name == "Test Modpack"
        assert i1.version == "1.0"
        assert i1.summary == "foo"
        assert i1.files == frozendict({f1.hashes.sha512: f1, f2.hashes.sha512: f2})
        assert i1.dependencies == frozendict(
            {"minecraft": "1.20.1", "foo": "2", "fabric-loader": "0.16"},
        )
        assert i1.known_dependencies == frozenset({"minecraft", "fabric-loader"})
        assert i1.unknown_dependencies == frozenset({"foo"})
        assert i1.game_version == GameVersion("1.20.1")
        assert i1.loaders == frozenset({"minecraft", "fabric"})

        i2 = Index.from_json(
            {
                "formatVersion": 1,
                "game": "minecraft",
                "versionId": "1.0",
                "name": "Test Modpack",
                "files": [
                    f1_raw,
                    f2_raw,
                ],
                "dependencies": {
                    "minecraft": "1.20.1",
                    "foo": "2",
                },
            },
        )

        assert i2.name == "Test Modpack"
        assert i2.version == "1.0"
        assert i2.summary == ""
        assert i2.files == frozendict({f1.hashes.sha512: f1, f2.hashes.sha512: f2})
        assert i2.dependencies == frozendict({"minecraft": "1.20.1", "foo": "2"})
        assert i2.known_dependencies == frozenset({"minecraft"})
        assert i2.unknown_dependencies == frozenset({"foo"})
        assert i2.game_version == GameVersion("1.20.1")
        assert i2.loaders == frozenset({"minecraft"})

        assert i1 == i1  # noqa: PLR0124
        assert i1 != i2
        with pytest.raises(NotImplementedError):
            assert i1 == "foo"

    def test_from_json_invalid(self) -> None:
        f1_raw = {
            "path": "a/b",
            "hashes": {
                "sha1": "a000000000000000000000000000000000000000",
                "sha512": (
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
            "downloads": [
                "foo",
                "bar",
            ],
            "fileSize": 10,
        }

        f2_raw = {
            "path": "c/d",
            "hashes": {
                "sha1": "b000000000000000000000000000000000000000",
                "sha512": (
                    "b000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
            "downloads": [
                "foo",
                "bar",
            ],
            "fileSize": 20,
        }

        f2_raw_f1_hash = {
            "path": "c/d",
            "hashes": {
                "sha1": "a000000000000000000000000000000000000000",
                "sha512": (
                    "a000000000000000000000000000000000000000000000000000000000000000"
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            },
            "downloads": [
                "foo",
                "bar",
            ],
            "fileSize": 20,
        }

        # No format version
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # Wrong format version
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 2,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # No game
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # Wrong game
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "foo",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # No version ID
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # No name
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # No files
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # Duplicate files
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f1_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # Duplicate hash
        with pytest.raises(ValueError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw_f1_hash,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                },
            )
        # No dependencies
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                },
            )
        # No minecraft dependency
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "foo": "2",
                    },
                },
            )
        # Extra key
        with pytest.raises(jsonschema.ValidationError):
            Index.from_json(
                {
                    "formatVersion": 1,
                    "game": "minecraft",
                    "versionId": "1.0",
                    "name": "Test Modpack",
                    "summary": "foo",
                    "files": [
                        f1_raw,
                        f2_raw,
                    ],
                    "dependencies": {
                        "minecraft": "1.20.1",
                        "foo": "2",
                    },
                    "foo": "bar",
                },
            )

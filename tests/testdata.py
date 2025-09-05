import requests_mock

_FILE_A0 = {
    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "a0000000",
        "version_number": "1.2.3",
        "files": [
            {
                "hashes": {
                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
            {
                "hashes": {
                    "sha512": "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
    },
}
_FILE_A1 = {
    "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "a0000000",
        "version_number": "1.2.4",
        "files": [
            {
                "hashes": {
                    "sha512": "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
            {
                "hashes": {
                    "sha512": "a1100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
    },
}
_FILE_B0 = {
    "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "b0000000",
        "version_number": "4.5.6",
        "files": [
            {
                "hashes": {
                    "sha512": "b0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
    },
}
_FILE_D0 = {
    "d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "d0000000",
        "version_number": "1.0.0",
        "files": [
            {
                "hashes": {
                    "sha512": "d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
    },
}

_PROJECT_A = {
    "id": "a0000000",
    "title": "A",
    "slug": "a",
    "client_side": "optional",
    "server_side": "required",
    "license": {"id": "MIT"},
    "source_url": "S",
    "issues_url": "I",
}
_PROJECT_B = {
    "id": "b0000000",
    "title": "B",
    "slug": "b",
}
_PROJECT_D = {
    "id": "d0000000",
    "title": "D",
    "slug": "d",
}

_VERSION_A0 = {
    "id": "A0000000",
    "project_id": "a0000000",
    "loaders": ["fabric"],
    "game_versions": ["1.19.2"],
}
_VERSION_A1 = {
    "id": "A1000000",
    "project_id": "a0000000",
    "loaders": ["fabric", "minecraft"],
    "game_versions": ["1.20"],
}
_VERSION_B0 = {
    "id": "B0000000",
    "project_id": "b0000000",
    "loaders": ["minecraft"],
    "game_versions": ["1.19.4"],
}
_VERSION_D0 = {
    "id": "D0000000",
    "project_id": "d0000000",
    "loaders": ["fabric"],
    "game_versions": ["1.19.4"],
}


def test1_list_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json=_FILE_A0 | _FILE_B0,
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
        complete_qs=True,
        json=[
            _PROJECT_A,
            _PROJECT_B,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            _VERSION_A0,
            _VERSION_A1,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            _VERSION_B0,
        ],
    )


def test1_test2_diff_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json=_FILE_A0 | _FILE_A1 | _FILE_B0 | _FILE_D0,
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000", "d0000000"]',
        complete_qs=True,
        json=[
            _PROJECT_A,
            _PROJECT_B,
            _PROJECT_D,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            _VERSION_A0,
            _VERSION_A1,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            _VERSION_B0,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/d0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            _VERSION_D0,
        ],
    )

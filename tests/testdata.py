import requests_mock

FILE_A0 = {
    "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "a0000000",
        "version_number": "1.2.3",
        "files": [
            {
                "hashes": {
                    "sha512": "a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                    "foo": "bar",
                },
                "foo": "bar",
            },
            {
                "hashes": {
                    "sha512": "a0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
        "foo": "bar",
    },
}
FILE_A1 = {
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
FILE_B0 = {
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
        "bar": "baz",
    },
}
FILE_B1 = {
    "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000": {  # noqa: E501
        "project_id": "b0000000",
        "version_number": "4.5.7",
        "files": [
            {
                "hashes": {
                    "sha512": "b1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                },
            },
        ],
    },
}
FILE_D0 = {
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

PROJECT_A = {
    "id": "a0000000",
    "title": "A",
    "slug": "a",
    "client_side": "optional",
    "server_side": "required",
    "license": {"id": "MIT"},
    "source_url": "S 1",
    "issues_url": "I 1",
}
PROJECT_B = {
    "id": "b0000000",
    "title": "B",
    "slug": "b",
}
PROJECT_D = {
    "id": "d0000000",
    "title": "D",
    "slug": "d",
}

VERSION_A0 = {
    "id": "A0000000",
    "project_id": "a0000000",
    "loaders": ["fabric"],
    "game_versions": ["1.19.2"],
    "foo": "bar",
}
VERSION_A1 = {
    "id": "A1000000",
    "project_id": "a0000000",
    "loaders": ["fabric", "minecraft"],
    "game_versions": ["1.20"],
}
VERSION_B0 = {
    "id": "B0000000",
    "project_id": "b0000000",
    "loaders": ["minecraft"],
    "game_versions": ["1.19.4"],
}
VERSION_B1 = {
    "id": "B1000000",
    "project_id": "b0000000",
    "loaders": ["forge"],
    "game_versions": ["1.20"],
}
VERSION_D0 = {
    "id": "D0000000",
    "project_id": "d0000000",
    "loaders": ["fabric"],
    "game_versions": ["1.19.4"],
}


def test1_list_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json=FILE_A0 | FILE_B0,
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
        complete_qs=True,
        json=[
            PROJECT_A,
            PROJECT_B,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            VERSION_A0,
            VERSION_A1,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            VERSION_B0,
        ],
    )


def test1_test2_diff_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json=FILE_A0 | FILE_A1 | FILE_B0 | FILE_D0,
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000", "d0000000"]',
        complete_qs=True,
        json=[
            PROJECT_A,
            PROJECT_B,
            PROJECT_D,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            VERSION_A0,
            VERSION_A1,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            VERSION_B0,
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/d0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            VERSION_D0,
        ],
    )

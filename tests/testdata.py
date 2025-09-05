import requests_mock


def test1_list_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json={
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
                            "sha512": "a1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # noqa: E501
                        },
                    },
                ],
            },
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
        },
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000"]',
        complete_qs=True,
        json=[
            {
                "id": "a0000000",
                "title": "A",
                "slug": "a",
                "client_side": "optional",
                "server_side": "required",
                "license": {"id": "MIT"},
                "source_url": "S",
                "issues_url": "I",
            },
            {
                "id": "b0000000",
                "title": "B",
                "slug": "b",
            },
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            {
                "id": "A0000000",
                "project_id": "a0000000",
                "loaders": ["fabric"],
                "game_versions": ["1.19.2"],
            },
            {
                "id": "A1000000",
                "project_id": "a0000000",
                "loaders": ["fabric", "minecraft"],
                "game_versions": ["1.20"],
            },
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            {
                "id": "B0000000",
                "project_id": "b0000000",
                "loaders": ["minecraft"],
                "game_versions": ["1.19.4"],
            },
        ],
    )


def test1_test2_diff_calls(m: requests_mock.Mocker) -> None:
    m.post(
        "https://api.modrinth.com/v2/version_files",
        json={
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
        },
    )
    m.get(
        'https://api.modrinth.com/v2/projects?ids=["a0000000", "b0000000", "d0000000"]',
        complete_qs=True,
        json=[
            {
                "id": "a0000000",
                "title": "A",
                "slug": "a",
                "client_side": "optional",
                "server_side": "required",
                "license": {"id": "MIT"},
                "source_url": "S",
                "issues_url": "I",
            },
            {
                "id": "b0000000",
                "title": "B",
                "slug": "b",
            },
            {
                "id": "d0000000",
                "title": "D",
                "slug": "d",
            },
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/a0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            {
                "id": "A0000000",
                "project_id": "a0000000",
                "loaders": ["fabric"],
                "game_versions": ["1.19.2"],
            },
            {
                "id": "A1000000",
                "project_id": "a0000000",
                "loaders": ["fabric", "minecraft"],
                "game_versions": ["1.20"],
            },
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/b0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            {
                "id": "B0000000",
                "project_id": "b0000000",
                "loaders": ["minecraft"],
                "game_versions": ["1.19.4"],
            },
        ],
    )
    m.get(
        'https://api.modrinth.com/v2/project/d0000000/version?loaders=["fabric", "minecraft"]',
        complete_qs=True,
        json=[
            {
                "id": "D0000000",
                "project_id": "d0000000",
                "loaders": ["fabric"],
                "game_versions": ["1.19.4"],
            },
        ],
    )

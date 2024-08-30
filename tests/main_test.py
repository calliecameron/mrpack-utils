import pytest
import requests_mock

from mrpack_utils.main import main


class TestMain:
    def test_list_normal(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "baz",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd",
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "wxyz",
                                },
                            },
                        ],
                    },
                    "fedc": {
                        "project_id": "quux",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc",
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["baz", "quux"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                        "client_side": "optional",
                        "server_side": "required",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                    {
                        "id": "quux",
                        "title": "Bar",
                        "slug": "bar",
                        "game_versions": ["1.19.4"],
                    },
                ],
            )
            main(["--csv", "list", "--check-version", "1.20", "testdata/test1.mrpack"])
            assert (
                capsys.readouterr().out
                == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20
modpack: Test Modpack,,1.1,,,,,
minecraft,,1.19.4,,,,,
fabric-loader,,0.16,,,,,
foo,,1,,,,,
Bar,https://modrinth.com/mod/bar,4.5.6,unknown,unknown,1.19.4,yes,no
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,no,yes
client-overrides/mods/baz-1.0.0.jar,unknown - probably CurseForge,a2c6f513,unknown,unknown,unknown,check manually,check manually
client-overrides/mods/foo-1.2.3.jar,unknown - probably CurseForge,d6902afc,unknown,unknown,unknown,check manually,check manually
overrides/mods/foo-1.2.3.jar,unknown - probably CurseForge,d6902afc,unknown,unknown,unknown,check manually,check manually
server-overrides/mods/bar-1.0.0.jar,unknown - probably CurseForge,7123eea6,unknown,unknown,unknown,check manually,check manually
overrides/config/foo.txt,non-mod file,7e3265a8,,,,,
server-overrides/config/bar.txt,non-mod file,04a2b3e9,,,,,
"""  # noqa: E501
            )

            main(["list", "--check-version", "1.20", "testdata/test1.mrpack"])
            assert (
                capsys.readouterr().out
                == """| Name                                | Link                          | Installed version   | On client   | On server   | Latest game version   | 1.19.4         | 1.20           |
|-------------------------------------|-------------------------------|---------------------|-------------|-------------|-----------------------|----------------|----------------|
| modpack: Test Modpack               |                               | 1.1                 |             |             |                       |                |                |
| minecraft                           |                               | 1.19.4              |             |             |                       |                |                |
| fabric-loader                       |                               | 0.16                |             |             |                       |                |                |
| foo                                 |                               | 1                   |             |             |                       |                |                |
| Bar                                 | https://modrinth.com/mod/bar  | 4.5.6               | unknown     | unknown     | 1.19.4                | yes            | no             |
| Foo                                 | https://modrinth.com/mod/foo  | 1.2.3               | required    | optional    | 1.20                  | no             | yes            |
| client-overrides/mods/baz-1.0.0.jar | unknown - probably CurseForge | a2c6f513            | unknown     | unknown     | unknown               | check manually | check manually |
| client-overrides/mods/foo-1.2.3.jar | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |
| overrides/mods/foo-1.2.3.jar        | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |
| server-overrides/mods/bar-1.0.0.jar | unknown - probably CurseForge | 7123eea6            | unknown     | unknown     | unknown               | check manually | check manually |
| overrides/config/foo.txt            | non-mod file                  | 7e3265a8            |             |             |                       |                |                |
| server-overrides/config/bar.txt     | non-mod file                  | 04a2b3e9            |             |             |                       |                |                |

Mods supposed to be on Modrinth, but not found:
  baz.jar

For version 1.19.4:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    Foo

For version 1.20:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    Bar
"""  # noqa: E501
            )

    def test_list_dev(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "baz",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd",
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "wxyz",
                                },
                            },
                        ],
                    },
                    "fedc": {
                        "project_id": "quux",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc",
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["baz", "quux"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                        "client_side": "optional",
                        "server_side": "required",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                    {
                        "id": "quux",
                        "title": "Bar",
                        "slug": "bar",
                        "game_versions": ["1.19.4"],
                    },
                ],
            )
            main(["--csv", "list", "--dev", "--check-version", "1.20", "testdata/test1.mrpack"])
            assert (
                capsys.readouterr().out
                == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20,License,Modrinth client,Modrinth server,Source,Issues
modpack: Test Modpack,,1.1,,,,,,,,,,
minecraft,,1.19.4,,,,,,,,,,
fabric-loader,,0.16,,,,,,,,,,
foo,,1,,,,,,,,,,
Bar,https://modrinth.com/mod/bar,4.5.6,unknown,unknown,1.19.4,yes,no,,unknown,unknown,,
Foo,https://modrinth.com/mod/foo,1.2.3,required,optional,1.20,no,yes,MIT,optional,required,example.com,example2.com
client-overrides/mods/baz-1.0.0.jar,unknown - probably CurseForge,a2c6f513,unknown,unknown,unknown,check manually,check manually,,,,,
client-overrides/mods/foo-1.2.3.jar,unknown - probably CurseForge,d6902afc,unknown,unknown,unknown,check manually,check manually,,,,,
overrides/mods/foo-1.2.3.jar,unknown - probably CurseForge,d6902afc,unknown,unknown,unknown,check manually,check manually,,,,,
server-overrides/mods/bar-1.0.0.jar,unknown - probably CurseForge,7123eea6,unknown,unknown,unknown,check manually,check manually,,,,,
overrides/config/foo.txt,non-mod file,7e3265a8,,,,,,,,,,
server-overrides/config/bar.txt,non-mod file,04a2b3e9,,,,,,,,,,
"""  # noqa: E501
            )

            main(["list", "--dev", "--check-version", "1.20", "testdata/test1.mrpack"])
            assert (
                capsys.readouterr().out
                == """| Name                                | Link                          | Installed version   | On client   | On server   | Latest game version   | 1.19.4         | 1.20           | License   | Modrinth client   | Modrinth server   | Source      | Issues       |
|-------------------------------------|-------------------------------|---------------------|-------------|-------------|-----------------------|----------------|----------------|-----------|-------------------|-------------------|-------------|--------------|
| modpack: Test Modpack               |                               | 1.1                 |             |             |                       |                |                |           |                   |                   |             |              |
| minecraft                           |                               | 1.19.4              |             |             |                       |                |                |           |                   |                   |             |              |
| fabric-loader                       |                               | 0.16                |             |             |                       |                |                |           |                   |                   |             |              |
| foo                                 |                               | 1                   |             |             |                       |                |                |           |                   |                   |             |              |
| Bar                                 | https://modrinth.com/mod/bar  | 4.5.6               | unknown     | unknown     | 1.19.4                | yes            | no             |           | unknown           | unknown           |             |              |
| Foo                                 | https://modrinth.com/mod/foo  | 1.2.3               | required    | optional    | 1.20                  | no             | yes            | MIT       | optional          | required          | example.com | example2.com |
| client-overrides/mods/baz-1.0.0.jar | unknown - probably CurseForge | a2c6f513            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |             |              |
| client-overrides/mods/foo-1.2.3.jar | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |             |              |
| overrides/mods/foo-1.2.3.jar        | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |             |              |
| server-overrides/mods/bar-1.0.0.jar | unknown - probably CurseForge | 7123eea6            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |             |              |
| overrides/config/foo.txt            | non-mod file                  | 7e3265a8            |             |             |                       |                |                |           |                   |                   |             |              |
| server-overrides/config/bar.txt     | non-mod file                  | 04a2b3e9            |             |             |                       |                |                |           |                   |                   |             |              |

Mods supposed to be on Modrinth, but not found:
  baz.jar

For version 1.19.4:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    Foo

For version 1.20:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    Bar
"""  # noqa: E501
            )

    def test_diff(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            m.post(
                "https://api.modrinth.com/v2/version_files",
                json={
                    "abcd": {
                        "project_id": "baz",
                        "version_number": "1.2.3",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd",
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "wxyz",
                                },
                            },
                        ],
                    },
                    "abcd2": {
                        "project_id": "baz",
                        "version_number": "1.2.4",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "abcd2",
                                },
                            },
                            {
                                "hashes": {
                                    "sha512": "wxyz2",
                                },
                            },
                        ],
                    },
                    "fedc": {
                        "project_id": "quux",
                        "version_number": "4.5.6",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "fedc",
                                },
                            },
                        ],
                    },
                    "lmno": {
                        "project_id": "blah",
                        "version_number": "1.0.0",
                        "files": [
                            {
                                "hashes": {
                                    "sha512": "lmno",
                                },
                            },
                        ],
                    },
                },
            )
            m.get(
                'https://api.modrinth.com/v2/projects?ids=["baz", "blah", "quux"]',
                complete_qs=True,
                json=[
                    {
                        "id": "baz",
                        "title": "Foo",
                        "slug": "foo",
                        "game_versions": ["1.19.2", "1.20"],
                        "client_side": "optional",
                        "server_side": "required",
                        "license": {"id": "MIT"},
                        "source_url": "example.com",
                        "issues_url": "example2.com",
                    },
                    {
                        "id": "blah",
                        "title": "Quux",
                        "slug": "quux",
                        "game_versions": ["1.19.4"],
                    },
                    {
                        "id": "quux",
                        "title": "Bar",
                        "slug": "bar",
                        "game_versions": ["1.19.4"],
                    },
                ],
            )

            main(["--csv", "diff", "testdata/test1.mrpack", "testdata/test2.mrpack"])
            assert (
                capsys.readouterr().out
                == """Name,Old,New
modpack version,1.1,1.2
fabric-loader,0.16,0.17
foo,1,2
Foo,1.2.3,1.2.4
Quux,,1.0.0
Bar,4.5.6,
client-overrides/mods/baz-1.0.0.jar,a2c6f513,d59e8961
overrides/mods/foo-1.2.4.jar,,99d1bc3b
overrides/mods/foo-1.2.3.jar,d6902afc,
server-overrides/config/bar.txt,04a2b3e9,a472c297
overrides/config/baz.txt,,cc7b39e1
overrides/config/foo.txt,7e3265a8,
"""
            )

            main(["diff", "testdata/test1.mrpack", "testdata/test2.mrpack"])
            assert (
                capsys.readouterr().out
                == """| Name                                | Old      | New      |
|-------------------------------------|----------|----------|
| modpack version                     | 1.1      | 1.2      |
| fabric-loader                       | 0.16     | 0.17     |
| foo                                 | 1        | 2        |
| Foo                                 | 1.2.3    | 1.2.4    |
| Quux                                |          | 1.0.0    |
| Bar                                 | 4.5.6    |          |
| client-overrides/mods/baz-1.0.0.jar | a2c6f513 | d59e8961 |
| overrides/mods/foo-1.2.4.jar        |          | 99d1bc3b |
| overrides/mods/foo-1.2.3.jar        | d6902afc |          |
| server-overrides/config/bar.txt     | 04a2b3e9 | a472c297 |
| overrides/config/baz.txt            |          | cc7b39e1 |
| overrides/config/foo.txt            | 7e3265a8 |          |

Mods supposed to be on Modrinth, but not found:
  baz.jar
"""
            )

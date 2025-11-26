from typing import TYPE_CHECKING

import requests_mock

from mrpack.main import main
from tests import testdata

if TYPE_CHECKING:
    import pytest

# ruff: noqa: S101


class TestMain:
    def test_list_normal(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_list_calls(m)

            main(["list", "--csv", "--check-version", "1.20", "testdata/test1.mrpack"])
            assert (
                capsys.readouterr().out
                == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20
modpack: Test Modpack,,1.1,,,,,
minecraft,,1.19.4,,,,,
fabric-loader,,0.16,,,,,
foo,,1,,,,,
A,https://modrinth.com/mod/a,1.2.3,required,optional,1.20,no,yes
B,https://modrinth.com/mod/b,4.5.6,unknown,unknown,1.19.4,yes,no
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
| A                                   | https://modrinth.com/mod/a    | 1.2.3               | required    | optional    | 1.20                  | no             | yes            |
| B                                   | https://modrinth.com/mod/b    | 4.5.6               | unknown     | unknown     | 1.19.4                | yes            | no             |
| client-overrides/mods/baz-1.0.0.jar | unknown - probably CurseForge | a2c6f513            | unknown     | unknown     | unknown               | check manually | check manually |
| client-overrides/mods/foo-1.2.3.jar | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |
| overrides/mods/foo-1.2.3.jar        | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |
| server-overrides/mods/bar-1.0.0.jar | unknown - probably CurseForge | 7123eea6            | unknown     | unknown     | unknown               | check manually | check manually |
| overrides/config/foo.txt            | non-mod file                  | 7e3265a8            |             |             |                       |                |                |
| server-overrides/config/bar.txt     | non-mod file                  | 04a2b3e9            |             |             |                       |                |                |

Modpack dependencies not corresponding to any known mod loader:
  foo

Mods supposed to be on Modrinth, but not found:
  c.jar

For version 1.19.4:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    A

For version 1.20:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    B
"""  # noqa: E501
            )

    def test_list_dev(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_list_calls(m)

            main(
                [
                    "list",
                    "--csv",
                    "--dev",
                    "--check-version",
                    "1.20",
                    "testdata/test1.mrpack",
                ],
            )
            assert (
                capsys.readouterr().out
                == """Name,Link,Installed version,On client,On server,Latest game version,1.19.4,1.20,License,Modrinth client,Modrinth server,Source,Issues
modpack: Test Modpack,,1.1,,,,,,,,,,
minecraft,,1.19.4,,,,,,,,,,
fabric-loader,,0.16,,,,,,,,,,
foo,,1,,,,,,,,,,
A,https://modrinth.com/mod/a,1.2.3,required,optional,1.20,no,yes,MIT,optional,required,S%201,I%201
B,https://modrinth.com/mod/b,4.5.6,unknown,unknown,1.19.4,yes,no,,unknown,unknown,,
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
                == """| Name                                | Link                          | Installed version   | On client   | On server   | Latest game version   | 1.19.4         | 1.20           | License   | Modrinth client   | Modrinth server   | Source   | Issues   |
|-------------------------------------|-------------------------------|---------------------|-------------|-------------|-----------------------|----------------|----------------|-----------|-------------------|-------------------|----------|----------|
| modpack: Test Modpack               |                               | 1.1                 |             |             |                       |                |                |           |                   |                   |          |          |
| minecraft                           |                               | 1.19.4              |             |             |                       |                |                |           |                   |                   |          |          |
| fabric-loader                       |                               | 0.16                |             |             |                       |                |                |           |                   |                   |          |          |
| foo                                 |                               | 1                   |             |             |                       |                |                |           |                   |                   |          |          |
| A                                   | https://modrinth.com/mod/a    | 1.2.3               | required    | optional    | 1.20                  | no             | yes            | MIT       | optional          | required          | S%201    | I%201    |
| B                                   | https://modrinth.com/mod/b    | 4.5.6               | unknown     | unknown     | 1.19.4                | yes            | no             |           | unknown           | unknown           |          |          |
| client-overrides/mods/baz-1.0.0.jar | unknown - probably CurseForge | a2c6f513            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |          |          |
| client-overrides/mods/foo-1.2.3.jar | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |          |          |
| overrides/mods/foo-1.2.3.jar        | unknown - probably CurseForge | d6902afc            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |          |          |
| server-overrides/mods/bar-1.0.0.jar | unknown - probably CurseForge | 7123eea6            | unknown     | unknown     | unknown               | check manually | check manually |           |                   |                   |          |          |
| overrides/config/foo.txt            | non-mod file                  | 7e3265a8            |             |             |                       |                |                |           |                   |                   |          |          |
| server-overrides/config/bar.txt     | non-mod file                  | 04a2b3e9            |             |             |                       |                |                |           |                   |                   |          |          |

Modpack dependencies not corresponding to any known mod loader:
  foo

Mods supposed to be on Modrinth, but not found:
  c.jar

For version 1.19.4:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    A

For version 1.20:
  1 out of 2 Modrinth mods are incompatible with this version (CurseForge mods must be checked manually):
    B
"""  # noqa: E501
            )

    def test_diff(self, capsys: pytest.CaptureFixture[str]) -> None:
        with requests_mock.Mocker() as m:
            testdata.test1_test2_diff_calls(m)

            main(["diff", "--csv", "testdata/test1.mrpack", "testdata/test2.mrpack"])
            assert (
                capsys.readouterr().out
                == """Name,Old,New
modpack version,1.1,1.2
fabric-loader,0.16,0.17
foo,1,2
A,1.2.3,1.2.4
D,,1.0.0
B,4.5.6,
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
| A                                   | 1.2.3    | 1.2.4    |
| D                                   |          | 1.0.0    |
| B                                   | 4.5.6    |          |
| client-overrides/mods/baz-1.0.0.jar | a2c6f513 | d59e8961 |
| overrides/mods/foo-1.2.4.jar        |          | 99d1bc3b |
| overrides/mods/foo-1.2.3.jar        | d6902afc |          |
| server-overrides/config/bar.txt     | 04a2b3e9 | a472c297 |
| overrides/config/baz.txt            |          | cc7b39e1 |
| overrides/config/foo.txt            | 7e3265a8 |          |

Modpack dependencies not corresponding to any known mod loader:
  foo

Mods supposed to be on Modrinth, but not found:
  c.jar
"""
            )

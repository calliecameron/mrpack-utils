from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version_hint")
    args = parser.parse_args(argv)

    # Make sure we're calling the global uv, in case a dependency installed a
    # different version of uv inside the virtualenv.
    uv = os.getenv("UV", "uv")

    j = json.loads(
        subprocess.run(
            [
                uv,
                "python",
                "list",
                "--output-format=json",
                f"cpython@{args.version_hint}",
            ],
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout,
    )

    versions = set()
    for version in [v["version"] for v in j]:
        if re.fullmatch(r"[1-9][0-9]*\.[0-9]+\.[0-9]+", version) is None:
            continue
        versions.add(tuple(int(part) for part in version.split(".")))

    if not versions:
        raise ValueError("Can't find a default python version")

    print(".".join(str(v) for v in sorted(versions, reverse=True)[0]))


if __name__ == "__main__":
    main()  # pragma: no cover

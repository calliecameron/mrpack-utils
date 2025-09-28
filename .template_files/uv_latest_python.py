import json
import re
import subprocess


def main() -> None:
    j = json.loads(
        subprocess.run(
            ["uv", "python", "list", "--output-format=json", "cpython"],
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout,
    )

    versions = set()
    for version in [v["version"] for v in j]:
        if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
            continue
        versions.add(tuple(int(part) for part in version.split(".")))

    if not versions:
        raise ValueError("Can't find a default python version")

    print(".".join(str(v) for v in sorted(versions, reverse=True)[0]))


if __name__ == "__main__":
    main()

import argparse
import json
import re
import tomllib
from collections.abc import Sequence


def extract_dep(dep: str) -> str:
    match = re.match(r"[a-zA-Z0-9_.-]+", dep)
    if match is None:
        raise ValueError(f"Failed to extract package name from '{dep}'")
    return match.group(0)


def extract_deps(deps: Sequence[str]) -> list[str]:
    return sorted({extract_dep(dep) for dep in deps})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdated_json")
    parser.add_argument("pyproject_toml")
    args = parser.parse_args()

    with open(args.outdated_json) as f:
        outdated_json = json.load(f)
    with open(args.pyproject_toml, mode="rb") as f:
        pyproject_toml = tomllib.load(f)

    deps = extract_deps(pyproject_toml["project"]["dependencies"])
    group_deps = {
        group: extract_deps(v)
        for (group, v) in pyproject_toml.get("dependency-groups", {}).items()
    }

    outdated = {item["name"]: item["latest_version"] for item in outdated_json}

    for dep in deps:
        if dep in outdated:
            print(f"{dep}=={outdated[dep]}")

    for group in sorted(group_deps):
        for dep in group_deps[group]:
            if dep in outdated:
                print(f"{dep}=={outdated[dep]} {group}")


if __name__ == "__main__":
    main()

#!/bin/bash

set -eu

if [ ! -e pyproject.toml ]; then
    echo 'Must be run in the root of the project' 2>&1
    exit 1
fi

uv sync

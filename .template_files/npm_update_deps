#!/bin/bash

set -eu

if [ ! -e package.json ]; then
    echo 'Must be run in the root of the project' 2>&1
    exit 1
fi

source "${NVM_DIR}/nvm.sh"
nvm use --save stable

# shellcheck disable=SC2016
nvm exec --silent npm outdated --parseable |
    cut -d : -f 4 |
    xargs bash -c 'source "${NVM_DIR}/nvm.sh" && nvm exec --silent npm install --save-exact "${@}"' --

rm -f package-lock.json
rm -rf node_modules
nvm exec --silent npm install

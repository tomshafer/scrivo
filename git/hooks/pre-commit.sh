#!/usr/bin/env bash

set -eu -o pipefail
[[ "${TRACE-0}" == "1" ]] && set -o xtrace

# https://stackoverflow.com/a/17841619
function join { local IFS="$1"; shift; echo "$*"; }
function lg { echo "$@" >&2; }

cd "$(dirname "$0")/../../"
lg "Running in directory $(pwd)"

toml="pyproject.toml"

# Skip if no package updates
if ! git diff --name-only HEAD | grep -qE '^scrivo/'; then
    exit
fi

# Skip if request no bump
if [[ ${NOBUMP-0} -gt 0 ]]; then
    exit
fi

# Update the version string
vstring="$(grep -E -m 1 '^version = "' "$toml" | grep -E -m 1 -o '[0-9.-]+')"
IFS='.-' read -r -a varray <<< "$vstring"  # https://stackoverflow.com/a/10586169

if [[ ${#varray[@]} -ne 4 ]]; then
    lg "Version number should have 4 elements."
    exit 1
fi

varray[3]=$((varray[3] + 1))
newvstring=$(join - "$(join . "${varray[@]::3}")" "${varray[3]}")

lg "Updating version = \"$vstring\" -> \"$newvstring\""

if sed -i.bak "s/^version.*$/version = \"$newvstring\"/1" $toml; then
    rm "$toml.bak"
    git add "$toml"
fi

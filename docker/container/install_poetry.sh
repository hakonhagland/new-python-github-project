#!/bin/bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
    echo "This script must be sourced, not run directly"
    exit 1
fi
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
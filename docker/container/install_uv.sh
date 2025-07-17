#!/bin/bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
    echo "This script must be sourced, not run directly"
    exit 1
fi

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
export PATH="$HOME/.cargo/bin:$PATH"

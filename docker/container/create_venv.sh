# source this file
if [[ "${BASH_SOURCE[0]}" == "${0}" ]] ; then
    echo "This script must be sourced, not run directly"
    exit 1
fi
python3 -m venv .venv
source .venv/bin/activate

#! /bin/bash

# This script should be called by running "make docker-image" in the
# root of the repository. After the image has been built, it can be
# run with "make docker-container".
#
# Builds the docker image from the current git HEAD. The docker image is
# tagged as "python-ghproj".

# Exit on error
set -e

if (( $# != 1 )); then
    echo "Usage: $0 <dockerdir>"
    exit 1
fi
# Check for unstaged, staged, and untracked files
git status
unstaged_changes=$(git diff --quiet; echo $?)
staged_changes=$(git diff --cached --quiet; echo $?)
untracked_files=$(git ls-files --others --exclude-standard)
if [[ $unstaged_changes -ne 0 || $staged_changes -ne 0 || -n $untracked_files ]]; then
    echo
    echo "Warning: You have unstaged or uncommitted changes, or untracked files."
    echo "These will not be included in the docker image."
    echo -n "Do you wish to continue with the build? (yes/no) "
    read answer
    if [[ $answer != "yes" ]]; then
        echo "Build aborted."
        exit 1
    fi
fi
dockerdir="$1"
#dir=$(mktemp -d)
dir="$dockerdir"
fn="myapp.tar.gz"
path="$dir"/myapp.tar.gz   # docker requires the file to be in the build context, so we put it there

# create a tar.gz archive of the current git HEAD that respects .gitignore
git archive -o "$path" --format=tar.gz HEAD
# pass the archive file to docker build as a build argument
docker build --build-arg "GIT_ARCH=$fn" --build-arg "DOCKER_DIR=$dockerdir" -t python-ghproj "$dockerdir"
rm "$path" # remove the archive file

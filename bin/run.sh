#!/bin/bash

function usage() {
cat <<EOF >&2
Usage: $0 <PROJECT_NAME>

  PROJECT_NAME: The name of the project to run. Default: sample
EOF
exit 1
}

args=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h | --help ) usage;;
    -* | --* ) echo "Unknown option: $1" >&2; exit 1;;
    *           ) args+=("$1");;
  esac
  shift
done

[ ${#args[@]} != 1 ] && usage

PROJECT_NAME="${args[0]}"

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
PROJECT_ROOT=$(cd $(dirname $0)/..; pwd)
cd "$PROJECT_ROOT"

docker build --rm \
  --build-arg PROJECT_NAME="$PROJECT_NAME" \
  -f docker/app/Dockerfile \
  -t "sls-tutorial/app/local:latest" .

docker run --rm -ti \
  --network host \
  -v "$PROJECT_ROOT/$PROJECT_NAME":/opt/app/api \
  -w /opt/app/api \
  "sls-tutorial/app/local:latest"
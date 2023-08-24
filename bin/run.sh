#!/bin/bash

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
PROJECT_ROOT=$(cd $(dirname $0)/..; pwd)
cd "$PROJECT_ROOT"

export LOCAL_UID=$(id -u)
export LOCAL_GID=$(id -g)

docker build --rm \
  --build-arg "host_uid=$LOCAL_UID" \
  --build-arg "host_gid=$LOCAL_GID" \
  -f docker/app/Dockerfile \
  -t "sls-tutorial/sample-app/dev:latest" .

docker run --rm -ti \
  --network host \
  --user app \
  -e "API_GATEWAY_BASE_PATH=/" \
  -w /opt/app/api \
  "sls-tutorial/sample-app/dev:latest"
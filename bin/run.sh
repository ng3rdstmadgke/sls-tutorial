#!/bin/bash

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
PROJECT_ROOT=$(cd $(dirname $0)/..; pwd)
cd "$PROJECT_ROOT"

docker build --rm \
  -f docker/app/Dockerfile \
  -t "sls-tutorial/sample-app/dev:latest" .

docker run --rm -ti \
  --network host \
  -e "API_GATEWAY_BASE_PATH=/" \
  -v "$PROJECT_ROOT/sample-app":/opt/app/api \
  -w /opt/app/api \
  "sls-tutorial/sample-app/dev:latest"
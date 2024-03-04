#!/bin/bash

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
PROJECT_ROOT=$(cd $(dirname $0)/..; pwd)
cd "$PROJECT_ROOT"

docker build --rm \
  -f docker/app/Dockerfile \
  -t "sls-tutorial/app/local:latest" .

docker run --rm -ti \
  --network host \
  -v "$PROJECT_ROOT/app":/opt/app/api \
  -w /opt/app/api \
  "sls-tutorial/app/local:latest"
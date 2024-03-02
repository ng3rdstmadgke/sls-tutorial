#!/bin/bash
set -e

cd ${CONTAINER_PROJECT_ROOT}/sample-app
uvicorn main:app --reload --port 8787
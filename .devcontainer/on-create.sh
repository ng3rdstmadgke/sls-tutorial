#!/bin/bash

echo "=== === === === === === ls -alF === === === === === ==="
ls -alF
echo "=== === === === === === pwd === === === === === ==="
pwd

SCRIPT_DIR=$(cd $(dirname $0); pwd)

cat <<EOF >> ~/.bashrc

source ${SCRIPT_DIR}/.bashrc_private
EOF
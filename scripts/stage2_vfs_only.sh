#!/bin/sh
# Этап 2: задан только путь к VFS.
cd "$(dirname "$0")/.." || exit 1
echo "== только --vfs =="
./run.sh --vfs /tmp/some/vfs.zip

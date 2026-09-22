#!/bin/sh
# Этап 2: заданы все параметры.
cd "$(dirname "$0")/.." || exit 1
echo "== --vfs и --script =="
./run.sh --vfs "/tmp/my vfs.zip" --script examples/stage2.emu

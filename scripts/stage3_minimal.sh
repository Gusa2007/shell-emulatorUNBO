#!/bin/sh
# Этап 3: минимальная VFS (только motd).
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== минимальная VFS =="
./run.sh --vfs build/vfs/minimal.zip --script examples/stage3.emu

#!/bin/sh
# Этап 4: проверка команд ls, cd, who, history на VFS deep.
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== ls, cd, who, history =="
./run.sh --vfs build/vfs/deep.zip --script examples/stage4.emu

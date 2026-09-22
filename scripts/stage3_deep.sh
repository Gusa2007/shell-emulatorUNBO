#!/bin/sh
# Этап 3: VFS с деревом не менее 3 уровней.
cd "$(dirname "$0")/.." || exit 1
"${PYTHON:-python3}" tools/make_vfs.py || exit 1
echo "== глубокое дерево =="
./run.sh --vfs build/vfs/deep.zip --script examples/stage3.emu

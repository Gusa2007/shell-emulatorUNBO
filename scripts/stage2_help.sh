#!/bin/sh
# Этап 2: справка по параметрам и неизвестный параметр.
cd "$(dirname "$0")/.." || exit 1
echo "== --help =="
./run.sh --help
echo "== неизвестный параметр =="
./run.sh --unknown

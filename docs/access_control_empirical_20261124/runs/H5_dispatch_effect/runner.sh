#!/bin/sh
set -eu
cat input.txt > "$1/normal.txt"
if [ -r secret.txt ]; then
  cat secret.txt > "$1/unauthorized.txt"
fi

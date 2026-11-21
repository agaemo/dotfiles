#!/bin/sh
# PreToolUse hook: Bash — 危険なコマンドをブロックする
# exit 0 → 許可 / exit 2 → ブロック
#
# git reset --hard・git push --force 等は、迂回されにくい permissions.deny（settings.json）に移した。
# ここには、deny のパターンで表せないものだけを残す。
input=$(cat)

block() {
  printf 'pre-bash フックによりブロックされました: %s\n' "$1" >&2
  exit 2
}

echo "$input" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+/' && block 'rm -rf /'
echo "$input" | grep -qiE 'DROP[[:space:]]+TABLE' && block 'DROP TABLE'
echo "$input" | grep -qE '>[[:space:]]*\.env' && block '> .env'

exit 0

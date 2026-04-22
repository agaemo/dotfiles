#!/bin/bash
# dotfiles を dotfiles リポジトリにコピーするスクリプト

set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Syncing dotfiles to $DOTFILES_DIR ..."

cp ~/.config/nvim/init.lua "$DOTFILES_DIR/neovim/init.lua"
echo "  ✓ neovim/init.lua"

cp ~/.config/ghostty/config "$DOTFILES_DIR/ghostty/config"
echo "  ✓ ghostty/config"

cp ~/.claude/CLAUDE.md "$DOTFILES_DIR/claude/CLAUDE.md"
echo "  ✓ claude/CLAUDE.md"

cp ~/.claude/statusline-command.sh "$DOTFILES_DIR/claude/statusline-command.sh"
echo "  ✓ claude/statusline-command.sh"

# ~/.claude/commands/ 内のファイル・ディレクトリをシムリンクで管理
mkdir -p "$DOTFILES_DIR/claude/commands"
mkdir -p ~/.claude/commands
for entry in "$DOTFILES_DIR/claude/commands/"*; do
  [ -e "$entry" ] || continue
  target=~/.claude/commands/$(basename "$entry")
  if [ ! -L "$target" ]; then
    ln -sf "$entry" "$target"
    echo "  ✓ symlinked $(basename "$entry")"
  else
    echo "  - skipped $(basename "$entry") (already linked)"
  fi
done

echo "Done."

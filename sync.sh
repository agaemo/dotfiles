#!/bin/bash
# dotfiles リポジトリからローカルに反映するスクリプト

set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Syncing dotfiles from $DOTFILES_DIR ..."

mkdir -p ~/.config/nvim
cp "$DOTFILES_DIR/neovim/init.lua" ~/.config/nvim/init.lua
echo "  ✓ neovim/init.lua"

mkdir -p ~/.config/ghostty
cp "$DOTFILES_DIR/ghostty/config" ~/.config/ghostty/config
echo "  ✓ ghostty/config"

cp "$DOTFILES_DIR/claude/CLAUDE.md" ~/.claude/CLAUDE.md
echo "  ✓ claude/CLAUDE.md"

cp "$DOTFILES_DIR/claude/statusline-command.sh" ~/.claude/statusline-command.sh
echo "  ✓ claude/statusline-command.sh"

# ~/.claude/commands/ 内のファイル・ディレクトリをシンボリックリンクで管理
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

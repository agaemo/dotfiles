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

# ~/.claude/commands/ 内のファイルをシムリンクで管理
mkdir -p "$DOTFILES_DIR/.claude/commands"
mkdir -p ~/.claude/commands
for f in "$DOTFILES_DIR/.claude/commands/"*.md; do
  [ -e "$f" ] || continue
  target=~/.claude/commands/$(basename "$f")
  if [ ! -L "$target" ]; then
    ln -sf "$f" "$target"
    echo "  ✓ symlinked $(basename "$f")"
  fi
done

echo "Done."

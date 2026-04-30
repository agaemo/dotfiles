#!/bin/bash
# dotfiles リポジトリからローカルに反映するスクリプト

set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

sync_neovim() {
  mkdir -p ~/.config/nvim
  cp "$DOTFILES_DIR/neovim/init.lua" ~/.config/nvim/init.lua
  echo "  ✓ neovim/init.lua"
}

sync_ghostty() {
  mkdir -p ~/.config/ghostty
  cp "$DOTFILES_DIR/ghostty/config" ~/.config/ghostty/config
  echo "  ✓ ghostty/config"
}

sync_claude() {
  cp "$DOTFILES_DIR/claude/CLAUDE.md" ~/.claude/CLAUDE.md
  echo "  ✓ claude/CLAUDE.md"

  cp "$DOTFILES_DIR/claude/statusline-command.sh" ~/.claude/statusline-command.sh
  echo "  ✓ claude/statusline-command.sh"
}

sync_skills() {
  mkdir -p "$DOTFILES_DIR/claude/commands"
  mkdir -p ~/.claude/commands
  for entry in "$DOTFILES_DIR/claude/commands/"*; do
    [ -e "$entry" ] || continue
    [ "$(basename "$entry")" = "README.md" ] && continue
    target=~/.claude/commands/$(basename "$entry")
    if [ ! -L "$target" ]; then
      ln -sf "$entry" "$target"
      echo "  ✓ symlinked $(basename "$entry")"
    else
      echo "  - skipped $(basename "$entry") (already linked)"
    fi
  done
}

sync_all() {
  echo "Syncing dotfiles from $DOTFILES_DIR ..."
  sync_neovim
  sync_ghostty
  sync_claude
  sync_skills
  echo "Done."
}

case "${1:-}" in
  all)
    sync_all
    ;;
  neovim)
    sync_neovim
    ;;
  ghostty)
    sync_ghostty
    ;;
  claude)
    sync_claude
    ;;
  skills)
    sync_skills
    ;;
  "")
    read -rp "全体を同期しますか？ [y/N] " answer
    case "$answer" in
      [yY]|[yY][eE][sS])
        sync_all
        ;;
      *)
        echo "キャンセルしました。"
        exit 0
        ;;
    esac
    ;;
  *)
    echo "使い方: $0 [all|neovim|ghostty|claude|skills]"
    exit 1
    ;;
esac

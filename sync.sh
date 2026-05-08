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

cleanup_old_commands() {
  # 旧 ~/.claude/commands 以下のシンボリックリンクと、commands ディレクトリ自体を削除
  if [ -L ~/.claude/commands ]; then
    rm ~/.claude/commands
    echo "  ✓ removed symlink ~/.claude/commands"
  elif [ -d ~/.claude/commands ]; then
    for entry in ~/.claude/commands/*; do
      [ -L "$entry" ] && rm "$entry"
    done
    rmdir ~/.claude/commands 2>/dev/null && echo "  ✓ removed dir ~/.claude/commands" || true
  fi
}

sync_skills() {
  cleanup_old_commands
  mkdir -p ~/.claude/skills
  for skill_dir in "$DOTFILES_DIR/claude/skills/"*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    [ "$skill_name" = "README.md" ] && continue
    target=~/.claude/skills/$skill_name
    if [ ! -L "$target" ]; then
      ln -sfn "$skill_dir" "$target"
      echo "  ✓ symlinked $skill_name"
    else
      echo "  - skipped $skill_name (already linked)"
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

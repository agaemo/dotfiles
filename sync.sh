#!/bin/bash
# dotfiles を dotfiles リポジトリにコピーするスクリプト

set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Syncing dotfiles to $DOTFILES_DIR ..."

cp ~/.config/nvim/init.lua "$DOTFILES_DIR/neovim/init.lua"
echo "  ✓ neovim/init.lua"

echo "Done."

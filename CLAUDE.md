# dotfiles

## ファイル編集後の同期

以下のファイルを編集した場合、編集後に `sync.sh` を実行してローカルへ反映すること。

| リポジトリ内のファイル | 同期先 | sync.sh の対象名 |
|---|---|---|
| `neovim/init.lua` | `~/.config/nvim/init.lua` | `neovim` |
| `ghostty/config` | `~/.config/ghostty/config` | `ghostty` |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | `claude` |
| `claude/statusline-command.sh` | `~/.claude/statusline-command.sh` | `claude` |

### 実行例

```bash
# 変更したファイルに対応する対象を指定
./sync.sh neovim
./sync.sh ghostty
./sync.sh claude

# 全体をまとめて同期
./sync.sh all
```

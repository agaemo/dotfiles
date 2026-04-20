# dotfiles

個人設定ファイルの管理リポジトリ。

## 前提条件

| ツール | 用途 | インストール |
|--------|------|-------------|
| `jq` | Claude Code ステータスライン | `brew install jq` |

## 同期方法

設定を変更したら以下を実行してこのリポジトリに反映する。

```bash
./sync.sh
```

> Windows では動作しない。Mac / Linux のみ対応。

## 設定一覧

| ディレクトリ | 対象ツール | 詳細 |
|-------------|-----------|------|
| [neovim/](neovim/README.md) | Neovim | プラグイン・キーマップ |
| [ghostty/](ghostty/config) | Ghostty | テーマ・フォント・ウィンドウ設定 |
| [claude/](claude/) | Claude Code | グローバル設定・ステータスライン |

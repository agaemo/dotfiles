# claude/

Claude Code のグローバル設定ディレクトリ。`~/.claude/` にシンボリックリンクされる。

## 構成

| ファイル / ディレクトリ | 説明 |
|------------------------|------|
| [`CLAUDE.md`](CLAUDE.md) | 全プロジェクト共通のグローバル指示（言語・コメント規約・コミット規約など） |
| [`statusline-command.sh`](statusline-command.sh) | Claude Code ステータスラインのカスタム表示スクリプト |
| [`commands/`](commands/README.md) | カスタムスラッシュコマンド定義 |

## ステータスライン

`statusline-command.sh` は Claude Code のステータスバーに以下を表示する:

- 現在のディレクトリ名・Gitブランチ
- 使用モデル名
- コンテキストウィンドウ使用率（バーチャート）
- 5時間・7日のレートリミット使用率と残り時間

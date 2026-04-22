# claude/commands

Claude Code のカスタムスラッシュコマンド定義ディレクトリ。
`~/.claude/commands/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| [`/new-project`](new-project.md) | 新規プロジェクトディレクトリを作成し、Claude ハーネス一式をセットアップする |

## 使い方

Claude Code のチャットで `/` + コマンド名を入力するだけで実行できる。

```
/new-project my-api
```

## コマンドの追加方法

このディレクトリに `<command-name>.md` を追加し、`sync.sh` を実行する。
フロントマターで `name` と `description` を設定すること。

```markdown
---
name: command-name
description: コマンドの説明
---

# /command-name

...
```

# claude/commands

Claude Code のカスタムスラッシュコマンド定義ディレクトリ。
`~/.claude/commands/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| [`/new-project`](new-project.md) | アプリ・API・管理画面など動的機能を持つプロジェクトにハーネス一式をセットアップする |
| [`/new-lp`](new-lp.md) | LP・静的ページを Astro + Node.js で新規作成する。`/new-project` の LP 特化版（デザインファースト、intake / planner 不要） |

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

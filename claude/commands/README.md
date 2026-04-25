# claude/commands

Claude Code のカスタムスラッシュコマンド定義ディレクトリ。
`~/.claude/commands/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| [`/new-project`](new-project.md) | アプリ・API・管理画面など動的機能を持つプロジェクトにハーネス一式をセットアップする |
| [`/new-lp`](new-lp.md) | LP・静的ページを Astro + Node.js で新規作成する。`/new-project` の LP 特化版（デザインファースト、intake / planner 不要） |
| [`/lp-publish`](lp-publish.md) | LP を本番公開するための準備・手順をガイドする。ホスティング・ドメイン・SEO ファイルの知識がなくても進められる |
| [`/improve-skill`](improve-skill.md) | スキルファイルを静的解析・実行シミュレーションで改善する |
| [`/improve-agent`](improve-agent.md) | エージェントファイルを静的解析・実行シミュレーションで改善する |

## 使い方

Claude Code のチャットで `/` + コマンド名を入力するだけで実行できる。

```
/new-project
/improve-agent agents/planner.md
```

## コマンドの追加方法

このディレクトリに `<command-name>.md` を追加するだけで利用可能になる
（`~/.claude/commands/` へのシンボリックリンクが張られているため再起動不要）。
フロントマターで `name` と `description` を設定すること。

```markdown
---
name: command-name
description: コマンドの説明
---

# /command-name

...
```

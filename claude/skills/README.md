# claude/skills

Claude Code のカスタムスキル定義ディレクトリ。
`~/.claude/skills/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## スキル一覧

| スキル | 説明 |
|--------|------|
| [`/new-project`](new-project/SKILL.md) | アプリ・API・管理画面など動的機能を持つプロジェクトにハーネス一式をセットアップする |
| [`/new-static`](new-static/SKILL.md) | LP・PoC・静的ページを Astro + Node.js で新規作成する。`/new-project` の静的特化版（デザインファースト、intake / planner 不要） |
| [`/lp-publish`](lp-publish/SKILL.md) | LP を本番公開するための準備・手順をガイドする。ホスティング・ドメイン・SEO ファイルの知識がなくても進められる |
| [`/issue-triage`](issue-triage/SKILL.md) | GitHub issue番号を渡すと対応方針を検討し、承認を得てから修正・PR作成まで行う |
| [`/improve-skill`](improve-skill/SKILL.md) | スキルファイルを静的解析・実行シミュレーションで改善する |
| [`/improve-agent`](improve-agent/SKILL.md) | エージェントファイルを静的解析・実行シミュレーションで改善する |

## 使い方

Claude Code のチャットで `/` + スキル名を入力するだけで実行できる。

```
/new-project
/improve-agent agents/planner.md
```

## スキルの追加方法

`<skill-name>/SKILL.md` を追加するだけで利用可能になる
（`~/.claude/skills/` へのシンボリックリンクが張られているため再起動不要）。
フロントマターで `name` と `description` を設定すること。

```markdown
---
name: skill-name
description: スキルの説明
---

# /skill-name

...
```

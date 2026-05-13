# claude/skills

Claude Code のカスタムスキル定義ディレクトリ。
`~/.claude/skills/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## スキル一覧

| スキル | 説明 |
|--------|------|
| [`/new-project`](new-project/SKILL.md) | 新規プロジェクトをセットアップする。起動時に静的サイト（LP・PoC）か動的アプリ（API・DB・認証あり）かを選択する |
| [`/lp-publish`](lp-publish/SKILL.md) | LP を本番公開するための準備・手順をガイドする。ホスティング・ドメイン・SEO ファイルの知識がなくても進められる |
| [`/issue-triage`](issue-triage/SKILL.md) | issue番号なしで呼ぶと一覧表示・選択、番号指定で直接トリアージ。承認を得てから修正・PR作成まで行う |
| [`/improve-skill`](improve-skill/SKILL.md) | スキルファイルを静的解析・実行シミュレーションで改善する |
| [`/improve-agent`](improve-agent/SKILL.md) | エージェントファイルを静的解析・実行シミュレーションで改善する |

## 使い方

Claude Code のチャットで `/` + スキル名を入力するだけで実行できる。

```
/new-project
/improve-agent agents/planner.md
```

## スキルの追加方法

1. `claude/skills/<skill-name>/SKILL.md` を作成する
2. `sync.sh skills` を実行して `~/.claude/skills/` にシンボリックリンクを張る
3. Claude Code を再起動せずそのまま `/skill-name` で呼び出せる

フロントマターで `name` と `description` を設定すること。

```markdown
---
name: skill-name
description: スキルの説明
---

# /skill-name

...
```

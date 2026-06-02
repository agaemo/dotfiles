# claude/skills

Claude Code のカスタムスキル定義ディレクトリ。
`~/.claude/skills/` にシンボリックリンクされ、どのプロジェクトからでも利用できる。

## スキル一覧

| スキル | 説明 |
|--------|------|
| [`/craft`](craft/) | システム開発に関する部品集。新規立ち上げ・維持保守・移行など開発全工程のフローを包含する |
| [`/think`](think/) | 入力の intent に応じて ideate / scamper / six-hats / triz / first-principles へ委譲する思考・分析オーケストレーター |
| [`/retrofit`](retrofit/) | テストが少ない・ない既存システムへのテスト追加ワークフロー。Characterization Test・Seam 導入・TDD 移行を段階的に進める |
| [`/runbook`](runbook/) | 開発タスク（本番デプロイ・DB移行・インシデント対応など）を渡すと航空SOP方式の読み上げ式チェックリストを生成する |
| [`/lp-publish`](lp-publish/) | LP を本番公開するための準備・手順をガイドする。ホスティング・ドメイン・SEO ファイルの知識がなくても進められる |
| [`/issue-triage`](issue-triage/) | issue番号なしで呼ぶと一覧表示・選択、番号指定で直接トリアージ。承認を得てから修正・PR作成まで行う |
| [`/improve-skill`](improve-skill/) | スキルファイルを静的解析・実行シミュレーションで改善する |
| [`/improve-agent`](improve-agent/) | エージェントファイルを静的解析・実行シミュレーションで改善する |
| [`/trade-roshi`](trade-roshi/) | 投資道場の老師として株式銘柄を分析・裁定する（エンタメ用途・投資助言ではない） |

## 使い方

Claude Code のチャットで `/` + スキル名を入力するだけで実行できる。

```
/craft
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

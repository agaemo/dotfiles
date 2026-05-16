---
name: craft
description: システム開発に関する部品集。新規立ち上げ・移行など開発全工程のフローを包含する。新規作成か既存プロジェクトの移行かを選択して対応する手順に委譲する。
---

# /craft

システム開発に関する作業を開始する。

## 手順

### ステップ 0: 種別選択

```
ASK USER: どの作業を行いますか？
  1. 静的サイトを新規作成（LP・PoC・画面モック。API / DB / 認証不要）
  2. 動的アプリを新規作成（API・DB・認証など動的機能あり）
  3. 既存プロジェクトの移行（DB・認証基盤・ライブラリ・ランタイム等の刷新）

WAIT_FOR: ユーザーの選択

IF 1（静的サイト）:
  READ ~/.claude/skills/craft/flows/new-static/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 2（動的アプリ）:
  READ ~/.claude/skills/craft/flows/new-project/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 3（移行）:
  READ ~/.claude/skills/craft/flows/migrate/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
```

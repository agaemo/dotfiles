---
name: craft
description: システム開発に関する部品集。新規立ち上げ・維持保守・移行など開発全工程のフローを包含する。静的サイト（LP・PoC）か動的アプリ（API・DB・認証あり）かを選択して対応する手順に委譲する。
---

# /craft

カレントディレクトリに新規プロジェクトをセットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 手順

### ステップ 0: 種別選択

```
ASK USER: どちらを作成しますか？
  1. 静的サイト（LP・PoC・画面モック。API / DB / 認証不要）
  2. 動的アプリ（API・DB・認証など動的機能あり）

WAIT_FOR: ユーザーの選択

IF 静的サイト:
  READ ~/.claude/skills/craft/flows/new-static/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 動的アプリ:
  READ ~/.claude/skills/craft/flows/new-project/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
```

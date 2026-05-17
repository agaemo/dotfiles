---
name: craft
description: システム開発に関する部品集。新規立ち上げ・移行など開発全工程のフローを包含する。新規作成か既存プロジェクトの移行かを選択して対応する手順に委譲する。
---

# /craft

システム開発に関する作業を開始する。

## 手順

### ステップ 0: 種別選択

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの絶対パス
  # 例: /Users/alice/.claude/skills/craft
  # このファイルを読んだパスから導出すること

ASK USER: どの作業を行いますか？
  1. 静的サイトを新規作成（LP・PoC・画面モック。API / DB / 認証不要）
  2. Webアプリを新規作成（Node.js系。API・DB・認証など動的機能あり）
  3. クロスプラットフォームアプリを新規作成（Flutter・React Native・Expo等）
  4. 既存システムの相談（課題整理・移行検討・品質改善・リファクタ等）

WAIT_FOR: ユーザーの選択

IF 1（静的サイト）:
  READ {SKILL_DIR}/flows/new-static/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 2（Webアプリ）:
  READ {SKILL_DIR}/flows/new-project/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 3（クロスプラットフォームアプリ）:
  READ {SKILL_DIR}/flows/new-app/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない

IF 4（相談）:
  READ {SKILL_DIR}/flows/consult/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
```

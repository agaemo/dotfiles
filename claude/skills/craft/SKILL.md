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

IF .craft/plan.md が存在する:
  SUGGEST: 「.craft/plan.mdが見つかりました。実装を再開しますか？」と提案する
  IF ユーザーが再開を選択:
    FOLLOW: 実装再開フロー（このファイル末尾）
    STOP: 以降のステップは実行しない

ASK USER: どの作業を行いますか？
  1. 静的サイトを新規作成（LP・PoC・画面モック。API / DB / 認証不要）
  2. Webアプリを新規作成（Node.js系。API・DB・認証など動的機能あり）
  3. クロスプラットフォームアプリを新規作成（Flutter・React Native・Expo等）
  4. 既存システムの相談（課題整理・移行検討・品質改善・リファクタ等）
  5. 実装を再開（.craft/plan.md が既にある）

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
  STOP: 以降のステップは実行しない

IF 5（実装再開）:
  FOLLOW: 実装再開フロー（このファイル末尾）
  STOP: 以降のステップは実行しない
```

---

## 実装再開フロー

`.craft/plan.md` が存在する状態から実装を続ける場合の汎用手順。
フレームワーク固有の注意点は各フローファイルを参照すること。

```
1. READ .craft/plan.md
2. READ .craft/design-system.md（存在すれば）
3. 完了状況を確認してユーザーに提示する:
   - 完了済みのステップ（対応するコード・ファイルが存在するか確認）
   - 未着手のステップ
   - 外部依存で未接続のもの（Firebase・外部API・認証基盤等）
4. 未着手のステップを plan.md の順番で実装する
5. 外部依存が未接続の場合はモックで実装し、CLAUDE.md に接続手順を記録する
6. 各ステップ完了後にビルド確認を行う
   - Flutter:        mise exec -- flutter analyze
   - Node.js / Web: mise exec -- pnpm build
   - 静的サイト:     mise exec -- pnpm build
```

---
name: craft
description: 新規プロジェクト（静的サイト・Webアプリ・モバイルアプリ）の立ち上げ、または既存システムの移行・リファクタ相談を開始するときに呼び出す。
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
  ELSE:
    # 再開しない → scope へ
  ENDIF

READ {SKILL_DIR}/flows/scope/SKILL.md
FOLLOW: そこに記述されたすべての手順を実行する
  NOTE: 種別の推定・確認・new-static/new-project/new-app/consult への振り分けは
        すべて scope フロー側で行われる。
STOP: 以降のステップは実行しない

```

NOTE: scope フロー（または scope が委譲した先のフロー）の FOLLOW 実行中にエラーや予期しない STOP が
  発生した場合は、中断した箇所と理由をユーザーに伝え、再試行するか（同じ種別を選択 / 別の種別を選ぶ）確認すること。

---

## 実装再開フロー

`.craft/plan.md` が存在する状態から実装を続ける場合は、build フローに委譲する。
初回実装（各 new-xxx フローの設計完了後）と同じエンジンを使うため、手順の二重管理がない。

```
READ {SKILL_DIR}/flows/build/SKILL.md
FOLLOW: そこに記述されたすべての手順を実行する
  NOTE: STACK・HAS_REVIEW_CHAIN・HAS_FRONTEND は呼び出し元変数が無いため
        build フロー内で自動判定される（pubspec.yaml・design-brief.md 等の有無から推定）
```

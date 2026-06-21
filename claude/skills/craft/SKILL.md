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
    # 再開しない → 以降の推定ロジックへ
  ENDIF

# 会話の文脈から種別を推定する（ユーザーに聞き直さない）
INFER kind FROM 直前の会話内容:
  キーワード例:
    1（静的サイト）  → LP・ランディングページ・PoC・画面モック・静的
    2（Webアプリ）   → API・DB・認証・バックエンド・Next.js・サーバー・チャット・管理画面
    3（アプリ）      → Flutter・React Native・Expo・iOS・Android・スマホアプリ
    4（相談）        → 移行・改善・リファクタ・相談・課題・既存
    5（再開）        → 再開・続き・続ける

IF kind が明確に推定できる:
  CONFIRM: 「〇〇（種別名）で進めますか？」と一言確認する
  IF ユーザーが否定した:
    READ {SKILL_DIR}/flows/scope/SKILL.md
    FOLLOW: そこに記述されたすべての手順を実行する
    STOP: 以降のステップは実行しない
  ENDIF
ELSE:
  READ {SKILL_DIR}/flows/scope/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP: 以降のステップは実行しない
ENDIF

NOTE: いずれの子スキルでも FOLLOW 実行中にエラーや予期しない STOP が発生した場合は、
  中断した箇所と理由をユーザーに伝え、再試行するか（同じ種別を選択 / 別の種別を選ぶ）確認すること。

# 種別 → フローファイルの対応
# | 種別                     | フローファイル                                       |
# |--------------------------|------------------------------------------------------|
# | 1（静的サイト）           | {SKILL_DIR}/flows/new-static/SKILL.md                |
# | 2（Webアプリ）            | {SKILL_DIR}/flows/new-project/SKILL.md               |
# | 3（クロスプラットフォーム）| {SKILL_DIR}/flows/new-app/SKILL.md                   |
# | 4（相談）                 | {SKILL_DIR}/flows/consult/SKILL.md                   |
# | 5（実装再開）             | このファイル末尾の「実装再開フロー」                   |
#
# NOTE: 種別が推定できない場合・確認が否定された場合は scope フロー
#       （{SKILL_DIR}/flows/scope/SKILL.md）が上記IF/ELSEで既に処理しており、
#       このテーブル・以降のIF文には到達しない。

IF kind != 5:
  READ 上記テーブルの対応フローファイル（{SKILL_DIR}は導出済みの絶対パスに展開すること）
  IF READ FAILED:
    REPORT: "フローファイルが見つかりません: {path}。SKILL_DIR の導出を確認してください。"
    STOP
  FOLLOW: そこに記述されたすべての手順を実行する
ELSE:
  FOLLOW: 実装再開フロー（このファイル末尾）
ENDIF
STOP: 以降のステップは実行しない

```

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

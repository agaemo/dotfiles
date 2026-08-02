---
name: craft
description: 新規プロジェクト（静的サイト・Webアプリ・モバイルアプリ）の立ち上げ、既存システムの移行・リファクタ相談の開始、または中断していた実装の再開時に呼び出す。
---

# /craft

システム開発に関する作業を開始する。

## 実行時の一般原則（craft 配下の全フロー・全エージェントに適用）

IMPORTANT: **内部変数名をユーザーに見せない。** `STACK`・`HAS_FRONTEND`・`HAS_REVIEW_CHAIN` 等の
制御変数は、進捗報告・完了報告・確認メッセージなどユーザー向けの出力に変数名のまま
含めないこと。「HAS_FRONTEND=true のため〜」ではなく「フロントエンドがあるため〜」のように、
常に人間が読める言葉に変換してから伝える。

## 手順

### ステップ 0: 種別選択

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの絶対パス
  # 例: /Users/alice/.claude/skills/craft
  # このファイルを読んだパスから導出すること

IF .craft/plan.md が存在する:
  # plan.md は初期設計ドキュメント。「既存実装の再開」か「新しい要件」かを明示的に確認する
  GATE: 「.craft/plan.mdが見つかりました。今回の依頼はどちらですか？」とユーザーに確認する
    選択肢:
      1. plan.md の実装を続ける（中断した実装の再開）
      2. plan.md とは別の新しい要件として進める（fix ファイルを新規作成）
  WAIT_FOR: ユーザーの選択
  IF ユーザーが 1（再開）を選択:
    FOLLOW: 実装再開フロー（本ファイルの「## 実装再開フロー」セクション）
    STOP: 以降のステップは実行しない
  ELSE:
    # 新しい要件として扱う（fix ファイルの作成・plan.md への追記は consult フローの
    # ステップ4で行われる。ここでは何もしない）
    CONTINUE: 下記のscope読み込みへ進む
  ENDIF
ENDIF
# .craft/plan.md がそもそも存在しない場合も、そのまま下記のscope読み込みへ継続する

READ {SKILL_DIR}/flows/scope/SKILL.md
IF READ FAILED:
  REPORT: "フローファイルが見つかりません: {SKILL_DIR}/flows/scope/SKILL.md。SKILL_DIR の導出を確認してください。"
  STOP
FOLLOW: そこに記述されたすべての手順を実行する
  NOTE: 種別の推定・確認・new-static/new-project/new-app/consult への振り分けは
        すべて scope フロー側で行われる。
STOP: 以降のステップは実行しない

```

NOTE: FOLLOW 実行中にエラーや予期しない STOP が発生した場合は、中断した箇所と理由をユーザーに伝え、
  再試行するか確認すること。選択肢は失敗した文脈に応じて提示する:
  - scope フロー（または委譲先フロー）の失敗時: 同じ種別を選択 / 別の種別を選ぶ / 中止する
  - 実装再開フロー（build フロー）の失敗時: 再試行する / 再開を中止する

---

## 実装再開フロー

（本セクションはステップ0の分岐からのみ到達する。SKILL_DIR はステップ0で定義済みの値をそのまま使う）

`.craft/plan.md` が存在する状態から実装を続ける場合は、build フローに委譲する。
初回実装（各 new-xxx フローの設計完了後）と同じエンジンを使うため、手順の二重管理がない。

```
READ {SKILL_DIR}/flows/build/SKILL.md
IF READ FAILED:
  REPORT: "フローファイルが見つかりません: {SKILL_DIR}/flows/build/SKILL.md。SKILL_DIR の導出を確認してください。"
  STOP
FOLLOW: そこに記述されたすべての手順を実行する
  NOTE: STACK・HAS_REVIEW_CHAIN・HAS_FRONTEND は呼び出し元変数が無いため
        build フロー内で自動判定される（pubspec.yaml・design-brief.md 等の有無から推定。
        判定ロジックの詳細は {SKILL_DIR}/flows/build/SKILL.md の AUTO-DETECT を参照）
```

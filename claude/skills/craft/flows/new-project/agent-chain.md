---
name: new-project-agent-chain
description: new-project セットアップ完了後の設計フェーズ・エージェントチェーン（STEP 1-7、STEP7はbuildフローへ委譲）・オプションエージェント・Node.js 再開時注意点
---

# 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。

> **IMPORTANT — PROHIBITED:** `intake`・`designer` を Agent ツール（サブエージェント）で起動すること
> 理由: ユーザーとの対話が必要。スキルとして呼び出すか、メインClaude自身が担当すること。

```
# HAS_FRONTEND はステップ1で設定済みの変数（このチェーン全体で参照する）
# true  → STEP 3（デザイン）・STEP 8（実画面レビュー）を実施
# false → STEP 3・STEP 8をスキップ
```

NOTE: 各 GATE で承認を求める前に以下の形式で進捗を必ず表示すること（N はフロントあり5・なし4）:
  ── 承認 [N/N]: <文書名> ──────────────────────
  ✅ STEP 1: requirements.md（承認済み）
  👉 STEP 2: stories.md（承認待ち）
  ⬜ STEP 3: デザイン（未着手）
  ──────────────────────────────────────────

```
STEP 1: intake
  OUTPUT: .craft/requirements.md
  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

STEP 2: refiner
  INPUT:  .craft/requirements.md
  OUTPUT: .craft/stories.md
  NOTE: 未解決の疑問はユーザーから回答を得た後も削除しない。
        以下の形式でチェック済みにして残すこと（意思決定の根拠として保持）:
        - [x] [疑問の内容]
              → **回答（YYYY-MM-DD）:** [回答内容]
  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

IF HAS_FRONTEND == true:
  STEP 3: designer ← 省略禁止・planner より先に実施すること
    a. designer エージェントを呼び出す（内蔵の「テンプレート: デザインブリーフ」を使用） → .craft/design-brief.md
    b. designer エージェントを呼び出す（内蔵の「テンプレート: デザインシステム」を使用） → .craft/design-system.md
    c. 画面構成・コンポーネント構成を .craft/design.md に記録
    GATE: 承認進捗を表示してからユーザーに提示し、承認を得ること
    PROHIBITED: デザイン承認前にコンポーネントを1行も書くこと
    NOTE: デザインによってAPIの形・DBフィールドが変わる場合があるため、planner より前に確定させること
ENDIF

STEP 4: planner
  INPUT:  .craft/stories.md（+ .craft/design-brief.md があれば）
  OUTPUT: .craft/plan.md
  NOTE: 呼び出し前に「planner へ渡すべき設計判断の確認事項」を参照し、ユーザーに確認すること
        → READ {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md
  GATE: 承認進捗を表示してからユーザーに計画を提示し、承認を得ること
  PROHIBITED: 承認前に実装を開始すること

STEP 5: 理解度チェック（Early Stop）← 統合設計書生成前の確認ゲート

  REPEAT:
    SELF_EVALUATE: 以下の5項目を 1〜5 で採点する
      スケール: 1=全く不明 / 2=断片的 / 3=概ね把握 / 4=ほぼ確信 / 5=完全に理解

      | # | 評価項目                                                 | スコア |
      |---|----------------------------------------------------------|--------|
      | 1 | 目的・ゴール（何を達成するプロジェクトか）                |        |
      | 2 | ユーザー・利用シーン（誰が・どう使うか）                  |        |
      | 3 | 主要機能・要件（何を作るか、スコープの境界線）            |        |
      | 4 | 技術的制約・設計判断（認証・DB・API など後から変えにくい部分）|     |
      | 5 | 完了条件・受け入れ基準（何をもって完成とするか）          |        |

    IF ANY(score < 4):
      ASK USER: スコアが4未満の項目について不明点を質問する
    ENDIF
  UNTIL ALL(score >= 4)

STEP 6: 統合設計書生成 ← 理解度確認後の総合確認ゲート

  目的: バラバラに承認してきた要求・要件・設計を1つの整合した文書群として出力し、
       「これで開発を始めてよい」と判断できる状態にする。

  READ {SKILL_DIR}/flows/new-project/templates.md  ← 3つのテンプレートが定義されている（SKILL_DIR はファイル先頭で定義済み）

  生成する3文書:
    a. templates.md の「テンプレート: 要求定義書」を参照 → .craft/01_requirements_doc.md
       入力: .craft/requirements.md
    b. templates.md の「テンプレート: 要件定義書」を参照 → .craft/02_specifications_doc.md
       入力: .craft/stories.md
    c. templates.md の「テンプレート: 基本設計書」を参照 → .craft/03_basic_design_doc.md
       入力: .craft/plan.md（+ .craft/design-system.md があれば）

  GATE: 3文書を生成後、以下の形式でユーザーに一括提示し、承認を得ること:

    ── 承認 [5/5]: 統合設計書（最終確認） ─────────────
    ✅ STEP 1: requirements.md
    ✅ STEP 2: stories.md
    ✅ STEP 3: デザイン
    ✅ STEP 4: plan.md
    👉 STEP 5: 統合設計書（承認待ち）
    ──────────────────────────────────────────────

    以下の3文書の内容を確認してください。これらの内容で開発を開始します。

    📄 要求定義書 → .craft/01_requirements_doc.md
    📄 要件定義書 → .craft/02_specifications_doc.md
    📄 基本設計書 → .craft/03_basic_design_doc.md

    （各文書の概要サマリーをここに記載する）

    承認いただけましたか？

  PROHIBITED: 3文書の承認前に実装を開始すること
  NOTE: 文書の内容に矛盾が見つかった場合は、該当する元ドキュメント（requirements.md 等）を修正してから再生成すること

STEP 7: build フローへ委譲

  READ {SKILL_DIR}/flows/build/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
    STACK = "node"
    HAS_REVIEW_CHAIN = true
    HAS_FRONTEND = <このチェーン冒頭で設定済みの変数>

  NOTE: 実装（フェーズ1〜3 or シンプルループ）・designerによる実画面レビュー・
        /ultrareview・レビューチェーン（verify→security-reviewer→qa→code-reviewer）・
        CLAUDE.md/README.md生成は build フロー側で実行される。
```

---

## オプションエージェント（必要に応じて追加）

| エージェント | 用途 |
|-------------|------|
| `ideator` | 何を作るか決まっていないときのアイデア探索 |
| `debugger` | 複雑なデバッグ（エラーの根本原因特定） |
| `tester` | テストコードの自動実装 |
| `scorer` | コードベース健全性の定期評価 |

---

## Node.js / Webアプリ固有の再開時注意点

汎用の実装フロー（初回実装・再開共通）は `{SKILL_DIR}/flows/build/SKILL.md` に定義されている。
Node.js 系プロジェクトで再開する際は以下を追加で確認すること。

```
- .env ファイルが存在するか確認する:
    存在しない → .env.example をもとに作成が必要かユーザーに確認する
- DBマイグレーション状態を確認する:
    `pnpm db:migrate` 等のマイグレーションコマンドが未実行でないか確認する
    スキーマと実際のDBがずれている場合はマイグレーションを先に実行する
- ビルド確認コマンドは `mise exec -- pnpm build` を使う
- `node_modules/` が存在しない場合は `mise exec -- pnpm install` を先に実行する
```

---
name: new-project-agent-chain
description: new-project セットアップ完了後の設計フェーズ・エージェントチェーン（STEP 1-7、STEP7はbuildフローへ委譲）・オプションエージェント・Node.js 再開時注意点
---

# 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。

> **IMPORTANT — PROHIBITED:** `intake`・`designer` を Agent ツール（サブエージェント）で起動すること
> 理由: ユーザーとの対話が必要。スキルとして呼び出すか、メインClaude自身が担当すること。

```
# SKILL_DIR は呼び出し元（new-project/SKILL.md 等）で定義済みの絶対パス（craftディレクトリを指す）。
# このファイル自身では定義しない。
# HAS_FRONTEND は呼び出し元（new-project/SKILL.md ステップ1、または new-app/SKILL.md ステップ1）で
# 設定済みの変数（このチェーン全体で参照する）。このファイル自身のSTEP1（intake）では設定されない。
# true  → STEP 3（デザイン）・build フロー内の実画面レビューを実施
# false → STEP 3・実画面レビューをスキップ
```

NOTE: 各 GATE で承認を求める前に以下の形式で進捗を必ず表示すること（N はフロントあり5・なし4）:
  ── 承認 [N/N]: <文書名> ──────────────────────
  ✅ STEP 1: requirements.md（承認済み）
  👉 STEP 2: stories.md（承認待ち）
  ⬜ STEP 3: デザイン（未着手）
  ──────────────────────────────────────────
  NOTE: HAS_FRONTEND == false の場合は「STEP 3: デザイン」の行を省き、Nは4に読み替える

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
       INCLUDE: 画面遷移（どの画面からどの画面へ・何をトリガーに遷移するか）を
                表または箇条書きで明記すること（例: 一覧画面 → [詳細を開く] → 詳細画面）
                → 基本設計書の画面遷移図はこの記録を元に生成する

    d. プレビュー生成（GATEの前に必ず実施）:
       READ {SKILL_DIR}/flows/new-project/preview-generation.md（このプレビュー生成チェーン中に
       未読の場合のみ。セッションが変わった場合は再度READする。共通ルール・CDN方針・
       ASSERT/失敗時の代替導線が定義されている）
       .craft/design-brief.md・.craft/design-system.md の内容から、
       カラーパレット（実際のスウォッチ）・タイポグラフィスケール・ブランドアーキタイプ・
       FEEL/ANTI-FEELワードを1枚にまとめる
         - ライト/ダーク両テーマに対応する
         - 治療は実務資料（memo/plan相当）: 誇張したヒーロー等は避け、パレット・タイポの実物大提示を主目的にする
       出力先: .craft/design-preview.html

    GATE: 承認進捗を表示してからユーザーに提示し、承認を得ること
    PROHIBITED: デザイン承認前にコンポーネントを1行も書くこと
    NOTE: デザインによってAPIの形・DBフィールドが変わる場合があるため、planner より前に確定させること
ENDIF

STEP 4: planner ← 基本設計を含む場合、このGATEが実質的な基本設計承認になる（DBスキーマ・API設計・セキュリティ設計を含む）
  INPUT:  .craft/stories.md（+ .craft/design-brief.md・.craft/design.md があれば）
  OUTPUT: .craft/plan.md
  NOTE: 呼び出し前に「planner へ渡すべき設計判断の確認事項」を参照し、ユーザーに確認すること
        → READ {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md
        IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md" → STOP

  プレビュー生成（GATEの前に必ず実施）:
    READ {SKILL_DIR}/flows/new-project/preview-generation.md（このプレビュー生成チェーン中に
    未読の場合のみ。セッションが変わった場合は再度READする。共通ルール・CDN方針・
    ASSERT/失敗時の代替導線が定義されている）
    .craft/plan.md の内容から以下を作成する:

    （「基本設計」セクションがある場合の追加提示。下記フィーチャートラックの有無とは独立に判定する）
    IF 「基本設計」セクションがある:
      DBスキーマ設計（テーブル一覧・リレーション）・API設計（エンドポイント一覧）・
      画面遷移図（ボックス＋矢印）・セキュリティ設計（脅威と対策）を提示する
    ENDIF

    IF 「フィーチャートラック設計」セクションがある:
      レビュートラック(A/B/C)バッジ・フェーズ1(クリティカルパス)の手順（番号付き縦リスト）・
      フェーズ2の並列トラック（カード形式・トラックごとに色分け）とその担当ファイル範囲・
      フェーズ1→フェーズ2への依存関係の分岐線を図解する
    ELSE:
      レビュートラック・実装ステップ・使用ライブラリ・リスクを整理して提示する
    ENDIF

    - 治療は実務資料（plan相当）: 図解による理解のしやすさを優先し、誇張した装飾は避ける
    出力先: .craft/plan-preview.html

  GATE: 承認進捗を表示してからユーザーに計画を提示し、承認を得ること
    NOTE: DB・API・認証を伴う場合、ここでDBスキーマ・API設計・セキュリティ設計が確定する。
          以降のSTEP6は、この内容を文書として整形するのみで新たな設計判断は行わない。
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

  目的: STEP 1〜4で既に承認済みの要求・要件・基本設計（DBスキーマ・API設計・
       セキュリティ設計・画面遷移を含む）を1つの整合した文書群として出力し、
       「これで開発を始めてよい」と判断できる状態にする。
  IMPORTANT: このSTEPで新たな設計判断を行わないこと。plan.md の「基本設計」セクションに
       ない内容（DBスキーマ・API設計等）が必要になった場合は、STEP4に戻って
       planner に追記させ、再承認を得ること。

  READ {SKILL_DIR}/flows/new-project/templates.md  ← 3つのテンプレートが定義されている（SKILL_DIR はファイル先頭で定義済み）
  IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/new-project/templates.md" → STOP

  生成する3文書:
    a. templates.md の「テンプレート: 要求定義書」を参照 → .craft/01_requirements_doc.md
       入力: .craft/requirements.md
    b. templates.md の「テンプレート: 要件定義書」を参照 → .craft/02_specifications_doc.md
       入力: .craft/stories.md
    c. templates.md の「テンプレート: 基本設計書」を参照 → .craft/03_basic_design_doc.md
       入力: .craft/plan.md の「基本設計」セクション（DBスキーマ・API設計・画面遷移図・
       セキュリティ設計を転記するのみ）+ design-system.md があれば

  プレビュー生成（GATEの前に必ず実施）:
    READ {SKILL_DIR}/flows/new-project/preview-generation.md（このプレビュー生成チェーン中に
    未読の場合のみ。セッションが変わった場合は再度READする。共通ルール・CDN方針・
    ASSERT/失敗時の代替導線が定義されている）
    3文書（01_requirements_doc.md・02_specifications_doc.md・03_basic_design_doc.md）を
    1枚のHTMLにまとめる。個別ファイルのまま提示すると3つを行き来して頭の中で
    統合する手間が残るため、必ず1枚に統合すること。
      - レイアウト: 左にセクションナビ（要求定義書 / 要件定義書 / 基本設計書 + 各文書内の見出しへのジャンプ）、
        右に本文（読みやすい行長・見出し階層を維持したまま各Markdownの内容を反映する）
      - 冒頭に「STEP 1〜4は承認済み、これが最終確認」であることが伝わる進捗表示を入れる
      - 基本設計書の「画面遷移図」セクションは、plan.md の「基本設計 > 画面遷移図」をそのまま
        転記して箱＋矢印で図解する（design.md へは戻らない。plan-preview.htmlと同様の方針）
      - 治療は文書（読み物）: 長文を読ませる前提のタイポグラフィ・余白を優先し、装飾は最小限にする
    出力先: .craft/spec-review.html

  GATE: 以下の形式でユーザーに一括提示し、承認を得ること:

    ── 承認 [N/N]: 統合設計書（最終確認） ─────────────
    ✅ STEP 1: requirements.md
    ✅ STEP 2: stories.md
    ✅ STEP 3: デザイン（HAS_FRONTEND == false の場合は省き、Nを4に読み替える）
    ✅ STEP 4: plan.md
    👉 STEP 5: 統合設計書（承認待ち）
    ──────────────────────────────────────────────

    以下の内容を確認してください（.craft/spec-review.html）。これらの内容で開発を開始します。

    承認いただけましたか？

  PROHIBITED: 3文書の承認前に実装を開始すること
  NOTE: 文書の内容に矛盾が見つかった場合は、該当する元ドキュメント（requirements.md 等）を修正してから再生成し、
        .craft/spec-review.html も再生成すること

STEP 7: build フローへ委譲

  READ {SKILL_DIR}/flows/build/SKILL.md
  IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/build/SKILL.md" → STOP
  FOLLOW: そこに記述されたすべての手順を実行する
    STACK = "node"
    HAS_REVIEW_CHAIN = true
    HAS_FRONTEND = <このチェーン冒頭で設定済みの変数>

  NOTE: 実装（フェーズ1〜3 or シンプルループ）・designerによる実画面レビュー・
        /ultrareview・レビューチェーン（plan.mdのレビュートラックA/B/Cに応じて
        verify→code-reviewer 〜 verify→security-reviewer→qa→code-reviewer→adversarial-reviewer）・
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

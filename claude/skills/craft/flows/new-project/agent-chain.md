---
name: new-project-agent-chain
description: new-project セットアップ完了後のエージェントチェーン（STEP 1-11）・オプションエージェント・Node.js 再開時注意点
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

STEP 7: 実装

  > **テスト戦略（フェーズ1開始前に決定すること）:**
  >
  > フェーズ1の実装を始める前に `tester` エージェントを呼び出してテスト環境をセットアップすること
  > （tester が vitest / pytest のセットアップ手順を案内する。Node.js のデフォルトは vitest 推奨）。
  > 後付けでテスト環境を追加するとモック設計が困難になり、テストの書けないコードが残る。
  >
  > | 対象 | 方針 | 理由 |
  > |------|------|------|
  > | API ルート・ミドルウェア・認証ロジック | **TDD 必須** | DBバグ・認証バイパスの温床。後から追加しにくい |
  > | DBクエリ・マイグレーション | **TDD 必須** | スキーマ変更後に追加すると既存動作の担保が取れない |
  > | バリデーション・状態遷移関数 | **TDD 必須** | 境界値バグが本番で発覚しやすく、修正コストが高い |
  > | その他のビジネスロジック関数 | TDD 推奨 | ロジックの複雑度に応じて判断 |
  > | UI コンポーネント | 任意 | 実画面確認で代替可能 |
  > | サーバーレスエッジ関数 | ローカルエミュレーターで統合テスト | ユニットテストでは実行環境を再現できない |
  > | WebSocket・リアルタイムイベント | 統合テスト推奨 | イベントループの非同期性がユニットテストでは再現困難 |
  > | 外部API連携 | モックで単体テスト | 実APIへの依存を排除してFastを保つ |
  >
  > TDD 必須の層を実装するときは `tester` エージェントを「TDDモード」で先に呼び出すこと。
  > `tester` が Red（失敗）を確認したら実装に進み、Green になったら次の層へ。
  >
  > バグが見つかった場合は**フェーズを問わず**後述の Bug-fix TDD 手順で修正すること。
  > （フェーズ1・2・3いずれでも同じ手順を使う。詳細はフェーズ3を参照）

  .craft/plan.md の「フィーチャートラック設計」セクションを読んでから実装を開始すること。
  トラック設計がある場合は以下の3フェーズで進める。
  トラック設計がない場合（小規模）は「フェーズ1のみ・逐次確認サイクル」で進める。

  ---

  ### フェーズ1: クリティカルパス（シリアル）

  .craft/plan.md の「フェーズ1」ステップを順番に実装する。
  各ステップ完了ごとに `mise exec -- pnpm build` で型エラーがないことを確認する。

  フェーズ1完了後:
    1. `mise exec -- pnpm dev` を起動し、ログイン〜基本ナビゲーションが動作することを確認する
    2. バグが見つかった場合は Bug-fix TDD 手順（フェーズ3参照）で修正してから commit すること
    3. 問題なければフェーズ1の成果を git commit する（フェーズ2の起点になる）

  ```bash
  git add -p  # 変更を確認しながらステージング
  git commit -m "フェーズ1: クリティカルパス実装完了"
  # 実際に実装した内容に合わせてメッセージを調整すること
  ```

  ---

  ### フェーズ2: 並列フィーチャートラック（worktree 分離）

  .craft/plan.md の「フェーズ2」に定義された各トラックを、
  **isolation: "worktree" + run_in_background: true** でバックグラウンド並列実行する。

  各トラックに渡すプロンプト:
  READ {SKILL_DIR}/flows/new-project/phase2-prompt.md  ← フェーズ2開始直前に読む
  （テンプレート内の [TRACK_NAME]・[ABSOLUTE_PATH] 等を実際の値に展開してから渡すこと）

  全トラック完了後:
    FOR EACH completed_track:
      1. worktree で作成されたブランチの差分を確認する
      2. main ブランチにマージする
      3. コンフリクトがあれば解消する
      4. `mise exec -- pnpm build` で統合ビルドを確認する

  ---

  ### フェーズ3: 統合確認

  全トラックのマージ完了後:
    1. `mise exec -- pnpm dev` を起動する
    2. 主要フローを実機で確認する（一覧→登録→詳細→操作→ダッシュボード）
    3. バグが見つかった場合は以下の **Bug-fix TDD** 手順で修正すること:
       a. `tester` エージェントを「バグ修正TDDモード」で呼び出し、バグを再現するテストを書く
       b. テストが Red（失敗）になることを確認する（再現できない場合は再現手順を精査する）
       c. バグを修正する
       d. テストが Green になることを確認する
       e. 補完モードで `tester` を再度呼び出してリグレッションテストを追加する
       ⚠️ PROHIBITED: テストを書かずに直接修正すること（同じバグが再発しても検出できなくなる）
    4. `git commit` で統合完了を記録する

  フェーズ3完了後に STEP 10 のレビューチェーン（verify → security-reviewer → qa → code-reviewer）へ進む。

IF HAS_FRONTEND == true:
  STEP 8: designer による実画面レビュー
    RUN: Puppeteer MCP でスクリーンショットを撮影
    CHECK: デザインブリーフ・デザインシステムとの差異を確認・修正

  STEP 9: /ultrareview（公式スキル・オプション）
    IF /ultrareview が利用可能:
      RUN: /ultrareview
    ELSE:
      SKIP → STEP 10 へ
    CHECK: コンポーネント設計・アクセシビリティ・型安全性
ENDIF

STEP 10: verify → security-reviewer → qa → code-reviewer

STEP 11: CLAUDE.md・README.md 生成 + クリーンアップ
  実装完了後、確定したスタック・コマンド・構造をもとに生成する。
  （実装前に生成するとプレースホルダーになるため、このタイミングで行う）

  CLAUDE.md に含めること:
    - プロジェクト名・目的（1〜2文）
    - スタック（実際に使う言語・フレームワーク・主要ライブラリ）
    - 開発コマンド（dev / test / build の実際のコマンド）
    - アーキテクチャ（採用パターン名・ディレクトリ構造のポイント・レイヤー間の依存の向き）
    - プロジェクト固有の制約（DBエンジン・実行環境の制限など）
    - .craft/plan.md を参照するよう一言書く
    上限: 60行以内

  README.md に含めること:
    - 概要（1〜2文）
    - 前提条件（mise・Node・pnpm の実際のバージョン）
    - セットアップ手順（git clone 〜 依存インストール 〜 .env 設定）
    - コマンド一覧（dev / test / build / migrate など）
    - 環境変数（キー名と説明のみ。実際の値は書かない）

  --- public/ クリーンアップ（HAS_FRONTEND == true の場合） ---

  IF HAS_FRONTEND == true:
    FOREACH file IN [vercel.svg, next.svg, window.svg, file.svg, globe.svg]:
      IF EXISTS(public/<file>):
        IF NOT REFERENCED IN src/:
          DELETE public/file
        ENDIF
      ENDIF
    ENDFOREACH
    NOTE: 要件検討中にロゴ等を public/ に置いている場合があるため、参照チェックを必ず行ってから削除すること
  ENDIF
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

汎用の実装再開フローは `/craft` の `SKILL.md` に定義されている。
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

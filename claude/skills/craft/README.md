# craft

システム開発に関する部品集。新規プロジェクト立ち上げ・既存システムの相談・各種フローを包含する。
`/craft` スキルで起動し、作業種別を選択して対応するフローに委譲する。

---

## /craft 起動フロー

```mermaid
flowchart TD
    START([/craft 起動]) --> DETECT{.craft/plan.md\n存在する?}
    DETECT -->|Yes| SUGGEST["「実装を再開しますか？」と提案"]
    SUGGEST -->|再開する| RESUME[実装再開フロー\nSKILL.md に定義]
    SUGGEST -->|しない| INFER
    DETECT -->|No| INFER

    INFER{種別を推定できる?\n会話の文脈から}
    INFER -->|Yes| CONFIRM["「〇〇で進めますか？」と確認"]
    CONFIRM -->|承認| DIRECT{種別}
    CONFIRM -->|否定| SCOPE
    INFER -->|No| SCOPE[scope フロー\n要件・制約をヒアリングして振り分け]

    DIRECT -->|1. 静的サイト| STATIC[new-static フロー]
    DIRECT -->|2. Webアプリ| DYNAMIC[new-project フロー]
    DIRECT -->|3. クロスプラットフォームアプリ| APP[new-app フロー]
    DIRECT -->|4. 既存システムの相談| CONSULT[consult フロー]

    SCOPE -->|既存システムの相談と判明| CONSULT
    SCOPE -->|静的サイトと判定| STATIC
    SCOPE -->|Webアプリと判定| DYNAMIC
    SCOPE -->|クロスプラットフォームと判定| APP
    SCOPE -->|対応レシピなし\nGAS等・TODO| TODO[未実装を報告\n近いカテゴリで妥協 or 終了]

    STATIC --> END_S([完了])
    DYNAMIC --> END_D([完了])
    APP --> END_A([完了])
    CONSULT --> END_C([完了])
    RESUME --> END_R([完了])
    TODO --> END_T([終了])
```

---

<details>
<summary>技術カテゴリ選定（scope）フロー</summary>

```mermaid
flowchart TD
    START([scope 起動]) --> S1["STEP 1: 相談の入口\n自由に話してもらう"]
    S1 --> EXIST{既存システムの\n相談?}
    EXIST -->|Yes| CONSULT[consult フローへ]
    EXIST -->|No| S2["STEP 2: 制約のヒアリング\nUI・DB認証・既存エコシステム依存・\n運用期間・技術知識レベル"]
    S2 --> S3["STEP 3: カテゴリ対応表と照合"]
    S3 --> MATCH{マッチする\nカテゴリ}
    MATCH -->|実装済み| GATE{ユーザー承認}
    MATCH -->|TODO\nGAS等| TODOR["未実装を報告"]
    TODOR --> COMPROMISE{近いカテゴリで\n妥協する?}
    COMPROMISE -->|Yes| GATE
    COMPROMISE -->|No| END_T([終了])
    GATE -->|承認| S4["STEP 4: 委譲"]
    GATE -->|否定| S3B[対応表から\n直接選んでもらう]
    S3B --> S4
    S4 --> STATIC[new-static]
    S4 --> DYNAMIC[new-project]
    S4 --> APP[new-app]
    CONSULT --> END_C([完了])
    STATIC --> END_S([完了])
    DYNAMIC --> END_D([完了])
    APP --> END_A([完了])
```

</details>

---

<details>
<summary>静的サイト（new-static）フロー</summary>

```mermaid
flowchart TD
    START([静的サイトを選択]) --> S1

    subgraph DESIGN["設計フェーズ（メインClaude が対話）"]
        S1["STEP 1: ヒアリング\n業種・ページ構成・色・フォント・\n参考デザイン・FEEL/ANTI-FEEL を\n1メッセージで質問"]
        S1 --> S1B["デザインブリーフ生成\n→ docs/design-brief.md"]
        S1B --> S2["STEP 2: 理解度チェック\n5項目すべて ≥4 になるまでループ"]
        S2 --> GATE{承認}
    end

    GATE -->|承認| S3

    subgraph SETUP["セットアップ（サブエージェント）"]
        S3["STEP 3:\nmise → Astro プロジェクト作成\n→ ファイル書き出し\n→ settings.json\n→ git init\n→ pnpm build 確認"]
    end

    S3 --> S4["STEP 4: CLAUDE.md・README.md 生成"]
    S4 --> S5["STEP 5: 完了報告"]
    S5 --> IMPL

    subgraph IMPL["実装フェーズ（セクション単位で繰り返す）"]
        direction LR
        IA["セクションを実装\n.astro コンポーネント"] --> IB["pnpm dev で表示確認"]
        IB --> IC{OK?}
        IC -->|問題あり| IA
        IC -->|OK| ID["次のセクションへ"]
        ID --> IA
    end

    IMPL --> REVIEW["全セクション完了後\nPuppeteer スクリーンショットで最終確認"]
    REVIEW --> END([完了])
```

</details>

<details>
<summary>動的アプリ（new-project）フロー</summary>

```mermaid
flowchart TD
    START([動的アプリを選択]) --> SETUP

    SETUP["ハーネスセットアップ\n（サブエージェント）\n.gitignore / .mcp.json / hooks/ / settings.json"]
    SETUP --> MISE["mise.toml 作成 → mise install"]
    MISE --> S1

    subgraph DESIGN["ウォーターフォール設計フェーズ（承認ゲートあり）"]
        S1["STEP 1: intake\n→ docs/working/requirements.md"]
        S1 -->|承認 1/5| S2
        S2["STEP 2: refiner\n→ docs/working/stories.md"]
        S2 -->|承認 2/5| S3_CHECK

        S3_CHECK{フロントあり?}
        S3_CHECK -->|Yes| S3["STEP 3: designer\n→ docs/working/design-brief.md\n→ docs/working/design-system.md"]
        S3 -->|承認 3/5| S4
        S3_CHECK -->|No| S4

        S4["STEP 4: planner\n→ docs/working/plan.md\n（クリティカルパス + 並列トラック定義）"]
        S4 -->|承認 4/5| S45
        S45["STEP 4.5: 理解度チェック\n（5項目すべて ≥4 になるまでループ）"]
        S45 --> S5
    end

    S5["STEP 5: 統合設計書生成\n→ docs/01_requirements_doc.md\n→ docs/02_specifications_doc.md\n→ docs/03_basic_design_doc.md"]
    S5 -->|承認 5/5| S6

    subgraph IMPL["実装フェーズ（3フェーズ）"]
        S6["STEP 6: 実装"]

        subgraph PH1["Phase 1: シリアル・クリティカルパス"]
            PH1A["DB スキーマ・認証基盤\nAppShell・共通コンポーネント"]
            PH1A --> PH1B["pnpm dev で動作確認\n→ git commit"]
        end

        subgraph PH2["Phase 2: 並列トラック（worktree 分離）"]
            direction LR
            TA["Agent: track-A\nisolation: worktree\nbackground: true"]
            TB["Agent: track-B\nisolation: worktree\nbackground: true"]
            TC["Agent: track-C\nisolation: worktree\nbackground: true"]
        end

        subgraph PH3["Phase 3: 統合"]
            PH3A["各ブランチをマージ\nコンフリクト解消"]
            PH3A --> PH3B["pnpm dev で実機確認\n→ git commit"]
        end

        S6 --> PH1A
        PH1B --> TA & TB & TC
        TA & TB & TC --> PH3A
    end

    PH3B --> S7_CHECK
    S7_CHECK{フロントあり?}
    S7_CHECK -->|Yes| S7["STEP 7: designer 実画面レビュー\n（Puppeteer スクリーンショット）"]
    S7 --> S8["STEP 8: /ultrareview（オプション）"]
    S8 --> S9
    S7_CHECK -->|No| S9

    S9["STEP 9: verify → security-reviewer\n→ qa → code-reviewer"]
    S9 --> S10["STEP 10: CLAUDE.md・README.md 生成"]
    S10 --> END([完了])
```

</details>

<details>
<summary>既存システムの相談（consult）フロー</summary>

```mermaid
flowchart TD
    START([相談を選択]) --> C1["STEP 1: 相談\n気になること・困っていることを聞く"]
    C1 --> DEEPEN{話が漠然としている?}
    DEEPEN -->|Yes| C1B["深掘り質問を繰り返す"]
    C1B --> DEEPEN
    DEEPEN -->|No| QA_CHECK{テスト・品質・QAの相談?}

    QA_CHECK -->|Yes| QA_MODE{実装まで進めたいか\n相談のみか}
    QA_MODE -->|不明確| ASK_MODE["どちらか確認"]
    ASK_MODE --> QA_MODE
    QA_MODE -->|実装まで| QA["SUMMARYを渡して\nflows/qa/SKILL.md に委譲"]
    QA --> END_Q([完了])
    QA_MODE -->|相談のみ| QAC["SUMMARYを渡して\nflows/qa-consult/SKILL.md に委譲"]
    QAC --> QAC_ESC{相談中に実装が\n必要と判明・承認?}
    QAC_ESC -->|Yes| QA
    QAC_ESC -->|No| END_QC([完了])

    QA_CHECK -->|No| C2["STEP 2: 現状調査\nコードベース・依存・複雑度を把握"]
    C2 --> C3["STEP 3: 選択肢の整理・提案\n移行 / リファクタ / 現状維持"]
    C3 --> GATE{ユーザーの判断}
    GATE -->|今はしない| END_N([相談のみで完了])
    GATE -->|実行する| C4

    subgraph EXEC["実行フェーズ"]
        C4["git pull → ブランチ作成"]
        C4 --> C5["issue 作成（任意）"]
        C5 --> C6["フェーズ単位で実装・検証"]
        C6 --> C7["PR 作成 → /review → main に戻る"]
    end

    C7 --> END([完了])
```

</details>

<details>
<summary>QA相談（qa-consult）フロー</summary>

```mermaid
flowchart TD
    START([qa-consult 起動\nSUMMARYを受け取る]) --> S1["STEP 1: 相談種別の判定\n1.テスト計画 / 2.体制構築 / 3.品質指標 / 4.横断"]
    S1 --> CONFIRM{種別を確認}
    CONFIRM -->|否定された| S1B["どの種別か選択してもらう"]
    S1B --> S2
    CONFIRM -->|承認| S2["STEP 2: 種別に対応する観点整理"]
    S2 --> S3["STEP 3: 観点・推奨事項を提示"]
    S3 --> GATE{十分か\n追加の深掘りが必要か}
    GATE -->|深掘り| S2
    GATE -->|十分| ESC_CHECK{実装が必要と判明?}
    ESC_CHECK -->|Yes・承認| QA["SUMMARYを渡して\nflows/qa/SKILL.md に委譲"]
    ESC_CHECK -->|No| END([相談のみで完了])
    QA --> END_Q([完了])
```

</details>

---

<details>
<summary>各フィーチャートラックの処理</summary>

フェーズ2で並列起動される各トラックエージェントの内部フロー。

```mermaid
flowchart LR
    subgraph Track["track-[name]（worktree 分離済み）"]
        direction TB
        R["docs/working/stories.md の\n担当 US を読む"]
        R --> I["所有ファイルを実装\n（依存ファイルは読み取り専用）"]
        I --> B{"pnpm build\n成功？"}
        B -->|失敗| I
        B -->|成功| V["受け入れ条件を\n1件ずつ確認"]
        V --> REP["完了レポート\n・実装ファイル一覧\n・受け入れ条件充足状況\n・未解決問題"]
    end
```

</details>

<details>
<summary>エージェントの呼び出しタイミング</summary>

```mermaid
flowchart LR
    subgraph AUTO["Claude が自律呼び出し"]
        intake --> refiner --> planner
        planner --> designer
        designer --> verify
        verify --> security-reviewer
        security-reviewer --> qa
        qa --> code-reviewer
    end

    subgraph MANUAL["ユーザーが手動呼び出し\n（プロジェクト内 /コマンド名）"]
        git-workflow
        db-migration
        api-design
        observability
        iac
        scorer
        release-planner
    end

    subgraph OPT["状況に応じて追加"]
        ideator
        debugger
        tester
        architect
    end
```

</details>

---

## mise の役割

| 管理するもの | 管理しないもの |
|-------------|--------------|
| Node.js / Bun / Flutter のバージョン | React, Drizzle 等のアプリライブラリ |
| pnpm のバージョン | プロジェクト固有の設定ファイル |

- ランタイムとパッケージマネージャーのバージョンを `.mise.toml` で固定する
- アプリのライブラリは `pnpm add`（Node.js系）または `flutter pub add`（Flutter）でインストールする（mise は関与しない）
- `mise install` は新規クローン時・`.mise.toml` 更新時に実行する
- **Flutter の注意:** `flutter = "stable"` は404エラーになる。`mise ls-remote flutter | tail -1` で最新バージョンを確認して固定すること

---

## ディレクトリ構成

```
craft/
├── SKILL.md      # エントリポイント（静的サイト / 動的アプリ / 相談 の選択ルーター）
├── agents/       # サブエージェント定義（Claude が自律的に呼び出す）
├── flows/        # 実行フロー定義（new-project・new-static・consult 等のサブ手順）
├── guidelines/   # 開発ガイドライン（アーキテクチャ・設計手法・DB設計）
├── hooks/        # ツール実行前後に自動で動くスクリプト
├── gitignore     # プロジェクトの .gitignore ひな形
├── mcp.json      # MCP サーバー設定（Puppeteer など）
└── settings.json # Claude Code 設定（権限・フック登録など）
```

### 新規プロジェクトにコピーされるファイル

agents・guidelines は craft から直接参照するためコピーしない。
プロジェクトに展開されるのは以下のみ。

| ファイル | 展開先 |
|---|---|
| `gitignore` | `.gitignore` |
| `mcp.json` | `.mcp.json` |
| `settings.json` | `.claude/settings.json`（絶対パス埋め込み） |
| `hooks/on-session-start.js` | `.claude/hooks/on-session-start.js` |
| `hooks/pre-bash.js` | `.claude/hooks/pre-bash.js` |
| `flows/git-workflow/SKILL.md` | `.claude/commands/git-workflow.md` |

---

## agents/

craft テンプレートに置かれ、Claude が状況に応じて自律呼び出しするサブエージェント。
各ファイルの `description` フィールドが「いつ呼び出すか」の判断基準になる。

### 設計フェーズ（STEP 1〜4 / 自動・順次）

| エージェント | 生成物 | 役割 |
|---|---|---|
| `ideator` | — | アイデア探索・プロジェクト方向性の提案。intake の前段。 |
| `intake` | `docs/working/requirements.md` | 新機能・曖昧な依頼のヒアリングと要件定義。 |
| `refiner` | `docs/working/stories.md` | requirements.md をユーザーストーリーと受け入れ条件に分解。 |
| `designer` | `docs/working/design-brief.md`<br>`docs/working/design-system.md` | UI/UX 設計・デザインブリーフ作成・Puppeteer での実画面レビュー。 |
| `planner` | `docs/working/plan.md` | 実装計画の立案。requirements.md / stories.md を読んでから動く。 |

### 完了チェック（STEP 9 / 自動・順次）

| エージェント | 確認観点 | 役割 |
|---|---|---|
| `verify` | 要件適合 | 要件定義と実装の照合。要件漏れ・スコープ外の混入を検出。 |
| `security-reviewer` | セキュリティ | 認証・認可・OWASP Top 10 の観点でのセキュリティレビュー。 |
| `qa` | ユーザー観点 | テスト戦略・E2E シナリオの網羅性・ユーザー観点での動作検証。 |
| `code-reviewer` | コード品質 | バグ・セキュリティ問題・規約違反の検出。 |

### 状況対応（任意呼び出し）

| エージェント | トリガー | 役割 |
|---|---|---|
| `debugger` | テスト失敗・実行時エラー | エラーの根本原因特定と最小修正案の提示。 |
| `tester` | テストを書きたいとき | 単体・統合テストの実装、テスト環境セットアップ。 |
| `architect` | 設計の大規模見直し | アーキテクチャ評価・テックデット特定・大規模リファクタ方針。 |

### シナリオ別ガイド

| やりたいこと | 修正するエージェント |
|---|---|
| ヒアリング項目・質問の仕方を変えたい | `intake` |
| ユーザーストーリーの粒度・形式を変えたい | `refiner` |
| デザインの評価基準・確認項目を変えたい | `designer` |
| 実装計画の構成・並列トラック分け方針を変えたい | `planner` |
| セキュリティチェックの観点を追加したい | `security-reviewer` |
| テスト戦略・E2E シナリオの方針を変えたい | `qa` |
| コードレビューの観点を追加・変更したい | `code-reviewer` |
| 要件適合チェックの基準を変えたい | `verify` |
| デバッグの手順・深さを変えたい | `debugger` |
| 呼び出しタイミングを変えたい | 該当エージェントの `description` フィールドを編集 |
| モデルを変えたい | 該当エージェントの `model` フィールドを編集（`opus` / `sonnet` / `haiku`） |
| 新しいエージェントを追加したい | `_TEMPLATE.md` をコピーして作る |

<details>
<summary>全エージェント一覧</summary>

| エージェント | 役割 |
|---|---|
| `ideator` | アイデア探索・プロジェクト方向性の提案。intake の前段。 |
| `intake` | 新機能・曖昧な依頼のヒアリング → `docs/working/requirements.md` 生成。 |
| `refiner` | requirements.md をユーザーストーリーと受け入れ条件に分解 → `docs/working/stories.md` 生成。 |
| `designer` | UI/UX 設計・デザインブリーフ作成・Puppeteer での実画面レビュー。 |
| `planner` | 実装計画の立案。requirements.md / stories.md を読んでから動く。 |
| `verify` | 要件定義と実装の照合。要件漏れ・スコープ外の混入を検出。 |
| `security-reviewer` | 認証・認可・OWASP Top 10 の観点でのセキュリティレビュー。 |
| `qa` | テスト戦略・E2E シナリオの網羅性・ユーザー観点での動作検証。 |
| `code-reviewer` | バグ・セキュリティ問題・規約違反の検出。 |
| `debugger` | エラー・テスト失敗の根本原因特定と最小修正案の提示。 |
| `tester` | 単体・統合テストの実装、テスト環境セットアップ。 |
| `architect` | アーキテクチャ評価・テックデット特定・大規模リファクタ方針。 |
| `_TEMPLATE` | 新規エージェント作成用のひな形。 |

</details>

---

## flows/

`/craft` スキルが内部で READ して実行するサブ手順書。
Claude Code のスキルとしては認識されず、メインの SKILL.md からの明示的な READ によって動作する。

| フロー | 役割 |
|---|---|
| `scope` | 種別（kind）が推定できない新規構築の要件・制約をヒアリングし、new-static / new-project / new-app または consult に振り分ける。対応レシピがない技術（GAS等）はTODOとして報告する。 |
| `new-project` | Webアプリ（Node.js系）のセットアップ手順（ハーネス構築〜実装チェーン）。 |
| `new-static` | 静的サイト（LP・PoC）のセットアップ手順。 |
| `new-app` | クロスプラットフォームアプリ（Flutter・React Native・Expo等）のセットアップ手順。Firebase 未取得時のモック実装分岐・`riverpod_generator` + `hive_generator` 競合の注記・Flutter用ビルドコマンド読み替え・実装再開フローを含む。 |
| `consult` | 既存システムへの課題相談。移行・リファクタ・現状維持を含めた選択肢を整理し、実行まで進める。 |
| `git-workflow` | ブランチ作成・コミット・PR 作成など git/gh 操作の安全手順。 |
| `db-migration` | DBスキーマ変更（テーブル追加・カラム変更）の安全な実行手順。 |
| `api-design` | REST API 設計規約（命名・HTTP メソッド・エラーフォーマット）。 |
| `observability` | ログ・トレーシング・ヘルスチェックの設計と実装指針。 |
| `iac` | Terraform/OpenTofu によるインフラ管理の導入・設計・運用手順。 |
| `qa` | 既存プロジェクトのQA基盤構築。テスト方針策定・フレームワーク導入・優先実装・CI組み込みまで一貫して進める。`agents/qa.md`（コードレビュー用エージェント）とは別物。 |
| `qa-consult` | テスト計画・戦略立案、QA体制・プロセス構築、品質指標・バグ管理など、実装を伴わないQA相談。`qa`フローとは別物（相談中に実装が必要と判明したら`qa`に切り替える）。 |
| `scorer` | コードベースの健全性を 6 観点で定期評価。スコアと改善タスクの一覧を返す。 |
| `release-planner` | リリース戦略・デプロイ計画・ロールバック手順の策定。 |
| `_TEMPLATE` | 新規フロー作成用のひな形。 |

---

## guidelines/

開発の指針として参照するガイドライン。直接呼び出すものではない。

| ファイル | 用途 |
|---|---|
| `tdd.md` | TDD（テスト駆動開発）の red-green-refactor サイクルと適用指針。 |
| `ddd.md` | DDD エッセンシャル。CQRS の適用指針を含む。 |
| `layered.md` | レイヤードアーキテクチャの構成。 |
| `modular-monolith.md` | モジュラーモノリスの構成。レイヤードの次のステップ。 |
| `onion.md` | オニオンアーキテクチャの構成。 |
| `db-design.md` | DB スキーマ設計ガイドライン。 |

---

## hooks/

`settings.json` に登録され、ツール実行の前後に自動で動く Node.js スクリプト。

| ファイル | タイミング | 役割 |
|---|---|---|
| `pre-bash.js` | Bash 実行前 | 危険なコマンドのブロック・警告。 |
| `on-session-start.js` | セッション開始時 | git状態表示・mise install 実行。 |

`post-write.js`（フォーマッタ）と `on-stop.js`（型チェック・リント）は技術スタックによって内容が変わるため、テンプレートには含めない。
新規プロジェクト作成時に `planner` エージェントが技術スタックに応じて生成する。

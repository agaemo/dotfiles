# new-project ハーネス

新規プロジェクト作成時に `/new-project` スキルでコピーされる一式。
プロジェクトルートの `.claude/` 以下に展開される。

---

## /new-project スキル 全体フロー

```mermaid
flowchart TD
    START([/new-project 起動]) --> SETUP

    SETUP["ハーネスセットアップ\n（サブエージェント）\n.gitignore / mcp.json / agents/ / hooks/ / settings.json"]
    SETUP --> MISE["mise.toml 作成 → mise install"]

    MISE --> S1

    subgraph DESIGN["ウォーターフォール設計フェーズ（承認ゲートあり）"]
        S1["STEP 1: intake\n→ docs/requirements.md"]
        S1 -->|承認 1/5| S2
        S2["STEP 2: refiner\n→ docs/stories.md\n※未解決の疑問は回答後も残す"]
        S2 -->|承認 2/5| S3_CHECK

        S3_CHECK{フロントあり?}
        S3_CHECK -->|Yes| S3["STEP 3: designer\n→ docs/design-brief.md\n→ docs/design-system.md"]
        S3 -->|承認 3/5| S4
        S3_CHECK -->|No| S4

        S4["STEP 4: planner\n→ docs/plan.md\n（クリティカルパス + 並列トラック定義）"]
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
    S7 --> S8["STEP 8: /review\nコンポーネント・アクセシビリティ・型安全性"]
    S8 --> S9
    S7_CHECK -->|No| S9

    S9["STEP 9: verify → security-reviewer\n→ qa → code-reviewer"]
    S9 --> S10["STEP 10: CLAUDE.md・README.md 生成\npublic/ クリーンアップ"]
    S10 --> END([完了])
```

---

## 各フィーチャートラックの処理

フェーズ2で並列起動される各トラックエージェントの内部フロー。

```mermaid
flowchart LR
    subgraph Track["track-[name]（worktree 分離済み）"]
        direction TB
        R["docs/stories.md の\n担当 US を読む"]
        R --> I["所有ファイルを実装\n（依存ファイルは読み取り専用）"]
        I --> B{"pnpm build\n成功？"}
        B -->|失敗| I
        B -->|成功| V["受け入れ条件を\n1件ずつ確認"]
        V --> REP["完了レポート\n・実装ファイル一覧\n・受け入れ条件充足状況\n・未解決問題"]
    end
```

---

## エージェントの呼び出しタイミング

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

    subgraph MANUAL["ユーザーが手動呼び出し\n（/コマンド名）"]
        git-workflow
        db-migration
        api-design
        observability
        iac
        scorer
        sre
        release-planner
    end

    subgraph OPT["状況に応じて追加"]
        ideator
        debugger
        tester
        architect
    end
```

---

## mise の役割

| 管理するもの | 管理しないもの |
|-------------|--------------|
| Node.js / Bun のバージョン | React, Drizzle 等のアプリライブラリ |
| pnpm のバージョン | プロジェクト固有の設定ファイル |

- ランタイムとパッケージマネージャーのバージョンを `.mise.toml` で固定する
- アプリのライブラリは `pnpm add` でインストールする（mise は関与しない）
- `mise install` は新規クローン時・`.mise.toml` 更新時に実行する

## ディレクトリ構成

```
new-project/
├── agents/       # サブエージェント定義（Claude が自律的に呼び出す）
├── commands/     # スラッシュコマンド定義（ユーザーが手動で呼び出す）
├── templates/    # ドキュメント・設計書のひな形
├── guidelines/   # 開発ガイドライン（アーキテクチャ・設計手法・DB設計）
├── hooks/        # ツール実行前後に自動で動くスクリプト
├── gitignore     # プロジェクトの .gitignore ひな形
├── mcp.json      # MCP サーバー設定（Puppeteer など）
└── settings.json # Claude Code 設定（権限・フック登録など）
```

---

## agents/

Claude が状況に応じて自律呼び出しするサブエージェント。
各ファイルの `description` フィールドが「いつ呼び出すか」の判断基準になる。

### 設計フェーズ（STEP 1〜4 / 自動・順次）

| エージェント | 生成物 | 役割 |
|---|---|---|
| `ideator` | — | アイデア探索・プロジェクト方向性の提案。intake の前段。 |
| `intake` | `docs/requirements.md` | 新機能・曖昧な依頼のヒアリングと要件定義。 |
| `refiner` | `docs/stories.md` | requirements.md をユーザーストーリーと受け入れ条件に分解。 |
| `designer` | `docs/design-brief.md`<br>`docs/design-system.md` | UI/UX 設計・デザインブリーフ作成・Puppeteer での実画面レビュー。 |
| `planner` | `docs/plan.md` | 実装計画の立案。requirements.md / stories.md を読んでから動く。 |

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
| `intake` | 新機能・曖昧な依頼のヒアリング → `docs/requirements.md` 生成。 |
| `refiner` | requirements.md をユーザーストーリーと受け入れ条件に分解 → `docs/stories.md` 生成。 |
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

## commands/

ユーザーが `/コマンド名` で手動呼び出すスラッシュコマンド。
参照資料・手順書として使われることが多い。

| コマンド | 役割 |
|---|---|
| `git-workflow` | ブランチ作成・コミット・PR 作成など git/gh 操作の安全手順。 |
| `db-migration` | DBスキーマ変更（テーブル追加・カラム変更）の安全な実行手順。 |
| `api-design` | REST API 設計規約（命名・HTTP メソッド・エラーフォーマット）。 |
| `observability` | ログ・トレーシング・ヘルスチェックの設計と実装指針。 |
| `iac` | Terraform/OpenTofu によるインフラ管理の導入・設計・運用手順。 |
| `scorer` | コードベースの健全性を 6 観点で定期評価。スコアと改善タスクの一覧を返す。 |
| `sre` | パフォーマンス・Web 表示速度・インフラのレビュー。 |
| `release-planner` | リリース戦略・デプロイ計画・ロールバック手順の策定。 |
| `_TEMPLATE` | 新規コマンド作成用のひな形。 |

---

## templates/

Claude がドキュメント生成時に参照するひな形。直接呼び出すものではない。

| テンプレート | 用途 |
|---|---|
| `ideator-input.md` | ideator エージェントへの入力フォーマット。 |
| `design-brief.md` | デザインブリーフの構成。 |
| `design-system.md` | デザインシステムの定義フォーマット。 |

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

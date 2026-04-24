# new-project ハーネス

新規プロジェクト作成時に `/new-project` スキルでコピーされる一式。
プロジェクトルートの `.claude/` 以下に展開される。

## ディレクトリ構成

```
new-project/
├── agents/       # サブエージェント定義（Claude が自律的に呼び出す）
├── commands/     # スラッシュコマンド定義（ユーザーが手動で呼び出す）
├── templates/    # ドキュメント・設計書のひな形
├── hooks/        # ツール実行前後に自動で動くスクリプト
├── CLAUDE.md     # プロジェクト向けの Claude 指示
├── mcp.json      # MCP サーバー設定（Puppeteer など）
└── settings.json # Claude Code 設定（権限・フック登録など）
```

---

## agents/

Claude が状況に応じて自律呼び出しするサブエージェント。
各ファイルの `description` フィールドが「いつ呼び出すか」の判断基準になる。

| エージェント | 役割 |
|---|---|
| `ideator` | アイデア探索・プロジェクト方向性の提案。intake の前段。 |
| `intake` | 新機能・曖昧な依頼のヒアリング → `docs/requirements.md` 生成。 |
| `refiner` | requirements.md をユーザーストーリーと受け入れ条件に分解 → `docs/stories.md` 生成。 |
| `planner` | 実装計画の立案。requirements.md / stories.md を読んでから動く。 |
| `architect` | アーキテクチャ評価・テックデット特定・大規模リファクタ方針。 |
| `designer` | UI/UX 設計・デザインブリーフ作成・Puppeteer での実画面レビュー。 |
| `tester` | 単体・統合テストの実装、テスト環境セットアップ。 |
| `debugger` | エラー・テスト失敗の根本原因特定と最小修正案の提示。 |
| `refactorer` | 振る舞いを変えずに内部構造を改善。新機能追加は行わない。 |
| `code-reviewer` | バグ・セキュリティ問題・規約違反の検出。 |
| `security-reviewer` | 認証・認可・OWASP Top 10 の観点でのセキュリティレビュー。 |
| `qa` | テスト戦略・E2E シナリオの網羅性・ユーザー観点での動作検証。 |
| `verify` | 要件定義と実装の照合。要件漏れ・スコープ外の混入を検出。 |
| `scorer` | コードベースの健全性を 6 観点で定期評価。実装は行わない。 |
| `sre` | インフラ・パフォーマンス・Web 表示速度のレビュー。 |
| `release-planner` | リリース戦略・デプロイ計画・ロールバック手順の策定。 |
| `_TEMPLATE` | 新規エージェント作成用のひな形。 |

### エージェントを修正するとき

- **呼び出しタイミングを変えたい** → `description` フィールドを編集する
- **モデルを変えたい** → `model` フィールドを `opus` / `sonnet` / `haiku` から選ぶ
- **指示内容を変えたい** → フロントマター以降の本文を編集する
- **新しいエージェントを追加したい** → `_TEMPLATE.md` をコピーして作る

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
| `_TEMPLATE` | 新規コマンド作成用のひな形。 |

---

## templates/

Claude がドキュメント生成時に参照するひな形。直接呼び出すものではない。

| テンプレート | 用途 |
|---|---|
| `ideator-input.md` | ideator エージェントへの入力フォーマット。 |
| `design-brief.md` | デザインブリーフの構成。 |
| `design-system.md` | デザインシステムの定義フォーマット。 |
| `architecture/ddd.md` | DDD エッセンシャル。 |
| `architecture/onion.md` | オニオンアーキテクチャの構成。 |
| `architecture/layered.md` | レイヤードアーキテクチャの構成。 |
| `architecture/db-design.md` | DB スキーマ設計ガイドライン。 |

---

## hooks/

`settings.json` に登録され、ツール実行の前後に自動で動く Node.js スクリプト。

| ファイル | タイミング | 役割 |
|---|---|---|
| `pre-bash.js` | Bash 実行前 | 危険なコマンドのブロック・警告。 |
| `on-session-start.js` | セッション開始時 | git状態表示・mise install 実行。 |

`post-write.js`（フォーマッタ）と `on-stop.js`（型チェック・リント）は技術スタックによって内容が変わるため、テンプレートには含めない。
新規プロジェクト作成時に `planner` エージェントが技術スタックに応じて生成する。

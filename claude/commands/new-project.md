---
name: new-project
description: アプリ・API・管理画面など動的機能を持つプロジェクトにハーネス一式（agents・hooks・settings・commands）をセットアップする。LP・静的ページなら /new-static を使うこと。
---

# /new-project

カレントディレクトリに Claude ハーネスを一式セットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-project` — カレントディレクトリにセットアップする
- LP・静的ページは `/new-static` を使うこと（intake / planner 不要のシンプルなフロー）

---

## 手順

### ステップ 1: フロントエンドの確認

```
ASK USER: "フロントエンドUI（画面）はありますか？（あり / なし）"
WAIT_FOR: ユーザーの回答

SET has_frontend = (回答が "あり" の場合 true、"なし" の場合 false)
```

---

### ステップ 2: ファイル書き出し（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、以下のプロンプトを渡す。
**変数 `<cwd>` と `<has_frontend>` は実際の値に展開してから渡すこと。**
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト:**

```
以下の STEP を上から順に実行してください。スキップ禁止。

CWD          = <現在の作業ディレクトリの絶対パス>
TEMPLATE     = ~/.claude/commands/new-project
HAS_FRONTEND = <true または false>

IMPORTANT: 以下の操作はすべてユーザーへの確認なしに即座に実行すること。
  - TEMPLATE ディレクトリからのファイルコピー（Read → Write）
  - ディレクトリ作成（mkdir）
  - ビルド・インストールコマンドの実行
  確認が必要なのは rm / git の破壊的操作のみ。

NOTE: .mcp.json と .claude/commands/git-workflow.md への Write は
  settings.json の permissions.allow に登録されているため自動承認される。
  初回セットアップ中（settings.json 書き出し前）に確認が表示された場合は
  「はい」を選択して続行すること。

PROHIBITED: CLAUDE.md および AGENTS.md を生成すること
  理由: CLAUDE.md は実装完了後のステップ9で正しい内容を書く。早期生成すると不完全な内容が残る。

--- STEP 1: git 初期化 ---

REQUIRE: カレントディレクトリが CWD であること

RUN:
  git init

ASSERT EXISTS(.git/)

--- STEP 2: ファイル書き出し ---

FOREACH row IN 以下の対応表:
  IF row.frontend_only == true AND HAS_FRONTEND == false:
    SKIP
  ELSE:
    READ  TEMPLATE/row.src
    WRITE CWD/row.dest
  ENDIF

  | src                                      | dest                                  | frontend_only |
  |------------------------------------------|---------------------------------------|---------------|
  | gitignore                                | .gitignore                            | false         |
  | mcp.json                                 | .mcp.json                             | false         |
  | agents/intake.md                         | agents/intake.md                      | false         |
  | agents/refiner.md                        | agents/refiner.md                     | false         |
  | agents/planner.md                        | agents/planner.md                     | false         |
  | agents/verify.md                         | agents/verify.md                      | false         |
  | agents/security-reviewer.md              | agents/security-reviewer.md           | false         |
  | agents/qa.md                             | agents/qa.md                          | false         |
  | agents/code-reviewer.md                  | agents/code-reviewer.md               | false         |
  | agents/release-planner.md                | agents/release-planner.md             | false         |
  | commands/git-workflow.md                 | .claude/commands/git-workflow.md      | false         |
  | guidelines/db-design.md                  | guidelines/db-design.md              | false         |
  | agents/designer.md                       | agents/designer.md                    | true          |

--- STEP 3: hooks ファイルの書き出し ---

FOREACH row IN 以下の対応表:
  IF EXISTS(TEMPLATE/row.src):
    READ  TEMPLATE/row.src
    WRITE CWD/row.dest
  ELSE:
    SKIP  # テンプレートに存在しないファイルはエラーではなくスキップ

  | src                        | dest                                    |
  |----------------------------|-----------------------------------------|
  | hooks/on-session-start.js  | .claude/hooks/on-session-start.js       |
  | hooks/pre-bash.js          | .claude/hooks/pre-bash.js               |
  | hooks/post-write.js        | .claude/hooks/post-write.js             |
  | hooks/on-stop.js           | .claude/hooks/on-stop.js                |

--- STEP 4: settings.json の書き出し（絶対パス埋め込み） ---

READ TEMPLATE/settings.json
REPLACE ALL: ".claude/hooks/" → "<絶対パス>/.claude/hooks/"  # <絶対パス> は CWD の実際の値（例: /Users/alice/myproject）
WRITE CWD/.claude/settings.json

例 (CWD = /Users/alice/myproject の場合):
  変換前: "command": "node .claude/hooks/on-stop.js"
  変換後: "command": "node /Users/alice/myproject/.claude/hooks/on-stop.js"

ASSERT EXISTS(CWD/.claude/settings.json)

--- STEP 5: セットアップ確認（安全網） ---

NOTE: 通常は発火しない。STEP 2〜4で書き出し済みのため

FOREACH (path, src) IN [
  (.claude/settings.json,    settings.json),
  (.claude/hooks/on-stop.js, hooks/on-stop.js),
  (agents/intake.md,         agents/intake.md)
]:
  IF NOT EXISTS(CWD/path):
    READ  TEMPLATE/src
    WRITE CWD/path
  ENDIF
  ASSERT EXISTS(CWD/path)

--- STEP 6: 完了報告 ---

REPORT: "完了しました"
```

---

### ステップ 3: mise.toml の作成と `mise install`

ランタイムと pnpm を mise で管理する。

> **mise の役割:** ランタイム（Node.js, Bun）とパッケージマネージャー（pnpm）のバージョン管理のみ。
> アプリのライブラリ（React, Drizzle 等）は `pnpm add` でインストールする。

```bash
# Node.js プロジェクト（デフォルト推奨）
cat > .mise.toml << 'EOF'
[tools]
node = "22"
pnpm = "latest"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise trust && mise install   # 新規ディレクトリでは mise trust が必要
```

```bash
# Bun プロジェクト（ユーザーが明示した場合のみ）
# 注意: better-sqlite3・drizzle-kit 等のネイティブモジュールは Node.js でしか動かない場合がある
cat > .mise.toml << 'EOF'
[tools]
bun = "1.3"
node = "lts"   # ネイティブモジュール実行用
pnpm = "latest"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise trust && mise install
```

```bash
# Python プロジェクト（uv をパッケージマネージャーとして使用）
cat > .mise.toml << 'EOF'
[tools]
python = "3.12"
uv = "latest"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise trust && mise install

# 仮想環境の作成と依存インストール
uv venv
uv sync
```

> **パッケージマネージャーは pnpm を標準として使うこと。**
> pnpm はサプライチェーン攻撃への耐性が高く（`--frozen-lockfile` / `onlyBuiltDependencies` 等）、
> ディスク効率も良い。インストールは `pnpm install`、追加は `pnpm add` を使うこと。

> **ランタイム（Node.js・Bun・Python）のバージョンは必ず固定すること。** `"latest"` はビルド再現性がなく、本番との差異が生じる原因になる。
> パッケージマネージャー（pnpm・uv 等）は `"latest"` で構わない。
> mise 管理下なので `mise upgrade` で意図的にアップグレードできる。

> **Apple Silicon (M1/M2/M3) の注意:**
> ネイティブモジュール（better-sqlite3 等）がアーキテクチャ不一致でクラッシュする場合は、
> `pnpm rebuild <パッケージ名>` で再ビルドすること。

---

### ステップ 4: 完了報告

```
REPORT TO USER:
  セットアップが完了しました。

  次のステップ:
  1. 何を作るか決まっていない場合は「ideatorエージェントを呼び出してください」
  2. 要件が決まっている場合は「intakeエージェントを呼び出してください」

IF 未完了タスクがある状態でセッションを終了する場合:
  SAVE TO MEMORY: 残タスクの一覧
  NOTE: 保存しないと次のセッションで「続きをお願いします」が機能しない
```

---

## 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。
各エージェント呼び出しにはプロジェクトルートの絶対パスと前フェーズの成果物パスを明示すること。

> **注意:** `intake`・`designer` はユーザーとの対話が必要なエージェントである。
> Agent ツール（サブエージェント）として起動してはならない。
> スキル（`/new-project:agents:intake` 等）として呼び出すか、メインClaude自身が担当すること。

<!-- 承認進捗の表示ルール:
  各 GATE でユーザーに承認を求める前に、以下の形式で現在の進捗を必ず表示すること。
  フロントエンドあり（N=5）: requirements / stories / design / plan / 統合設計書
  フロントエンドなし（N=4）: requirements / stories / plan / 統合設計書

  表示例:
  ── 承認 [2/5]: stories.md ──────────────────────
  ✅ STEP 1: requirements.md
  👉 STEP 2: stories.md（承認待ち）
  ⬜ STEP 3: デザイン
  ⬜ STEP 4: plan.md
  ⬜ STEP 4.5: 統合設計書（3文書）
  ─────────────────────────────────────────────
-->

```
STEP 1: intake
  OUTPUT: docs/requirements.md
  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

STEP 2: refiner
  INPUT:  docs/requirements.md
  OUTPUT: docs/stories.md
  NOTE: 未解決の疑問はユーザーから回答を得た後も削除しない。
        以下の形式でチェック済みにして残すこと（意思決定の根拠として保持）:
        - [x] [疑問の内容]
              → **回答（YYYY-MM-DD）:** [回答内容]
  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

IF HAS_FRONTEND == true:
  STEP 3: designer ← 省略禁止・planner より先に実施すること
    a. /new-project:templates:design-brief を参照してデザインブリーフを生成 → docs/design-brief.md
    b. /new-project:templates:design-system を参照してデザインシステムを定義 → docs/design-system.md
    c. 画面構成・コンポーネント構成を docs/design.md に記録
    GATE: 承認進捗を表示してからユーザーに提示し、承認を得ること
    PROHIBITED: デザイン承認前にコンポーネントを1行も書くこと
    NOTE: デザインによってAPIの形・DBフィールドが変わる場合があるため、planner より前に確定させること
ENDIF

STEP 4: planner
  INPUT:  docs/stories.md（+ docs/design-brief.md があれば）
  OUTPUT: docs/plan.md
  GATE: 承認進捗を表示してからユーザーに計画を提示し、承認を得ること
  PROHIBITED: 承認前に実装を開始すること

STEP 4.5: 統合設計書生成 ← 実装着手前の総合確認ゲート

  目的: バラバラに承認してきた要求・要件・設計を1つの整合した文書群として出力し、
       「これで開発を始めてよい」と判断できる状態にする。

  生成する3文書:
    a. /new-project:templates:doc-requirements を参照 → docs/01_requirements_doc.md
       入力: docs/requirements.md
    b. /new-project:templates:doc-specifications を参照 → docs/02_specifications_doc.md
       入力: docs/stories.md
    c. /new-project:templates:doc-basic-design を参照 → docs/03_basic_design_doc.md
       入力: docs/plan.md（+ docs/design-system.md があれば）

  GATE: 3文書を生成後、以下の形式でユーザーに一括提示し、承認を得ること:

    ── 承認 [5/5]: 統合設計書（最終確認） ─────────────
    ✅ STEP 1: requirements.md
    ✅ STEP 2: stories.md
    ✅ STEP 3: デザイン
    ✅ STEP 4: plan.md
    👉 STEP 4.5: 統合設計書（承認待ち）
    ──────────────────────────────────────────────

    以下の3文書の内容を確認してください。これらの内容で開発を開始します。

    📄 要求定義書 → docs/01_requirements_doc.md
    📄 要件定義書 → docs/02_specifications_doc.md
    📄 基本設計書 → docs/03_basic_design_doc.md

    （各文書の概要サマリーをここに記載する）

    承認いただけましたか？

  PROHIBITED: 3文書の承認前に実装を開始すること
  NOTE: 文書の内容に矛盾が見つかった場合は、該当する元ドキュメント（requirements.md 等）を修正してから再生成すること

STEP 5: 理解度チェック（Early Stop）← 実装着手前の最終確認ゲート

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

STEP 6: 実装

  docs/plan.md の「フィーチャートラック設計」セクションを読んでから実装を開始すること。
  トラック設計がある場合は以下の3フェーズで進める。
  トラック設計がない場合（小規模）は「フェーズ1のみ・逐次確認サイクル」で進める。

  ---

  ### フェーズ1: クリティカルパス（シリアル）

  docs/plan.md の「フェーズ1」ステップを順番に実装する。
  各ステップ完了ごとに `pnpm build` で型エラーがないことを確認する。

  フェーズ1完了後:
    1. `pnpm dev` を起動し、ログイン〜基本ナビゲーションが動作することを確認する
    2. 問題がなければフェーズ1の成果を git commit する（フェーズ2の起点になる）

  ```bash
  git add -A
  git commit -m "フェーズ1: クリティカルパス（DB・認証・AppShell）実装完了"
  ```

  ---

  ### フェーズ2: 並列フィーチャートラック（worktree 分離）

  docs/plan.md の「フェーズ2」に定義された各トラックを、
  **isolation: "worktree" + run_in_background: true** でバックグラウンド並列実行する。

  各トラックに渡すプロンプト（下記テンプレートを使用・変数を展開して渡すこと）:

  ```
  あなたは [TRACK_NAME] フィーチャートラックの実装担当エージェントです。

  プロジェクトルート: [ABSOLUTE_PATH]

  担当ユーザーストーリー:
  [US番号とタイトルのリスト（docs/stories.md の該当USを転記）]

  所有ファイル（このトラックだけが作成・編集する）:
  [docs/plan.md のトラック定義から転記]

  依存ファイル（読み取り専用・編集禁止）:
  [docs/plan.md のトラック定義から転記]

  実装手順:
  1. docs/stories.md の担当 US の受け入れ条件をすべて読む
  2. 依存ファイルを読んで型・インターフェースを把握する
  3. 所有ファイルを実装する（所有ファイル以外は絶対に編集しない）
  4. `pnpm build` を実行し、型エラー・コンパイルエラーがないことを確認する
  5. 担当 US の各受け入れ条件に対して実装を確認し、満たしていることを確認する

  完了基準（両方満たすこと）:
  - `pnpm build` が成功すること
  - 担当 US の全受け入れ条件が実装に反映されていること

  PROHIBITED:
  - 所有ファイル以外のファイルを編集すること
  - DB スキーマ（lib/db/schema.ts）を変更すること
  - フェーズ1の共通コンポーネントを新規作成・変更すること

  完了後に報告すること:
  - 実装したファイルの一覧
  - `pnpm build` 成功の確認
  - 受け入れ条件の充足状況（条件ごとに ✅ または ⚠️）
  - 未解決の問題（あれば）
  ```

  全トラック完了後:
    FOR EACH completed_track:
      1. worktree で作成されたブランチの差分を確認する
      2. main ブランチにマージする
      3. コンフリクトがあれば解消する
      4. `pnpm build` で統合ビルドを確認する

  ---

  ### フェーズ3: 統合確認

  全トラックのマージ完了後:
    1. `pnpm dev` を起動する
    2. 主要フローを実機で確認する（一覧→登録→詳細→操作→ダッシュボード）
    3. 問題があれば即修正する
    4. `git commit` で統合完了を記録する

  フェーズ3完了後に STEP 9 のレビューチェーン（verify → security-reviewer → qa → code-reviewer）へ進む。

IF HAS_FRONTEND == true:
  STEP 7: designer による実画面レビュー
    RUN: Puppeteer MCP でスクリーンショットを撮影
    CHECK: デザインブリーフ・デザインシステムとの差異を確認・修正

  STEP 8: /review（公式スキル）
    CHECK: コンポーネント設計・アクセシビリティ・型安全性
ENDIF

STEP 9: verify → security-reviewer → qa → code-reviewer

STEP 10: CLAUDE.md・README.md 生成 + クリーンアップ
  実装完了後、確定したスタック・コマンド・構造をもとに生成する。
  （実装前に生成するとプレースホルダーになるため、このタイミングで行う）

  PROHIBITED: CLAUDE.md および AGENTS.md を実装完了前に生成すること
    理由: 早期生成すると不完全な内容が残り、Claude Code が誤った文脈で動作する。

  CLAUDE.md に含めること:
    - プロジェクト名・目的（1〜2文）
    - スタック（実際に使う言語・フレームワーク・主要ライブラリ）
    - 開発コマンド（dev / test / build の実際のコマンド）
    - アーキテクチャ（採用パターン名・ディレクトリ構造のポイント・レイヤー間の依存の向き）
    - プロジェクト固有の制約（DBエンジン・実行環境の制限など）
    - docs/plan.md を参照するよう一言書く
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
      IF EXISTS(public/file):
        IF NOT REFERENCED IN src/:
          DELETE public/file
        ENDIF
      ENDIF
    ENDFOREACH
    NOTE: 要件検討中にロゴ等を public/ に置いている場合があるため、参照チェックを必ず行ってから削除すること
  ENDIF
```

---

### Next.js プロジェクト初期化（ハーネス設置済みディレクトリ）

`new-project` ハーネス設置後のディレクトリには `.gitignore`・`agents/` 等が既存のため、
`pnpm create next-app .` は競合エラーになる。**カレントディレクトリ内**に一時サブディレクトリを作ってマージすること。

```bash
# NG: /tmp など外部ディレクトリは使わない（スキルの「カレントディレクトリで実行」原則に反する）
# OK: カレントディレクトリ内に _tmp を作成してマージ
pnpm create next-app _tmp --typescript --tailwind --app --src-dir=false --import-alias "@/*" --no-git --yes
cp -r _tmp/. . && rm -rf _tmp
```

> **バージョン管理の注意:**
> `pnpm create next-app` は常に最新版をインストールする。メジャーバージョンが変わると
> API・ファイル規約・設定形式が大きく変わる場合がある（例: Next.js 16 で `middleware.ts` → `proxy.ts`）。
> インストール後、`node_modules/next/dist/docs/` の変更点ドキュメントを必ず確認すること。
> 特定バージョンに固定したい場合: `pnpm create next-app _tmp --version X.Y ...`

---

### planner へ渡すべき設計判断の確認事項

planner を呼び出す前に、以下の判断をユーザーに確認すること。これらは後から変更するとコストが大きい。

**フロントエンドがある場合:**
- ログイン窓口は統一するか分けるか
  - 統一（`/login` → ロールに応じてリダイレクト）← 推奨
  - 分離（`/admin/login` と `/customer/login` を別々に）
- 管理者と顧客でドメインを分けるか（`admin.example.com` / `example.com`）

**バックエンドがある場合:**
- 公開エンドポイント（認証不要）と保護エンドポイント（認証必要）の境界線
  - 特に「ログイン前の顧客がアクセスできる情報」を明確にする

> **設計判断の記録:** 確認した内容は `docs/plan.md` の「設計判断」セクションに記録すること。

---

## オプションエージェント（必要に応じて追加）

| エージェント | 用途 |
|-------------|------|
| `ideator` | 何を作るか決まっていないときのアイデア探索 |
| `debugger` | 複雑なデバッグ（エラーの根本原因特定） |
| `tester` | テストコードの自動実装 |
| `refactorer` | 振る舞いを変えずにコード構造を改善 |
| `scorer` | コードベース健全性の定期評価 |
| `sre` | Web表示速度・インフラのパフォーマンスレビュー |

---
name: new-project
description: 動的アプリ（API・DB・認証あり）のセットアップ手順。/craft から動的アプリを選択したときに実行される。
---

# new-project（動的アプリセットアップ）

カレントディレクトリに Claude ハーネスを一式セットアップする。

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
TEMPLATE     = このSKILL.mdが存在するディレクトリの2階層上の絶対パス
  # craft/flows/new-project/SKILL.md → craft/
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
  理由: CLAUDE.md は実装完了後のステップ11で正しい内容を書く。早期生成すると不完全な内容が残る。

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
  | flows/git-workflow/SKILL.md             | .claude/commands/git-workflow.md      | false         |

--- STEP 3: hooks ファイルの書き出し ---

FOREACH row IN 以下の対応表:
  READ  TEMPLATE/row.src
  WRITE CWD/row.dest

  | src                        | dest                                    |
  |----------------------------|-----------------------------------------|
  | hooks/on-session-start.js  | .claude/hooks/on-session-start.js       |
  | hooks/pre-bash.js          | .claude/hooks/pre-bash.js               |

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
  (.claude/settings.json,              settings.json),
  (.claude/hooks/on-session-start.js,  hooks/on-session-start.js),
  (.claude/hooks/pre-bash.js,          hooks/pre-bash.js),
  (.claude/commands/git-workflow.md,   flows/git-workflow/SKILL.md)
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

### ステップ 3: mise.toml の作成と `mise install`（メインClaude が実行）

ランタイムと pnpm を mise で管理する。

> **mise の役割:** ランタイム（Node.js, Bun）とパッケージマネージャー（pnpm）のバージョン管理のみ。
> アプリのライブラリ（React, Drizzle 等）は `pnpm add` でインストールする。

```
IF ユーザーが Bun を明示した:    → 以下の Bun テンプレートを使用
ELIF ユーザーが Python を明示した: → 以下の Python テンプレートを使用
ELSE:                             → Node.js テンプレートを使用（デフォルト。ユーザーに確認不要）
ENDIF
```

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
_.path = [".venv/bin"]
EOF

mise trust && mise install

# 仮想環境の作成と依存インストール
uv venv
uv sync
```

```
ASSERT: `mise exec -- node --version` が成功すること（Python プロジェクトは `python --version`）
ASSERT: `mise exec -- pnpm --version` が成功すること（Python プロジェクトは `uv --version`）
IF FAILED: エラー内容を報告し、STOP すること
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

```

---

## 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。

> **注意:** `intake`・`designer` はユーザーとの対話が必要なエージェントである。
> Agent ツール（サブエージェント）として起動してはならない。
> スキル（`/craft:agents:intake` 等）として呼び出すか、メインClaude自身が担当すること。

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
  ⬜ STEP 5: 統合設計書（3文書）
  ─────────────────────────────────────────────
-->

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
  NOTE: 呼び出し前に「planner へ渡すべき設計判断の確認事項」セクションを参照し、
        ユーザーに確認すること
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

  生成する3文書:
    a. このファイル末尾の「テンプレート: 要求定義書」を参照 → .craft/01_requirements_doc.md
       入力: .craft/requirements.md
    b. このファイル末尾の「テンプレート: 要件定義書」を参照 → .craft/02_specifications_doc.md
       入力: .craft/stories.md
    c. このファイル末尾の「テンプレート: 基本設計書」を参照 → .craft/03_basic_design_doc.md
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

  .craft/plan.md の「フィーチャートラック設計」セクションを読んでから実装を開始すること。
  トラック設計がある場合は以下の3フェーズで進める。
  トラック設計がない場合（小規模）は「フェーズ1のみ・逐次確認サイクル」で進める。

  ---

  ### フェーズ1: クリティカルパス（シリアル）

  .craft/plan.md の「フェーズ1」ステップを順番に実装する。
  各ステップ完了ごとに `mise exec -- pnpm build` で型エラーがないことを確認する。

  フェーズ1完了後:
    1. `mise exec -- pnpm dev` を起動し、ログイン〜基本ナビゲーションが動作することを確認する
    2. 問題がなければフェーズ1の成果を git commit する（フェーズ2の起点になる）

  ```bash
  git add -A
  git commit -m "フェーズ1: クリティカルパス実装完了"
  # 実際に実装した内容に合わせてメッセージを調整すること
  ```

  ---

  ### フェーズ2: 並列フィーチャートラック（worktree 分離）

  .craft/plan.md の「フェーズ2」に定義された各トラックを、
  **isolation: "worktree" + run_in_background: true** でバックグラウンド並列実行する。

  各トラックに渡すプロンプト（下記テンプレートを使用・変数を展開して渡すこと）:

  ```
  あなたは [TRACK_NAME] フィーチャートラックの実装担当エージェントです。

  プロジェクトルート: [ABSOLUTE_PATH]

  担当ユーザーストーリー:
  [US番号とタイトルのリスト（.craft/stories.md の該当USを転記）]

  所有ファイル（このトラックだけが作成・編集する）:
  [.craft/plan.md のトラック定義から転記]

  依存ファイル（読み取り専用・編集禁止）:
  [.craft/plan.md のトラック定義から転記]

  実装手順:
  1. .craft/stories.md の担当 US の受け入れ条件をすべて読む
  2. 依存ファイルを読んで型・インターフェースを把握する
  3. 所有ファイルを実装する（所有ファイル以外は絶対に編集しない）
  4. `mise exec -- pnpm build` を実行し、型エラー・コンパイルエラーがないことを確認する
  5. 担当 US の各受け入れ条件に対して実装を確認し、満たしていることを確認する

  完了基準（両方満たすこと）:
  - `mise exec -- pnpm build` が成功すること
  - 担当 US の全受け入れ条件が実装に反映されていること

  PROHIBITED:
  - 所有ファイル以外のファイルを編集すること
  - DB スキーマ（[スキーマファイルのパス: 例 lib/db/schema.ts]）を変更すること
  - フェーズ1の共通コンポーネントを新規作成・変更すること

  完了後に報告すること:
  - 実装したファイルの一覧
  - `mise exec -- pnpm build` 成功の確認
  - 受け入れ条件の充足状況（条件ごとに ✅ または ⚠️）
  - 未解決の問題（あれば）
  ```

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
    3. 問題があれば即修正する
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

### Next.js プロジェクト初期化（ステップ3の直後・Next.js を使う場合のみ）

`craft` ハーネス設置後のディレクトリには `.gitignore`・`agents/` 等が既存のため、
`pnpm create next-app .` は競合エラーになる。**カレントディレクトリ内**に一時サブディレクトリを作ってマージすること。

```
REQUIRE: フレームワークに Next.js を使うことが確定していること
TIMING:  ステップ3（mise install）完了直後、ステップ4（完了報告）の前に実行すること
ASSERT:  `mise exec -- node --version` が成功すること
ASSERT:  `mise exec -- pnpm --version` が成功すること
```

```bash
# NG: /tmp など外部ディレクトリは使わない（スキルの「カレントディレクトリで実行」原則に反する）
# OK: カレントディレクトリ内に _tmp を作成してマージ
mise exec -- pnpm create next-app _tmp --typescript --tailwind --app --src-dir=false --import-alias "@/*" --no-git --yes
cp -r _tmp/. . && rm -rf _tmp
mise exec -- pnpm install
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

> **設計判断の記録:** 確認した内容は `.craft/plan.md` の「設計判断」セクションに記録すること。

---

## オプションエージェント（必要に応じて追加）

| エージェント | 用途 |
|-------------|------|
| `ideator` | 何を作るか決まっていないときのアイデア探索 |
| `debugger` | 複雑なデバッグ（エラーの根本原因特定） |
| `tester` | テストコードの自動実装 |
| `scorer` | コードベース健全性の定期評価 |

---

## テンプレート: 要求定義書

STEP 6 で `.craft/01_requirements_doc.md` を生成する際の雛形。入力: `.craft/requirements.md`

```markdown
# 要求定義書

> バージョン: 1.0
> 作成日: YYYY-MM-DD
> 元要件: .craft/requirements.md

---

## 1. プロジェクト概要

**プロジェクト名:**

**背景・解決する課題:**
-

**目的:**
-

---

## 2. ステークホルダー

| ロール | 人数 | 主な関心事 |
|--------|------|-----------|
| | | |

---

## 3. システム概要

---

## 4. スコープ

### スコープ内（作るもの）

-

### スコープ外（作らないもの）

-

---

## 5. 制約・前提条件

| 区分 | 内容 |
|------|------|
| 技術スタック | |
| 実行環境 | |
| 外部連携 | |
| 期限 | |
| 予算・規模 | |

---

## 6. 成功の基準

-

---

## 7. リスク

| リスク | 影響度 | 対策 |
|--------|--------|------|
| | | |
```

---

## テンプレート: 要件定義書

STEP 6 で `.craft/02_specifications_doc.md` を生成する際の雛形。入力: `.craft/stories.md`

```markdown
# 要件定義書

> バージョン: 1.0
> 作成日: YYYY-MM-DD
> 元要件: .craft/stories.md

---

## 1. ユーザー・ロール定義

| ロール | 説明 | 主な操作権限 |
|--------|------|------------|
| | | |

---

## 2. ロール × 機能 権限マトリクス

| 機能 | [ロールA] | [ロールB] | [ロールC] |
|------|----------|----------|----------|
| | ✅ | ❌ | ✅ |

凡例: ✅ 可能 / ❌ 不可 / 👁 閲覧のみ

---

## 3. 機能要件一覧

| US番号 | 機能名 | 概要 | サイズ | 優先度 |
|--------|--------|------|--------|--------|
| US-001 | | | S/M/L | 高/中/低 |

---

## 4. ビジネスルール

### ステータス遷移

```
[状態A] → [状態B] → [状態C]
              ↕
          [状態D]
```

### その他のルール

-

---

## 5. 画面一覧

| 画面ID | 画面名 | パス | アクセス可能ロール | 備考 |
|--------|--------|------|-----------------|------|
| P-001 | | | | |

---

## 6. 非機能要件

| 区分 | 要件 |
|------|------|
| パフォーマンス | |
| 可用性 | |
| セキュリティ | |
| データ保持 | |
| 対応デバイス | |

---

## 7. 未解決の疑問（決定済み）

- [x] [疑問の内容]
      → **回答（YYYY-MM-DD）:** [回答内容]
```

---

## テンプレート: 基本設計書

STEP 6 で `.craft/03_basic_design_doc.md` を生成する際の雛形。入力: `.craft/plan.md`（+ `.craft/design-system.md` があれば）

```markdown
# 基本設計書

> バージョン: 1.0
> 作成日: YYYY-MM-DD
> 元要件: .craft/plan.md

---

## 1. アーキテクチャ概要

**採用パターン:** <!-- Layered / Modular Monolith / Onion / DDD 等 -->
**選択理由:**

### レイヤー構成

```
[UIレイヤー]      app/ または pages/
[ユースケース層]  actions/ または usecases/
[サービス層]      lib/services/
[DBレイヤー]      lib/db/
```

---

## 2. 技術スタック

| 区分 | 技術 | バージョン | 採用理由 |
|------|------|-----------|--------|
| 言語 | | | |
| フレームワーク | | | |
| DB | | | |
| 認証 | | | |
| UI | | | |
| バリデーション | | | |

---

## 3. ディレクトリ構成

```
project-root/
├── app/
│   ├── (auth)/
│   └── (app)/
├── lib/
│   ├── db/
│   └── services/
├── actions/
└── components/
```

---

## 4. 認証・認可設計

**認証方式:**
**セッション管理:**
**トークン:**

### 保護対象ルート

| パス | 必要ロール |
|------|----------|
| /* | 認証済み全員 |
| /admin/* | [ロール名] のみ |

---

## 5. DBスキーマ設計

### テーブル一覧

| テーブル名 | 説明 | 主要カラム |
|-----------|------|----------|
| | | |

### 主要なリレーション

```
[テーブルA] 1 ── N [テーブルB]
[テーブルB] N ── M [テーブルC]（中間テーブル: junction_table）
```

---

## 6. API 設計（Route Handlers / API Routes）

| メソッド | パス | 説明 | 認証要否 |
|---------|------|------|---------|
| GET | /api/... | | 要 |
| POST | /api/... | | 要 |

---

## 7. 主要画面・コンポーネント設計

### 共通レイアウト

### 主要画面

| 画面 | パス | レイアウト | 主要コンポーネント |
|------|------|-----------|-----------------|
| | | | |

---

## 8. デザインシステム概要

**ブランドカラー:**
**フォント:**
**ダーク/ライト:**

---

## 9. セキュリティ設計

| 脅威 | 対策 |
|------|------|
| 認証バイパス | |
| CSRF | |
| XSS | |
| SQLi | |
| 不正アクセス（IDOR） | |

---

## 10. ADR（アーキテクチャ決定記録）

| ADR番号 | タイトル | ステータス |
|--------|---------|---------|
| ADR-001 | | 決定済み |
```

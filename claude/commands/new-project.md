---
name: new-project
description: アプリ・API・管理画面など動的機能を持つプロジェクトにハーネス一式（agents・hooks・settings・commands）をセットアップする。LP・静的ページなら /new-lp を使うこと。
---

# /new-project

カレントディレクトリに Claude ハーネスを一式セットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-project` — カレントディレクトリにセットアップする
- LP・静的ページは `/new-lp` を使うこと（intake / planner 不要のシンプルなフロー）

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
  | CLAUDE.md                                | CLAUDE.md                             | false         |
  | agents/intake.md                         | agents/intake.md                      | false         |
  | agents/refiner.md                        | agents/refiner.md                     | false         |
  | agents/planner.md                        | agents/planner.md                     | false         |
  | agents/verify.md                         | agents/verify.md                      | false         |
  | agents/security-reviewer.md              | agents/security-reviewer.md           | false         |
  | agents/qa.md                             | agents/qa.md                          | false         |
  | agents/code-reviewer.md                  | agents/code-reviewer.md               | false         |
  | agents/release-planner.md                | agents/release-planner.md             | false         |
  | commands/git-workflow.md                 | .claude/commands/git-workflow.md      | false         |
  | templates/architecture/db-design.md      | templates/architecture/db-design.md   | false         |
  | agents/designer.md                       | agents/designer.md                    | true          |

--- STEP 3: hooks ファイルの書き出し ---

FOREACH row IN 以下の対応表:
  READ  TEMPLATE/row.src
  WRITE CWD/row.dest

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
  (CLAUDE.md,                CLAUDE.md),
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

ランタイムと pnpm を mise で管理する。以下を参考に `.mise.toml` を作成し、`mise install` を実行する。

```bash
# Bun プロジェクトの場合（推奨）
cat > .mise.toml << 'EOF'
[tools]
bun = "1.3"        # バージョンは固定すること（"latest"は避ける）
node = "lts"       # pnpm が内部で使う Node.js
pnpm = "9"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise install
```

```bash
# Node.js プロジェクトの場合
cat > .mise.toml << 'EOF'
[tools]
node = "22"
pnpm = "9"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise install
```

> **パッケージマネージャーは pnpm を標準として使うこと。**
> pnpm はサプライチェーン攻撃への耐性が高く（`--frozen-lockfile` / `onlyBuiltDependencies` 等）、
> ディスク効率も良い。インストールは `pnpm install`、追加は `pnpm add` を使うこと。

> **バージョンは必ず固定すること。** `"latest"` はビルド再現性がなく、本番との差異が生じる原因になる。
> mise 管理下なので `mise upgrade` で意図的にアップグレードできる。

> **Apple Silicon (M1/M2/M3) + Bun 環境の注意:**
> Node.js が Rosetta 2 (x64) で動いている環境では `bunx` 経由の CLI ツールが esbuild・rollup のアーキテクチャミスマッチで起動しないことがある。
> - `drizzle-kit` は `bunx` ではなく `bun node_modules/.bin/drizzle-kit` で実行すること
> - `vite` は `bunx --bun vite` で実行すること（`--bun` フラグで Bun ネイティブランタイムを強制）

---

### ステップ 4: 完了報告

```
REPORT TO USER:
  セットアップが完了しました。
  （詳細はサブエージェントの報告を参照）

  次のステップ:
  1. CLAUDE.md の TODO をプロジェクトの内容で埋めること
  2. 何を作るか決まっていない場合は「ideatorエージェントを呼び出してください」
  3. 要件が決まっている場合は「intakeエージェントを呼び出してください」

IF 未完了タスクがある状態でセッションを終了する場合:
  SAVE TO MEMORY: 残タスクの一覧
  NOTE: 保存しないと次のセッションで「続きをお願いします」が機能しない
```

---

## 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。
各エージェント呼び出しにはプロジェクトルートの絶対パスと前フェーズの成果物パスを明示すること。

```
STEP 1: intake
  OUTPUT: docs/requirements.md
  GATE: ユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

STEP 2: refiner
  INPUT:  docs/requirements.md
  OUTPUT: docs/stories.md
  GATE: ユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

STEP 3: planner
  INPUT:  docs/stories.md
  OUTPUT: docs/plan.md
  GATE: ユーザーに計画を提示し、承認を得ること
  PROHIBITED: 承認前に実装を開始すること

STEP 3.5: 理解度チェック（Early Stop）← 実装着手前の最終確認ゲート

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

IF HAS_FRONTEND == true:
  STEP 4: designer ← 省略禁止
    a. /new-project:templates:design-brief を参照してデザインブリーフを生成
    b. /new-project:templates:design-system を参照してデザインシステムを定義
    c. 画面構成・コンポーネント構成を docs/design.md に記録
    GATE: ユーザーに提示し、承認を得ること
    PROHIBITED: デザイン承認前にコンポーネントを1行も書くこと
ENDIF

STEP 5: 実装

IF HAS_FRONTEND == true:
  STEP 6: designer による実画面レビュー
    RUN: Puppeteer MCP でスクリーンショットを撮影
    CHECK: デザインブリーフ・デザインシステムとの差異を確認・修正

  STEP 7: /review（公式スキル）
    CHECK: コンポーネント設計・アクセシビリティ・型安全性
ENDIF

STEP 8: verify → security-reviewer → qa → code-reviewer
```

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
> CLAUDE.md には記録しない（ファイルが重くなる）。CLAUDE.md からは `docs/plan.md` を参照するよう一言書く。

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

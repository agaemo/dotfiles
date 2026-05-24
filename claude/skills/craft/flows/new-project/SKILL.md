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
**変数 `<cwd>`・`<template>`・`<has_frontend>` は実際の値に展開してから渡すこと。**
**TEMPLATEは「このSKILL.mdが存在するディレクトリの2階層上」= craftディレクトリの絶対パス（例: /Users/alice/.claude/skills/craft）を親エージェントが計算して埋め込む。**
WAIT_FOR: サブエージェントの完了報告（"完了しました"）を受け取ってから続きに進む。

---

**サブエージェントへのプロンプト:**

```
以下の STEP を上から順に実行してください。スキップ禁止。

CWD          = <現在の作業ディレクトリの絶対パス>
TEMPLATE     = <craftディレクトリの絶対パス>  # 例: /Users/alice/.claude/skills/craft
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

### ステップ 3: ランタイムマネージャーのセットアップ（メインClaude が実行）

ランタイムと pnpm を管理する。

> **ランタイムマネージャーの選択:**
> ユーザーが明示していない場合は `mise` をデフォルトとして使用する。
> ユーザーが別のマネージャーを使っている場合はそちらに従うこと。
>
> | マネージャー | セットアップ | 実行prefix |
> |---|---|---|
> | mise（デフォルト） | `mise trust && mise install` | `mise exec --` |
> | devbox | `devbox init && devbox shell` | `devbox run` |
> | nix-shell | `nix-shell` | `nix-shell --run` |
> | 直接インストール済み | なし | （prefixなし） |
>
> 以降のコマンド例は mise を前提として記載しているが、
> 他のマネージャーを使う場合は適宜 `mise exec --` 部分を読み替えること。

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

Bun / Python の場合: `READ flows/new-project/recipes/runtime-bun-python.md`

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

> **ネイティブモジュール（better-sqlite3・esbuild 等）のビルド許可:**
> pnpm v10 以降は `pnpm approve-builds`（インタラクティブ）が必要だが、CI や自動実行では使えない。
> `package.json` に以下を追加することで承認をスキップできる:
>
> ```json
> {
>   "pnpm": {
>     "onlyBuiltDependencies": ["better-sqlite3", "esbuild"]
>   }
> }
> ```
>
> ネイティブモジュールを追加するたびにこのリストに追記すること。
> 追加後は `pnpm install` を再実行してビルドを通す。

---

### ステップ 3.5: フレームワーク・追加パターンの選択

mise install 完了後、会話の文脈からフレームワークと追加パターンを確定する。

```
INFER framework FROM 会話の文脈:
  Next.js  → フロント+APIルート一体型、SSR/SSG が必要な場合
  Hono     → APIのみ・Edge Runtime・軽量な場合
  Express  → シンプルなAPIサーバーの場合
  その他   → ユーザーに確認

IF framework == Next.js:
  READ flows/new-project/recipes/nextjs-init.md
  FOLLOW: Next.js初期化手順を実行する
  TIMING: このステップで実行し、ステップ4（完了報告）の前に完了させること

IF リアルタイム通信（WebSocket・チャット・通知）が要件にある:
  READ flows/new-project/recipes/socketio.md
  NOTE: Socket.IOのパターンはフェーズ1実装時に参照すること

IF Bun または Python を使う場合:
  READ flows/new-project/recipes/runtime-bun-python.md
  FOLLOW: 該当するmise.tomlテンプレートを使用すること
```

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

```
# HAS_FRONTEND はステップ1で設定済みの変数（このチェーン全体で参照する）
# true  → STEP 3（デザイン）・STEP 8（実画面レビュー）を実施
# false → STEP 3・STEP 8をスキップ
```

PROHIBITED: `intake`・`designer` を Agent ツール（サブエージェント）で起動すること
  理由: これらはユーザーとの対話が必要。スキルとして呼び出すか、メインClaude自身が担当すること。

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

  # SKILL_DIR = このSKILL.mdが存在するディレクトリの2階層上の絶対パス
  # 例: /Users/alice/.claude/skills/craft
  # 親SKILL.mdと同じ方法で導出すること（SKILL.mdのパスから逆算）
  READ {SKILL_DIR}/flows/new-project/templates.md  ← 3つのテンプレートが定義されている

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

### 参照: planner前の設計判断確認事項

READ flows/new-project/recipes/planner-checklist.md（STEP 4: planner の直前に参照）

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


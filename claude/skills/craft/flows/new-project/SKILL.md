---
name: new-project
description: 動的アプリ（API・DB・認証あり）のセットアップ手順。/craft から動的アプリを選択したときに実行される。
---

# new-project（動的アプリセットアップ）

カレントディレクトリに Claude ハーネスを一式セットアップする。

```
SKILL_DIR = このSKILL.md（craft/flows/new-project/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/new-project/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft
  # 以降の READ {SKILL_DIR}/... は Read ツールで絶対パスに展開して実行すること

REQUIRE: カレントディレクトリがプロジェクトルートであること（cd してから実行すること）
```

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
IF サブエージェントが "完了しました" を報告しない（エラー・中断）:
  REPORT: 失敗したステップと理由をユーザーに伝え、再試行するか確認すること
  STOP

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

NOTE: .mcp.json への Write は settings.json の permissions.allow に登録されているため自動承認される。
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
REPLACE ALL: ".claude/hooks/" → "<CWD>/.claude/hooks/"  # CWD の実際の値に展開（例: /Users/alice/myproject）
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
  (.claude/hooks/pre-bash.js,          hooks/pre-bash.js)
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

```
# デフォルト: mise。ユーザーが別のマネージャー（devbox / nix-shell）を使っている場合はそちらに従う。
# 非標準構成やトラブル時: READ {SKILL_DIR}/flows/new-project/recipes/runtime-notes.md

IF ユーザーが Bun を明示した:
  READ {SKILL_DIR}/flows/new-project/recipes/runtime-bun-python.md
  FOLLOW: Bun の mise.toml テンプレートを使用する
ELIF ユーザーが Python を明示した:
  READ {SKILL_DIR}/flows/new-project/recipes/runtime-bun-python.md
  FOLLOW: Python の mise.toml テンプレートを使用する
ELSE:
  # Node.js（デフォルト・ユーザーに確認不要）
  RUN:
    cat > .mise.toml << 'EOF'
    [tools]
    node = "22"
    pnpm = "latest"

    [env]
    _.path = ["./node_modules/.bin"]
    EOF
    mise trust && mise install
ENDIF

ASSERT: `mise exec -- node --version` が成功すること（Python プロジェクトは `python --version`）
ASSERT: `mise exec -- pnpm --version` が成功すること（Python プロジェクトは `uv --version`）
IF FAILED: エラー内容を報告し、STOP すること
```

---

### ステップ 3.5: フレームワーク・追加パターンの選択

mise install 完了後、会話の文脈からフレームワークと追加パターンを確定する。

# NOTE: このステップはwebフレームワーク選択（Step 3のランタイム選択とは別）
```
INFER framework FROM 会話の文脈:
  Next.js      → フロント+APIルート一体型、SSR/SSG が必要な場合
  Vite + React → フロントエンドのみ（SPA）、Oxc / Rolldown を試したい場合
  Hono         → APIのみ・Edge Runtime・軽量な場合
  Express      → シンプルなAPIサーバーの場合
  その他       → ユーザーに確認:
    ASK USER: 使用するフレームワークを教えてください
    WAIT_FOR: ユーザーの回答
    SET framework = ユーザーの回答

IF framework == Next.js:
  READ {SKILL_DIR}/flows/new-project/recipes/nextjs-init.md
  FOLLOW: Next.js初期化手順を実行する
  TIMING: このステップで実行し、ステップ4（完了報告）の前に完了させること

IF framework == Vite + React:
  READ {SKILL_DIR}/flows/new-project/recipes/vite-react.md
  FOLLOW: Vite + React 初期化手順を実行する
  TIMING: このステップで実行し、ステップ4（完了報告）の前に完了させること

# Next.js はバンドラー込み。それ以外で HAS_FRONTEND == true の場合は明示確認する。
IF HAS_FRONTEND == true AND framework NOT IN [Next.js, Vite + React]:
  ASK USER:
    フロントエンドのバンドラー・開発サーバーはどうしますか？
    開発を継続するなら導入しておくことを推奨します。
      1. Vite（推奨）— フロントエンド HMR あり・Rolldown/Oxc ベースで高速
      2. 今は不要（静的ファイルのみ、または後で決める）
  WAIT_FOR: ユーザーの選択
  IF 選択 == Vite:
    READ {SKILL_DIR}/flows/new-project/recipes/vite-react.md
    FOLLOW: Vite + React 初期化手順を実行する
  ENDIF

IF リアルタイム通信（WebSocket・チャット・通知）が要件にある:
  READ {SKILL_DIR}/flows/new-project/recipes/socketio.md
  NOTE: Socket.IOのパターンはフェーズ1実装時に参照すること
# ※ Bun / Python の mise.toml は Step 3 で既に適用済み
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

## 標準エージェントチェーン・オプションエージェント・再開時注意点

READ {SKILL_DIR}/flows/new-project/agent-chain.md ← ステップ4完了後、エージェントチェーンを開始する前に読む
（STEP 1〜6 の設計フェーズ詳細手順・GATEがここに定義されている。STEP 7 で build フローに委譲し、
 実装・テスト戦略・フェーズ2/3・CLAUDE.md生成は {SKILL_DIR}/flows/build/SKILL.md が担当する）


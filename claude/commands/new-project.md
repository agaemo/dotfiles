---
name: new-project
description: 新規プロジェクトにハーネス一式（agents・hooks・settings・commands）をセットアップする。
---

# /new-project

カレントディレクトリに Claude ハーネスを一式セットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-project` — カレントディレクトリにセットアップする

## 手順

### ステップ 1: フロントエンドの確認

以下を確認する:

```
フロントエンドUI（画面）はありますか？（あり / なし）
```

### ステップ 2: ファイル書き出し（サブエージェントで実行）

**Agent ツール**を使ってサブエージェントを起動し、以下のプロンプトを渡す。
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト（変数を展開してから渡すこと）:**

```
以下の作業を実行してください。

## 作業内容

### 1. git 初期化
カレントディレクトリ（<現在の作業ディレクトリの絶対パス>）で実行する:
git init

### 2. ファイル書き出し
テンプレートディレクトリ `~/.claude/commands/new-project/` 内の各ファイルを
Read ツールで読み込み、Write ツールで書き出す。
書き出し先は `<現在の作業ディレクトリの絶対パス>/` を起点とした絶対パスを使うこと。

| 読み込み元（~/.claude/commands/new-project/ からの相対パス） | 書き出し先（カレントディレクトリからの相対パス） |
|---|---|
| gitignore | .gitignore |
| mcp.json | .mcp.json |
| CLAUDE.md | CLAUDE.md |
| agents/intake.md | agents/intake.md |
| agents/refiner.md | agents/refiner.md |
| agents/planner.md | agents/planner.md |
| agents/verify.md | agents/verify.md |
| agents/security-reviewer.md | agents/security-reviewer.md |
| agents/qa.md | agents/qa.md |
| agents/code-reviewer.md | agents/code-reviewer.md |
| agents/release-planner.md | agents/release-planner.md |
| commands/git-workflow.md | .claude/commands/git-workflow.md |
| templates/architecture/db-design.md | templates/architecture/db-design.md |
<フロントエンドありの場合のみ: | agents/designer.md | agents/designer.md |>

### 3. hooks ファイルの書き出し
hooks は以下のファイルを書き出す（内容はテンプレートをそのままコピー）:
- `~/.claude/commands/new-project/hooks/on-session-start.js` → `<現在の作業ディレクトリの絶対パス>/.claude/hooks/on-session-start.js`
- `~/.claude/commands/new-project/hooks/pre-bash.js` → `<現在の作業ディレクトリの絶対パス>/.claude/hooks/pre-bash.js`
- `~/.claude/commands/new-project/hooks/post-write.js` → `<現在の作業ディレクトリの絶対パス>/.claude/hooks/post-write.js`
- `~/.claude/commands/new-project/hooks/on-stop.js` → `<現在の作業ディレクトリの絶対パス>/.claude/hooks/on-stop.js`

### 4. settings.json の書き出し（絶対パス埋め込み）
テンプレート `~/.claude/commands/new-project/settings.json` を **そのままコピーせず**、
hook コマンドの `.claude/hooks/` を `<現在の作業ディレクトリの絶対パス>/.claude/hooks/` に置換してから
`<現在の作業ディレクトリの絶対パス>/.claude/settings.json` に書き出す。

例: `"command": "node .claude/hooks/on-stop.js"` →
    `"command": "node <現在の作業ディレクトリの絶対パス>/.claude/hooks/on-stop.js"`

### 5. セットアップ確認
`CLAUDE.md` が存在することを確認する。存在しなければ再度書き出すこと。

### 6. 完了報告
すべて書き出したら「完了しました」とだけ返してください。
```

---

### ステップ 3: mise.toml の作成と `mise install`

ランタイムと pnpm を mise で管理する。以下を参考に `.mise.toml` を作成し、`mise install` を実行すること。

```bash
# Bun プロジェクトの場合（推奨）
cat > .mise.toml << 'EOF'
[tools]
bun = "1.3"        # バージョンは固定すること（"latest"は避ける）
node = "lts"       # pnpm が内部で使う Node.js
pnpm = "9"

[env]
# プロジェクト内のバイナリを優先
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

### ステップ 4: 完了報告

```
セットアップが完了しました。

作成したファイル:
- .gitignore / .mcp.json / .mise.toml
- .claude/settings.json（hooks は絶対パス設定済み）
- .claude/hooks/ （4ファイル）
- .claude/commands/git-workflow.md
- CLAUDE.md
- agents/ （intake / refiner / planner / verify / security-reviewer / qa / code-reviewer / release-planner）
- templates/architecture/db-design.md
[フロントエンドありの場合] - agents/designer.md

次のステップ:
1. CLAUDE.md の TODO をプロジェクトの内容で埋めること
2. 何を作るか決まっていない場合は「ideatorエージェントを呼び出してください」
3. 要件が決まっている場合は「intakeエージェントを呼び出してください」
```

**未完了タスクがある状態でセッションを終了する場合は、必ず残タスクをメモリに保存してから終了すること。**

---

## 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。
各エージェント呼び出しにはプロジェクトルートの絶対パスと前フェーズの成果物パスを明示すること。

```
1. intake
   → docs/requirements.md を生成
   → ユーザーに内容を提示して確認を得ること

2. refiner
   → docs/stories.md を生成
   → ユーザーに内容を提示して確認を得ること

3. planner
   → docs/plan.md を生成
   → ★ 必ずユーザーに計画を提示し、承認を得てから次に進むこと ★
   → 承認前に実装を開始してはいけない

4. [フロントエンドありの場合] designer ← 省略禁止
   → 以下の順で実行すること:
     a. /new-project:templates:design-brief を参照してデザインブリーフを生成
     b. /new-project:templates:design-system を参照してデザインシステムを定義
     c. 画面構成・コンポーネント構成を docs/design.md に記録
     d. ユーザーに提示して承認を得ること
   → ★ デザイン承認前にコンポーネントを1行も書いてはいけない ★

5. 実装

6. [フロントエンドありの場合] designer による実画面レビュー
   → Puppeteer MCP でスクリーンショットを撮影
   → デザインブリーフ・デザインシステムとの差異を確認・修正

7. /review（公式スキル）← UIコードの品質確認に使う
   → コンポーネント設計・アクセシビリティ・型安全性をレビュー

8. verify → security-reviewer → qa → code-reviewer（Track C）
```

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

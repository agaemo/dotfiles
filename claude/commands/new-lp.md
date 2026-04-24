---
name: new-lp
description: ランディングページ（LP）や静的ページのプロジェクトを新規作成する。
---

# /new-lp

Astro + Node.js でランディングページ（LP）プロジェクトをセットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-lp` — カレントディレクトリに LP をセットアップする

## 手順

### ステップ 1: デザイン（designerエージェントで実行）

designerを呼ぶ前に、テンプレートを `docs/design-brief.md` としてコピーする（docsディレクトリがなければ作成する）:
- 読み込み元: `~/.claude/commands/new-project/templates/design-brief.md`
- 書き出し先: `<カレントディレクトリ>/docs/design-brief.md`

その後、**Agent ツール**を使って `designer` エージェントを起動する。

- designerがヒアリングを行い、`docs/design-brief.md` のTODOを埋める
- コンポーネント構成・カラーパレット・タイポグラフィを決める
- designer完了後、デザインブリーフの内容を確認する

### ステップ 2: ユーザー確認

デザイン方針が固まったら、以下をユーザーに確認する：

```
デザインブリーフが完成しました。この方針で実装を進めますか？
```

ユーザーが承認したら次のステップへ進む。承認前にセットアップを始めてはならない。

### ステップ 3: セットアップ（サブエージェントで実行）

**Agent ツール**を使ってサブエージェントを起動し、以下のプロンプトを渡す。
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト（変数を展開してから渡すこと）:**

```
以下の作業を順番に実行してください。

## 作業内容

### 1. Node / pnpm 環境構築
カレントディレクトリ（<現在の作業ディレクトリの絶対パス>）で実行する:
```bash
mise use --path mise.toml node@lts
mise use --path mise.toml pnpm@latest
```
※ --path mise.toml を必ず付けること（付けないと上位ディレクトリの mise.toml が更新される）。

次に node と pnpm をインストールする:
```bash
mise install
```

### 2. Astro プロジェクト作成
ローカルの mise 環境（.mise.toml）経由で実行する:
```bash
mise exec -- pnpm create astro@latest . --template minimal --no-git
```

### 3. ファイル書き出し
テンプレートを Read ツールで読み込み、Write ツールで書き出す。
書き出し先は `<現在の作業ディレクトリの絶対パス>/` を起点とした絶対パスを使うこと。
.gitignore は Astro が生成した内容とマージすること（上書き禁止）。
docs/design-brief.md はすでに存在するためスキップすること。

| 読み込み元（~/.claude/commands/new-project/ からの相対パス） | 書き出し先（カレントディレクトリからの相対パス） |
|---|---|
| gitignore | .gitignore（既存とマージ） |
| mcp.json | .mcp.json |
| settings.json | .claude/settings.json |
| hooks/on-session-start.js | .claude/hooks/on-session-start.js |
| hooks/pre-bash.js | .claude/hooks/pre-bash.js |
| hooks/post-write.js | .claude/hooks/post-write.js |
| hooks/on-stop.js | .claude/hooks/on-stop.js |
| CLAUDE.md | CLAUDE.md |
| agents/designer.md | agents/designer.md |
| commands/git-workflow.md | .claude/commands/git-workflow.md |

### 4. git 初期化
```bash
git init
```

### 5. ネイティブ依存関係のビルド承認
```bash
mise exec -- pnpm approve-builds --all
```
esbuild・sharp などのpostinstallスクリプトを承認しないと devサーバー起動時にエラーになる。

### 6. ビルド確認
```bash
mise exec -- pnpm run build
```
エラーが出た場合は内容を報告すること。

### 7. セットアップ確認
以下のファイルが存在することを確認する:
- `.claude/settings.json`
- `.claude/hooks/on-stop.js`
- `CLAUDE.md`
- `agents/designer.md`

存在しないファイルがあれば再度書き出すこと。

### 8. 完了報告
すべて完了したら「完了しました」とだけ返してください。
```

---

### ステップ 4: 完了報告

すべての作業が完了したら、以下を報告する:

```
LP プロジェクトのセットアップが完了しました。

作成したファイル:
- .gitignore / .mcp.json / .claude/settings.json
- .claude/hooks/ （4ファイル）
- .claude/commands/git-workflow.md
- CLAUDE.md
- agents/designer.md
- docs/design-brief.md（designerが作成済み）

次のステップ:
1. CLAUDE.md の TODO をプロジェクトの内容で埋める
2. セクション単位で .astro コンポーネントに分割して実装する
3. Puppeteer MCP で画面確認して完了
```

**未完了タスクがある状態でセッションを終了する場合は、必ず残タスクをメモリに保存してから終了すること。**
保存しないと次のセッションで「続きをお願いします」が機能しない。

---

## ワークフロー

`intake` / `planner` / `security-reviewer` / `qa` は不要。

1. `designer` エージェントでUI設計・コンポーネント構成を決める（docs/design-brief.md を作成）
2. ユーザー承認後にセットアップを実行する
3. セクション単位で `.astro` コンポーネントに分割して実装する
4. Puppeteer MCP で画面確認して完了

※ 単一HTMLファイルで実装しない（メンテナンス性が著しく低下するため）
※ フレームワークのインストール手順は必ず公式ドキュメントを確認すること

---
name: new-lp
description: Astro + Node.js でランディングページプロジェクトをセットアップする。
---

# /new-lp

Astro + Node.js でランディングページ（LP）プロジェクトを新規作成する。
**LPを置きたい親ディレクトリで実行すること。**

## 使い方

- `/new-lp` — プロジェクト名を確認してから LP をセットアップする

## 手順

### ステップ 1: プロジェクト名の確認

以下を確認する:

```
プロジェクト名（ディレクトリ名）を教えてください。
```

### ステップ 2: プロジェクト作成・セットアップ（サブエージェントで実行）

**Agent ツール**を使ってサブエージェントを起動し、以下のプロンプトを渡す。
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト（変数を展開してから渡すこと）:**

```
以下の作業を実行してください。

## 作業内容

### 1. Astro プロジェクト作成
親ディレクトリ（<現在の作業ディレクトリの絶対パス>）で実行する:
```bash
mise exec node@lts -- npm create astro@latest <project-name> -- --template minimal --no-git --install --yes
```
※ 先に cd して mise.toml を置くとディレクトリが「空ではない」と判定され別フォルダに作成されるため、親ディレクトリから実行すること。

### 2. Node バージョン固定
```bash
cd <project-name>
mise use --path mise.toml node@lts
```
※ --path mise.toml を必ず付けること（付けないと親ディレクトリの mise.toml が更新される）。

### 3. git 初期化
プロジェクトディレクトリ（<現在の作業ディレクトリの絶対パス>/<project-name>）で実行する:
```bash
git init
```

### 4. ファイル書き出し
テンプレートを Read ツールで読み込み、Write ツールで書き出す。
書き出し先は `<現在の作業ディレクトリの絶対パス>/<project-name>/` を起点とした絶対パスを使うこと。
.gitignore は Astro が生成した内容とマージすること（上書き禁止）。

| 読み込み元（~/.claude/commands/new-project/ からの相対パス） | 書き出し先（プロジェクトルートからの相対パス） |
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
| templates/design-brief.md | docs/design-brief.md |

### 5. ビルド確認
```bash
mise exec -- npm run build
```
エラーが出た場合は内容を報告すること。

### 6. 完了報告
すべて完了したら「完了しました」とだけ返してください。
```

---

### ステップ 3: 完了報告

すべての作業が完了したら、以下を報告する:

```
LP プロジェクト「<project-name>」のセットアップが完了しました。

作成したファイル:
- .gitignore / .mcp.json / .claude/settings.json
- .claude/hooks/ （4ファイル）
- .claude/commands/git-workflow.md
- CLAUDE.md
- agents/designer.md
- docs/design-brief.md

次のステップ:
1. cd <project-name> でプロジェクトに入る
2. CLAUDE.md の TODO をプロジェクトの内容で埋める
3. 「designer エージェントを呼び出してください」でUI設計を開始する
   designer がヒアリングを通じて docs/design-brief.md を埋め、
   コンポーネント構成を提案してくれます
```

---

## ワークフロー

セットアップ後は以下の順で進める。`intake` / `planner` / `security-reviewer` / `qa` は不要。

1. `designer` エージェントでUI設計・コンポーネント構成を決める（docs/design-brief.md を作成）
2. セクション単位で `.astro` コンポーネントに分割して実装する
3. Puppeteer MCP で画面確認して完了

※ 単一HTMLファイルで実装しない（メンテナンス性が著しく低下するため）
※ フレームワークのインストール手順は必ず公式ドキュメントを確認すること

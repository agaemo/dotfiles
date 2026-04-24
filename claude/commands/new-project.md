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
| settings.json | .claude/settings.json |
| hooks/on-session-start.js | .claude/hooks/on-session-start.js |
| hooks/pre-bash.js | .claude/hooks/pre-bash.js |
| hooks/post-write.js | .claude/hooks/post-write.js |
| hooks/on-stop.js | .claude/hooks/on-stop.js |
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

### 3. セットアップ確認
`CLAUDE.md` が存在することを確認する。存在しなければ再度書き出すこと。

### 4. 完了報告
すべて書き出したら「完了しました」とだけ返してください。
```

---

### ステップ 3: mise.toml の確認

ランタイムが決まっている場合は以下を作成するか確認する:

```bash
# 例: Node.js の場合
cat > .mise.toml << 'EOF'
[tools]
node = "lts"
# bun = "latest"
# go = "latest"
# python = "3.12"
EOF
```

### ステップ 4: 完了報告

すべてのファイルを書き出したら、以下を報告する:

```
セットアップが完了しました。

作成したファイル:
- .gitignore / .mcp.json / .claude/settings.json
- .claude/hooks/ （4ファイル）
- .claude/commands/git-workflow.md
- CLAUDE.md
- agents/ （intake / refiner / planner / verify / security-reviewer / qa / code-reviewer / release-planner）
- templates/architecture/db-design.md
[フロントエンドありの場合] - agents/designer.md

次のステップ:
1. CLAUDE.md の TODO をプロジェクトの内容で埋めること
2. .claude/hooks/ を使用言語に合わせてカスタマイズすること
3. 必要に応じて mise.toml でランタイムを固定すること
4. 何を作るか決まっていない場合は「ideatorエージェントを呼び出してください」
5. 要件が決まっている場合は「intakeエージェントを呼び出してください」
```

**未完了タスクがある状態でセッションを終了する場合は、必ず残タスクをメモリに保存してから終了すること。**
保存しないと次のセッションで「続きをお願いします」が機能しない。

---

## オプションエージェント（必要に応じて追加）

以下のエージェントは標準セットに含まれていない。必要になったら追加すること。

| エージェント | 用途 |
|-------------|------|
| `ideator` | 何を作るか決まっていないときのアイデア探索 |
| `debugger` | 複雑なデバッグ（エラーの根本原因特定） |
| `tester` | テストコードの自動実装 |
| `refactorer` | 振る舞いを変えずにコード構造を改善 |
| `scorer` | コードベース健全性の定期評価 |
| `sre` | Web表示速度・インフラのパフォーマンスレビュー |

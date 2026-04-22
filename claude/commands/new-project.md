---
name: new-project
description: 新規プロジェクトにハーネス一式（agents・hooks・settings・commands）をセットアップする。
---

# /new-project

新規プロジェクトディレクトリを作成し、Claude ハーネスを一式セットアップする。

## 使い方

- `/new-project` — プロジェクト名をインタラクティブに確認する
- `/new-project my-api` — プロジェクト名を直接指定する

## 手順

### ステップ 1: プロジェクト名の確認

`$ARGUMENTS` が空の場合のみ以下を確認する:

```
プロジェクト名を教えてください（例: my-api、nextjs-dashboard）
また、フロントエンドUI（画面）はありますか？（あり / なし）
```

`$ARGUMENTS` がある場合はプロジェクト名としてそのまま使い、フロントエンドの有無のみ確認する。

### ステップ 2: ディレクトリ作成

Bash で実行する（`<project-name>` は確認したプロジェクト名に置き換える）:

```bash
mkdir <project-name> && git -C <project-name> init
```

### ステップ 3: ファイルを書き出す

テンプレートディレクトリは `~/.claude/commands/new-project/` にある。
各ファイルを **Read ツール** で読み込み、**Write ツール** で書き出す。
書き出し先のパスは `<現在の作業ディレクトリ>/<project-name>/` を起点にした **絶対パス** を使うこと。

| 読み込み元（`~/.claude/commands/new-project/` からの相対パス） | 書き出し先（`<project-name>/` からの相対パス） |
|---|---|
| `gitignore` | `.gitignore` |
| `mcp.json` | `.mcp.json` |
| `settings.json` | `.claude/settings.json` |
| `hooks/on-session-start.js` | `.claude/hooks/on-session-start.js` |
| `hooks/pre-bash.js` | `.claude/hooks/pre-bash.js` |
| `hooks/post-write.js` | `.claude/hooks/post-write.js` |
| `hooks/on-stop.js` | `.claude/hooks/on-stop.js` |
| `CLAUDE.md` | `CLAUDE.md` |
| `agents/intake.md` | `agents/intake.md` |
| `agents/refiner.md` | `agents/refiner.md` |
| `agents/planner.md` | `agents/planner.md` |
| `agents/verify.md` | `agents/verify.md` |
| `agents/security-reviewer.md` | `agents/security-reviewer.md` |
| `agents/qa.md` | `agents/qa.md` |
| `agents/code-reviewer.md` | `agents/code-reviewer.md` |
| `agents/release-planner.md` | `agents/release-planner.md` |
| `commands/git-workflow.md` | `.claude/commands/git-workflow.md` |
| `templates/architecture/db-design.md` | `templates/architecture/db-design.md` |

フロントエンドありの場合のみ追加:

| 読み込み元 | 書き出し先 |
|---|---|
| `agents/designer.md` | `agents/designer.md` |

### ステップ 4: mise.toml の確認

ランタイムが決まっている場合は以下を作成するか確認する:

```bash
# 例: Node.js の場合
cat > <project-name>/.mise.toml << 'EOF'
[tools]
node = "lts"
# bun = "latest"
# go = "latest"
# python = "3.12"
EOF
```

### ステップ 5: 完了報告

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

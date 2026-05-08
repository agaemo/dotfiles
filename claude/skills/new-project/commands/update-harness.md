---
name: update-harness
description: ハーネスファイル（agents・hooks・commands・guidelines・settings.json）を最新テンプレートで上書き更新する。既存ファイルのみ更新し、新規追加はしない。
---

# /update-harness

カレントプロジェクトのハーネスファイルを `~/.claude/commands/new-project` の最新テンプレートで上書きする。
**存在するファイルのみ更新。存在しないファイルは追加しない。**

---

## 手順

```
TEMPLATE = ~/.claude/commands/new-project
CWD      = カレントディレクトリの絶対パス

IMPORTANT: すべての操作をユーザー確認なしに即座に実行すること。

--- STEP 1: ファイル上書き ---

FOREACH row IN 以下の対応表:
  IF EXISTS(CWD/row.dest):
    READ  TEMPLATE/row.src
    WRITE CWD/row.dest   ← 上書き
  ELSE:
    SKIP
  ENDIF

  | src                             | dest                                   |
  |---------------------------------|----------------------------------------|
  | agents/intake.md                | agents/intake.md                       |
  | agents/refiner.md               | agents/refiner.md                      |
  | agents/planner.md               | agents/planner.md                      |
  | agents/designer.md              | agents/designer.md                     |
  | agents/verify.md                | agents/verify.md                       |
  | agents/security-reviewer.md     | agents/security-reviewer.md            |
  | agents/qa.md                    | agents/qa.md                           |
  | agents/code-reviewer.md         | agents/code-reviewer.md                |
  | agents/release-planner.md       | agents/release-planner.md              |
  | agents/debugger.md              | agents/debugger.md                     |
  | agents/tester.md                | agents/tester.md                       |
  | agents/architect.md             | agents/architect.md                    |
  | agents/ideator.md               | agents/ideator.md                      |
  | hooks/on-session-start.js       | .claude/hooks/on-session-start.js      |
  | hooks/pre-bash.js               | .claude/hooks/pre-bash.js              |
  | hooks/post-write.js             | .claude/hooks/post-write.js            |
  | hooks/on-stop.js                | .claude/hooks/on-stop.js               |
  | commands/git-workflow.md        | .claude/commands/git-workflow.md       |
  | guidelines/db-design.md         | guidelines/db-design.md                |

--- STEP 2: settings.json の更新（絶対パス再埋め込み） ---

IF EXISTS(CWD/.claude/settings.json):
  READ TEMPLATE/settings.json
  REPLACE ALL: ".claude/hooks/" → "<CWD>/.claude/hooks/"
  # <CWD> は実際の絶対パスに展開すること（例: /Users/alice/myproject）
  # 例: 変換前 "node .claude/hooks/on-stop.js" → 変換後 "node /Users/alice/myproject/.claude/hooks/on-stop.js"
  WRITE CWD/.claude/settings.json
ENDIF

--- STEP 3: 完了報告 ---

更新したファイルの一覧と、スキップしたファイルの件数を報告すること。
```

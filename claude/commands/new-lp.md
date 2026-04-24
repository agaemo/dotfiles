---
name: new-lp
description: ランディングページ（LP）や静的ページのプロジェクトを新規作成する。
---

# /new-lp

Astro + Node.js でランディングページ（LP）プロジェクトをセットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-lp` — カレントディレクトリに LP をセットアップする

---

## 手順

### ステップ 1: デザイン（designerエージェントで実行）

```
REQUIRE: カレントディレクトリがプロジェクトルートであること

IF NOT EXISTS(docs/):
  MKDIR docs/
ENDIF

IF NOT EXISTS(docs/design-brief.md):
  COPY ~/.claude/commands/new-project/templates/design-brief.md
    → <cwd>/docs/design-brief.md
ENDIF

ASSERT EXISTS(docs/design-brief.md)

RUN: Agent ツールで designer エージェントを起動する（完了まで待機）
  designer はヒアリングを行い、docs/design-brief.md の TODO を埋める
  コンポーネント構成・カラーパレット・タイポグラフィを決める

THEN: デザインブリーフの内容を確認する
```

---

### ステップ 2: 理解度チェック（Early Stop）& ユーザー確認

designer のヒアリング後でも、AI が仮定で埋めた部分が残っている可能性がある。
セットアップ前にここで潰す。

```
REPEAT:
  SELF_EVALUATE: 以下の5項目を 1〜5 で採点する
    スケール: 1=全く不明 / 2=断片的 / 3=概ね把握 / 4=ほぼ確信 / 5=完全に理解

    | # | 評価項目                                          | スコア |
    |---|---------------------------------------------------|--------|
    | 1 | 目的・ターゲット（誰に・何を伝えるLPか）            |        |
    | 2 | コンテンツ・訴求ポイント（何を見せるか・伝えるか）  |        |
    | 3 | デザイン方針（ビジュアルトーン・ブランド制約）      |        |
    | 4 | 技術的制約（アニメーション・フォーム・外部連携）    |        |
    | 5 | 完了条件（何をもって完成とするか・公開先・締め切り）|        |

  IF ANY(score < 4):
    ASK USER: スコアが4未満の項目について不明点を質問する
  ENDIF
UNTIL ALL(score >= 4)

GATE: ユーザー承認
  SHOW USER:
    "デザインブリーフが完成しました。この方針で実装を進めますか？"
  WAIT_FOR: ユーザーが明示的に承認する
  PROHIBITED: 承認を受け取る前にステップ3へ進むこと
  IF NOT CONFIRMED: STOP
```

---

### ステップ 3: セットアップ（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、以下のプロンプトを渡す。
**変数 `<cwd>` は実際の絶対パスに展開してから渡すこと。**
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト:**

```
以下の STEP を上から順に実行してください。スキップ禁止。

CWD        = <現在の作業ディレクトリの絶対パス>
TEMPLATE   = ~/.claude/commands/new-project

--- STEP 1: Node / pnpm 環境構築 ---

REQUIRE: カレントディレクトリが CWD であること

RUN:
  mise use --path mise.toml node@lts
  mise use --path mise.toml pnpm@latest
NOTE: --path mise.toml を必ず付けること（付けないと上位の mise.toml が更新される）

RUN:
  mise install

ASSERT: `mise exec -- node --version` が成功すること
ASSERT: `mise exec -- pnpm --version` が成功すること

--- STEP 2: Astro プロジェクト作成 ---

RUN:
  mise exec -- pnpm create astro@latest . --template minimal --no-git

ASSERT EXISTS(package.json)

--- STEP 3: ファイル書き出し ---

FOREACH row IN 以下の対応表:
  IF row.dest == ".gitignore":
    READ TEMPLATE/gitignore
    MERGE INTO CWD/.gitignore （既存の Astro 生成内容に追記。上書き禁止）
  ELSE:
    READ  TEMPLATE/row.src
    WRITE CWD/row.dest
  ENDIF

  | src                           | dest                                 |
  |-------------------------------|--------------------------------------|
  | gitignore                     | .gitignore                           |
  | mcp.json                      | .mcp.json                            |
  | settings.json                 | .claude/settings.json                |
  | hooks/on-session-start.js     | .claude/hooks/on-session-start.js    |
  | hooks/pre-bash.js             | .claude/hooks/pre-bash.js            |
  | hooks/post-write.js           | .claude/hooks/post-write.js          |
  | hooks/on-stop.js              | .claude/hooks/on-stop.js             |
  | CLAUDE.md                     | CLAUDE.md                            |
  | agents/designer.md            | agents/designer.md                   |
  | commands/git-workflow.md      | .claude/commands/git-workflow.md     |

--- STEP 4: git 初期化 ---

RUN:
  git init

ASSERT EXISTS(.git/)

--- STEP 5: ネイティブ依存関係のビルド承認 ---

RUN:
  mise exec -- pnpm approve-builds --all
NOTE: esbuild・sharp などの postinstall を承認しないと dev サーバー起動時にエラーになる

IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 6: ビルド確認 ---

RUN:
  mise exec -- pnpm run build

IF build FAILED:
  REPORT: エラー内容を報告する
  STOP
ENDIF

--- STEP 7: セットアップ確認 ---

FOREACH path IN [
  .claude/settings.json,
  .claude/hooks/on-stop.js,
  CLAUDE.md,
  agents/designer.md
]:
  IF NOT EXISTS(CWD/path):
    READ  TEMPLATE/<対応する src>
    WRITE CWD/path
  ENDIF
  ASSERT EXISTS(CWD/path)

--- STEP 8: 完了報告 ---

REPORT: "完了しました"
```

---

### ステップ 4: 完了報告

```
REPORT TO USER:
  LP プロジェクトのセットアップが完了しました。
  （詳細はサブエージェントの報告を参照）

  次のステップ:
  1. CLAUDE.md の TODO をプロジェクトの内容で埋める
  2. セクション単位で .astro コンポーネントに分割して実装する
  3. Puppeteer MCP で画面確認して完了

IF 未完了タスクがある状態でセッションを終了する場合:
  SAVE TO MEMORY: 残タスクの一覧
  NOTE: 保存しないと次のセッションで「続きをお願いします」が機能しない
```

---

## 注意事項

- `intake` / `planner` / `security-reviewer` / `qa` は不要
- 単一 HTML ファイルで実装しない（メンテナンス性が著しく低下するため）
- フレームワークのインストール手順は必ず公式ドキュメントを確認すること

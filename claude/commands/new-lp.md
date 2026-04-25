---
name: new-lp
description: Astro + Node.js でLP・静的ページを新規作成する。/new-project の LP 特化版（デザインファーストで開始、intake・planner・qa 不要）。動的機能・バックエンドが必要なら /new-project を使うこと。
---

# /new-lp

Astro + Node.js でランディングページ（LP）プロジェクトをセットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 使い方

- `/new-lp` — カレントディレクトリに LP をセットアップする
- 動的機能・バックエンドが必要なら `/new-project` を使うこと（intake → planner → 実装のフルチェーン）

---

## 手順

### ステップ 1: ヒアリング & デザインブリーフ作成（メインClaude自身が実行）

> **注意:** サブエージェントはユーザーと対話できない。ヒアリングは必ずメインClaude自身が行うこと。

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

--- ヒアリング（SELF = メインClaudeがユーザーに直接質問する） ---

SELF: 以下を 1つのメッセージ でユーザーに質問する
  1. 業種・サービス内容とターゲットユーザー（誰に届けたいか）
  2. 画面の明暗（ダーク系 / ライト系 / どちらでも）
  3. 色の方向性（使いたい色・避けたい色・ブランドカラーの有無）
  4. 文字の印象（A. 丸みがあって親しみやすい / B. きっちり直線的 / C. どちらでもない）
  5. 参考にしたいデザイン（サービス名 + 好きな部分を1〜3つ、なければ「なし」でOK）
  6. 感じてほしい印象（FEEL 3語）・感じてほしくない印象（ANTI-FEEL 3語）

WAIT_FOR: ユーザーの回答

--- デザインブリーフ作成（SELF = メインClaudeが記入する） ---

SELF: ヒアリング回答をもとに docs/design-brief.md の全TODOを埋める
  - ブランドアーキタイプはヒアリング結果から推定して選択する
  - 仮定で埋めた項目がある場合は、その旨をユーザーに明示すること

--- サロン名・ブランド名の決定 ---

ユーザーからサロン名の指定がない場合:
  RECOMMENDED: 「SAMPLE SALON」「DEMO HAIR」など、サンプルであることが一目でわかる名前を使う
  ALTERNATIVE: ユーザーに希望を確認する
  PROHIBITED: 実在するブランド・店舗・通販サイトの名前を参考にして流用すること
  理由: 後から名前変更が必要になると、レイアウト崩れ・文言の意味的不整合が連鎖して発生する

THEN: 埋めたデザインブリーフの内容をユーザーに簡潔に見せる
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

---

## 名前変更が発生した場合のチェックリスト

ユーザーがブランド名・サロン名の変更を依頼した場合、以下を順番に実行する。

### 1. sed 置換は「長いパターンを先に」並べる

部分文字列が先にマッチして誤変換が起きるのを防ぐため、より具体的なパターンを上に置く。

```bash
# 悪い例（ルミエール が先にマッチして プルミエール → プエシャンティヨン になる）
sed -e 's/ルミエール/エシャンティヨン/g' \
    -e 's/プルミエール/エシャンティヨン/g'

# 良い例（完全一致を先に処理してから部分一致）
sed -e 's/プルミエール/エシャンティヨン/g' \
    -e 's/ルミエール/エシャンティヨン/g'
```

### 2. 名前の「意味・由来」に依存する文言を手動で確認する

機械的な文字列置換では意味まで更新できない。置換後に以下を grep して確認する。

```bash
grep -rn "フランス語\|意味\|由来\|語源" src/
```

見つかった箇所は新しい名前の意味・由来に合わせて書き直す。

### 3. 大きく表示する要素の文字数が変わった場合はフォントを見直す

ヒーロー・見出しなど `clamp()` でサイズを指定している要素は、文字数が増えると viewport からはみ出す。

```
旧名: LUMIÈRE（7文字）→ 新名: ÉCHANTILLON（11文字、+57%）
```

変更後は必ず `font-size` と `letter-spacing` を文字数に合わせて調整する。

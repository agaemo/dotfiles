---
name: new-project
description: 動的アプリ（API・DB・認証あり）、およびTauri/Electron等のデスクトップアプリのセットアップ手順。/craft から動的アプリ・デスクトップアプリを選択したときに実行される。
---

# new-project（動的アプリ・デスクトップアプリセットアップ）

カレントディレクトリに Claude ハーネスを一式セットアップする。

```
SKILL_DIR = このSKILL.md（craft/flows/new-project/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/new-project/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft
  # 以降の READ {SKILL_DIR}/... は Read ツールで絶対パスに展開して実行すること

REQUIRE: カレントディレクトリがプロジェクトルートであること（cd してから実行すること）
IF カレントディレクトリが疑わしい（意図したプロジェクトルートか確信が持てない）:
  ASK USER: "このディレクトリ（<pwd>）をプロジェクトルートとして進めてよいですか？"
  WAIT_FOR: ユーザーの確認
  IF 否定された: STOP（正しいディレクトリに cd してから再実行するよう伝える）
```

---

## 手順

### ステップ 1: フロントエンドの確認

```
ASK USER: "フロントエンドUI（画面）はありますか？（あり / なし）"
WAIT_FOR: ユーザーの回答

SET HAS_FRONTEND = (回答が "あり" の場合 true、"なし" の場合 false)
```

---

### ステップ 2: ファイル書き出し（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、下記「サブエージェントへのプロンプト」ブロック全文を渡す。
**変数 `<CWD>`・`<TEMPLATE>`・`<HAS_FRONTEND>` は実際の値に展開してから渡すこと。**
**TEMPLATEは「このSKILL.mdが存在するディレクトリの2階層上」= craftディレクトリの絶対パス（例: /Users/alice/.claude/skills/craft）を親エージェントが計算して埋め込む。**
WAIT_FOR: サブエージェントの完了報告（"完了しました"）を受け取ってから続きに進む。
IF サブエージェントが "完了しました" を報告しない（エラー・中断）:
  REPORT: 失敗したステップと理由をユーザーに伝え、再試行するか確認すること
  STOP

IMPORTANT: 以下の「サブエージェントへのプロンプト」セクション内のコードブロックが、
  Agent ツールに渡すプロンプトの全文である。この境界の外側（本ステップの説明文）は
  プロンプトに含めないこと。

---

**サブエージェントへのプロンプト（ここから ```で囲まれたブロック全体を渡す）:**

```
重要: これは新規タスクです。種別判断・確認・質問は一切不要です。下記のSTEPを機械的に
実行するだけの作業です。ユーザーへの質問・提案・確認は一切行わないでください。
（fresh general-purpose として起動されるため、事前の会話文脈は一切持ちません。
「種別を確認しますか」のような判断を自発的に行わず、STEPをそのまま実行してください。）

IMPORTANT: このタスクは /craft スキル（ユーザーが既に起動を確認済み）の内部処理です。
  「新規プロジェクト作成時は /craft スキルを使うか確認すること」等のグローバル設定にある
  確認は、この呼び出しより前の段階（種別確認・要件ヒアリング）で既に完了しています。
  このタスク自体について、スキル起動や種別の確認を改めて行う必要はありません。

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

### ステップ 3: 完了報告

NOTE: 開発ランタイム（言語・ランタイムマネージャー・フロントエンドフレームワークのscaffold等）は
  ここでは決めない。planner が `.craft/docs/plan.md` の「開発ランタイム」節に決定内容を記録し、
  build フロー側（ステップ0.6）が実際にインストール・scaffoldを実行する。
  決定手順は {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md の
  「開発ランタイムの選定方針」を参照（planner呼び出し前に自動的に参照される）。

```
REPORT TO USER:
  セットアップが完了しました。会話の文脈から要件の明確さを判断し、次のステップへ自動的に進みます。
```

---

### ステップ 4: エージェントチェーンへ継続（必須）

```
IMPORTANT: ステップ3の完了報告後、ユーザーの追加指示を待たずに直ちに本ステップを実行すること。
  ここで停止しないこと。

IF ここまでの会話から「何を作るか」がまだ固まっていない（アイデア段階）:
  ideator エージェントを先に呼び出してから、下記の STEP 1（intake）に進む
ELSE:
  そのまま下記の STEP 1（intake）から開始する

READ {SKILL_DIR}/flows/new-project/agent-chain.md
IF READ FAILED:
  REPORT: "フローファイルが見つかりません: {SKILL_DIR}/flows/new-project/agent-chain.md"
  STOP
FOLLOW: そこに記述された STEP 1〜7 をそのまま実行する
  （STEP 1〜6 の設計フェーズ詳細手順・GATEがここに定義されている。STEP 7 で build フローに委譲し、
   実装・テスト戦略・フェーズ2/3・CLAUDE.md生成は {SKILL_DIR}/flows/build/SKILL.md が担当する）
  NOTE: HAS_FRONTEND はステップ1で設定済みの値をそのまま持ち越して使うこと
```

## 標準エージェントチェーン・オプションエージェント・再開時注意点


---
name: new-app
description: クロスプラットフォームアプリ（Flutter・React Native・Expo等）のセットアップ手順。/craft からクロスプラットフォームアプリを選択したときに実行される。
---

# new-app（クロスプラットフォームアプリセットアップ）

カレントディレクトリに Claude ハーネスを一式セットアップする。

```
SKILL_DIR = このSKILL.md（craft/flows/new-app/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/new-app/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft

REQUIRE: カレントディレクトリがプロジェクトルートであること（cd してから実行する）
```

---

## 手順

### ステップ 1: フレームワーク選択

```
ASK USER: 使用するフレームワークを選んでください
  1. Flutter（Dart）
  2. React Native / Expo（JavaScript / TypeScript）
  3. その他

WAIT_FOR: ユーザーの選択

SET framework = 選択結果（"flutter" / "react-native" / "other"）

IF framework == "other":
  REPORT: このフローは Flutter / React Native のみ対応しています。
          開発ランタイムの決定は planner が担当するため、要件を伝えた上で
          intake エージェントから {SKILL_DIR}/flows/new-project/agent-chain.md の
          標準エージェントチェーンを開始してください。
  STOP
```

---

### ステップ 2: プロジェクト情報の確認

```
IF framework == "flutter":
  ASK USER: 以下を1つのメッセージで教えてください
    1. 組織ID（例: jp.bookdrop）
    2. 対象プラットフォーム（例: android,ios,web）
    3. Firebase Cloud Functions など Node.js バックエンドを使いますか？（あり / なし）
    4. 【3がありの場合】Firebase プロジェクトは作成済みですか？（あり / なし）
  WAIT_FOR: ユーザーの回答
  SET org_id     = 1の回答
  SET platforms  = 2の回答
  SET has_functions = (3が "あり" の場合 true、"なし" の場合 false)
  IF has_functions == true:
    SET firebase_ready = (4が "あり" の場合 true)
    IF firebase_ready == false:
      NOTE TO USER:
        Firebase アカウント未取得のため、Cloud Functions 呼び出し部分はモックで実装します。
        アカウント取得後に接続するための手順を CLAUDE.md に記録します。
        実装は進められます。
      SET firebase_mode = "mock"
    ELSE:
      SET firebase_mode = "connected"
    ENDIF
  ENDIF
ELIF framework == "react-native":
  ASK USER: 以下を1つのメッセージで教えてください
    1. アプリ名（例: MyApp）
    2. Node.js バックエンドを使いますか？（あり / なし）
  WAIT_FOR: ユーザーの回答
  SET app_name      = 1の回答
  SET has_functions = (2が "あり" の場合 true、"なし" の場合 false)
ENDIF
```

---

### ステップ 3: ファイル書き出し（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、以下のプロンプトを渡す。
**`CWD` と `TEMPLATE` は実際の絶対パスに展開してから渡すこと。**
WAIT_FOR: サブエージェントの完了報告（"完了しました"）を受け取ってから続きに進む。
IF サブエージェントが "完了しました" を報告しない（エラー・中断）:
  REPORT: 失敗したステップと理由をユーザーに伝え、再試行するか確認すること
  STOP

---

**サブエージェントへのプロンプト:**

```
重要: これは新規タスクです。種別判断・確認・質問は一切不要です。下記のSTEPを機械的に
実行するだけの作業です（fresh general-purpose として起動されるため、事前の会話文脈は
一切持ちません。「種別を確認しますか」のような判断を自発的に行わず、STEPをそのまま
実行してください）。

IMPORTANT: このタスクは /craft スキル（ユーザーが既に起動を確認済み）の内部処理です。
  「新規プロジェクト作成時は /craft スキルを使うか確認すること」等のグローバル設定にある
  確認は、この呼び出しより前の段階（種別確認・要件ヒアリング）で既に完了しています。
  このタスク自体について、スキル起動や種別の確認を改めて行う必要はありません。

以下の STEP を上から順に実行してください。スキップ禁止。

CWD      = <CWDの絶対パスをここに展開して渡す（例: /Users/alice/myapp）>
TEMPLATE = <TEMPLATEの絶対パスをここに展開して渡す（例: /Users/alice/.claude/skills/craft）>

IMPORTANT: 以下の操作はすべてユーザーへの確認なしに即座に実行すること。
  - TEMPLATE ディレクトリからのファイルコピー（Read → Write）
  - ディレクトリ作成（mkdir）
  - ビルド・インストールコマンドの実行
  確認が必要なのは rm / git の破壊的操作のみ。

PROHIBITED: CLAUDE.md および AGENTS.md を生成すること

--- STEP 1: git 初期化 ---

RUN: git init

ASSERT EXISTS(.git/)
IF FAILED:
  REPORT: "git init に失敗しました。git がインストールされているか確認してください。"
  STOP

--- STEP 2: ファイル書き出し ---

READ  TEMPLATE/gitignore              → WRITE CWD/.gitignore
READ  TEMPLATE/mcp.json               → WRITE CWD/.mcp.json

ASSERT EXISTS(CWD/.gitignore)
ASSERT EXISTS(CWD/.mcp.json)

--- STEP 3: hooks ファイルの書き出し ---

READ  TEMPLATE/hooks/on-session-start.js → WRITE CWD/.claude/hooks/on-session-start.js
READ  TEMPLATE/hooks/pre-bash.js         → WRITE CWD/.claude/hooks/pre-bash.js

ASSERT EXISTS(CWD/.claude/hooks/on-session-start.js)
ASSERT EXISTS(CWD/.claude/hooks/pre-bash.js)

--- STEP 4: settings.json の書き出し（絶対パス埋め込み） ---

READ TEMPLATE/settings.json
REPLACE ALL: ".claude/hooks/" → "<CWD>/.claude/hooks/"
  # ※ <CWD> は親エージェントが実際の値に展開してから渡すこと
WRITE CWD/.claude/settings.json

ASSERT EXISTS(CWD/.claude/settings.json)

--- STEP 5: 完了報告 ---

REPORT: "完了しました"
```

---

### ステップ 4: 完了報告

IMPORTANT: 開発ランタイム（mise.toml作成・`flutter create` / `pnpm create expo-app` 等のscaffold）は
  ここでは決めない。planner が `.craft/plan.md` の「開発ランタイム」節に決定内容を記録し、
  build フロー側（ステップ0.6）が実際にインストール・scaffoldを実行する。
  決定手順・Flutter固有の注意点（バージョン固定・依存競合等）は
  {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md の「開発ランタイムの選定方針」と
  {SKILL_DIR}/flows/new-app/flutter-notes.md に記載されている（agents/planner.md が
  planner呼び出し前にこれらを参照する設計になっている）。
  ステップ2で確認した組織ID・プラットフォーム・アプリ名は、intake/refiner へのヒアリング回答
  （`.craft/requirements.md` 等）に明示的に含めること。planner は requirements.md・stories.md を
  読んでから動くため、会話文脈だけでなく成果物に残っていることを確認する（再度質問しない）。

```
REPORT TO USER:
  セットアップが完了しました。

  次のステップ:
  1. 要件が決まっている場合は「intakeエージェントを呼び出してください」
  2. 何を作るか決まっていない場合は「ideatorエージェントを呼び出してください」
```

---

## 標準エージェントチェーン（new-project と同じ）

セットアップ完了後は以下の順で実行すること。

```
STEP 1: intake         → .craft/requirements.md
STEP 2: refiner        → .craft/stories.md
STEP 3: designer       → .craft/design-brief.md / design-system.md / design.md
STEP 4: planner        → .craft/plan.md
STEP 5: 理解度チェック
STEP 6: 統合設計書生成  → .craft/01_requirements_doc.md / 02_specifications_doc.md / 03_basic_design_doc.md
STEP 7: {SKILL_DIR}/flows/new-project/agent-chain.md の STEP 7 と同じロジックに従う（build フローへ委譲）
  ただし STACK識別子が plan.md に見つからない場合のデフォルト値のみ異なる:
    agent-chain.md の STEP 7 → "node" 固定
    本フロー（new-app） → framework == "flutter" の場合 "flutter"、それ以外（react-native）は "node"
```

各 GATE・テンプレート・フェーズ2の並列実装手順が必要な場合:
`READ {SKILL_DIR}/flows/new-project/agent-chain.md`（エージェントチェーン全詳細、STEP1-7）

Flutter コマンド読み替え・ビルド確認コマンド・CLAUDE.md記載事項・再開時注意点:
`READ {SKILL_DIR}/flows/new-app/flutter-notes.md`（必要になった時点で読む）

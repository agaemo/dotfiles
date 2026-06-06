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
          .mise.toml を手動で作成し、エージェントチェーンから再開してください。
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

--- STEP 2: ファイル書き出し ---

READ  TEMPLATE/gitignore              → WRITE CWD/.gitignore
READ  TEMPLATE/mcp.json               → WRITE CWD/.mcp.json
READ  TEMPLATE/flows/git-workflow/SKILL.md → WRITE CWD/.claude/commands/git-workflow.md

ASSERT EXISTS(CWD/.gitignore)
ASSERT EXISTS(CWD/.mcp.json)
ASSERT EXISTS(CWD/.claude/commands/git-workflow.md)

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

### ステップ 4: mise.toml の作成と `mise install`

フレームワークと has_functions に応じて以下のテンプレートを使用する。

#### Flutter（has_functions = false）

```bash
# 利用可能な最新バージョンを確認してから固定すること
# mise ls-remote flutter | tail -1
cat > .mise.toml << 'EOF'
[tools]
flutter = "3.41.9"  # ← mise ls-remote flutter | tail -1 で確認した値に更新

[env]
_.path = ["./bin"]
EOF

mise trust && mise install
```

> **注意:** `flutter = "stable"` は 404 エラーになる。必ず具体的なバージョン番号を指定すること。

#### Flutter（has_functions = true）

Firebase Cloud Functions など Node.js バックエンドを含む場合。

```bash
cat > .mise.toml << 'EOF'
[tools]
flutter = "3.41.9"  # ← mise ls-remote flutter | tail -1 で確認した値に更新
node = "22"
pnpm = "latest"

[env]
_.path = ["./bin", "./node_modules/.bin"]
EOF

mise trust && mise install
```

#### React Native / Expo

```bash
cat > .mise.toml << 'EOF'
[tools]
node = "22"
pnpm = "latest"

[env]
_.path = ["./node_modules/.bin"]
EOF

mise trust && mise install
```

```
ASSERT: `mise exec -- flutter --version` が成功すること（Flutter の場合）
ASSERT: `mise exec -- node --version` が成功すること（Node.js を含む場合）
IF FAILED: エラー内容を報告し、STOP すること
```

---

### ステップ 5: プロジェクト初期化

#### Flutter

```bash
# プラットフォームはステップ2で確認した内容を使う
mise exec -- flutter create . --org {org_id} --platforms {platforms}

# パッケージは flutter pub add で追加する（pubspec.yaml を手編集して pub get より推奨）
# 例: mise exec -- flutter pub add flutter_riverpod go_router hive_flutter

# 開発用パッケージ
# 例: mise exec -- flutter pub add --dev build_runner riverpod_generator
```

> **Flutter 既知の依存競合:**
> `riverpod_generator` (3.x+) と `hive_generator` は `source_gen` のバージョン要件が競合するため同時利用不可。
> Hive を使う場合は `hive_generator` を使わず、`TypeAdapter` を手動実装すること（`BinaryReader` / `BinaryWriter` を使う数十行のボイラープレート）。
> 詳細: `riverpod_generator` は `source_gen ^3.0.0+` を要求するが `hive_generator` は `source_gen ^1.0.0` を要求する。

#### React Native（Expo）

```bash
mise exec -- pnpm create expo-app . --template blank-typescript
mise exec -- pnpm install
```

#### React Native（CLI）

```bash
mise exec -- pnpm dlx @react-native-community/cli init {app_name} --directory .
mise exec -- pnpm install
```

---

### ステップ 6: 完了報告

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
STEP 7: 実装
STEP 8: designer による実画面レビュー
STEP 9: /ultrareview（オプション）
STEP 10: verify → security-reviewer → qa → code-reviewer
STEP 11: CLAUDE.md・README.md 生成 + クリーンアップ
```

各 GATE・テンプレート・フェーズ2の並列実装手順が必要な場合:
`READ {SKILL_DIR}/flows/new-project/agent-chain.md`（エージェントチェーン全詳細）

Flutter コマンド読み替え・STEP 7 確認コマンド・STEP 11 CLAUDE.md 記載事項・再開時注意点:
`READ {SKILL_DIR}/flows/new-app/flutter-notes.md`（必要になった時点で読む）

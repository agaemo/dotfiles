---
name: new-app
description: クロスプラットフォームアプリ（Flutter・React Native・Expo等）のセットアップ手順。/craft からクロスプラットフォームアプリを選択したときに実行される。
---

# new-app（クロスプラットフォームアプリセットアップ）

カレントディレクトリに Claude ハーネスを一式セットアップする。

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

### ステップ 2: バックエンド確認

```
ASK USER: Firebase Cloud Functions など Node.js バックエンドを使いますか？（あり / なし）
  ※ Flutter + Firebase Functions の組み合わせで特に重要

WAIT_FOR: ユーザーの回答

SET has_functions = (回答が "あり" の場合 true、"なし" の場合 false)
```

---

### ステップ 2.5: 追加情報の確認

```
IF framework == "flutter":
  ASK USER: アプリの組織IDを教えてください（例: jp.bookdrop）
  SET org_id = 回答

IF framework == "react-native-cli":
  ASK USER: アプリ名を教えてください（例: MyApp）
  SET app_name = 回答
```

---

### ステップ 3: ファイル書き出し（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、以下のプロンプトを渡す。
**`CWD` と `TEMPLATE` は実際の絶対パスに展開してから渡すこと。**
サブエージェントが完了したら結果のみ受け取り、続きに進む。

---

**サブエージェントへのプロンプト:**

```
以下の STEP を上から順に実行してください。スキップ禁止。

CWD      = <CWDの絶対パスをここに展開して渡す（例: /Users/alice/myapp）>
TEMPLATE = <TEMPLATEの絶対パスをここに展開して渡す（例: /Users/alice/.claude/skills/craft）>
  # craft/flows/new-app/SKILL.md の2階層上が craft/ になる

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

--- STEP 3: hooks ファイルの書き出し ---

READ  TEMPLATE/hooks/on-session-start.js → WRITE CWD/.claude/hooks/on-session-start.js
READ  TEMPLATE/hooks/pre-bash.js         → WRITE CWD/.claude/hooks/pre-bash.js

--- STEP 4: settings.json の書き出し（絶対パス埋め込み） ---

READ TEMPLATE/settings.json
REPLACE ALL: ".claude/hooks/" → "<絶対パス>/.claude/hooks/"
  # ※ <絶対パス> は親エージェントが CWD の実際の値に展開してから渡すこと
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
mise exec -- flutter create . --org {org_id} --platforms ios,android,web
# Web が不要な場合は --platforms ios,android

# 依存パッケージは pubspec.yaml に追記後 flutter pub get で追加
mise exec -- flutter pub get
```

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
詳細な手順・テンプレートは `flows/new-project/SKILL.md` の「標準エージェントチェーン」セクションを参照すること。

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

> **各 GATE・テンプレート・フェーズ2の並列実装手順は `flows/new-project/SKILL.md` を参照すること。**
> 重複を避けるため、このファイルには記載しない。

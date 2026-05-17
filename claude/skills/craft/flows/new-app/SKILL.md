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

IF has_functions == true AND framework == "flutter":
  ASK USER: Firebase プロジェクトはすでに作成済みですか？（あり / なし）
  WAIT_FOR: ユーザーの回答
  SET firebase_ready = (回答が "あり" の場合 true、"なし" の場合 false)

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
# プラットフォームはステップ2.5で確認した内容を使う
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

---

## Flutter 固有の読み替え（new-project/SKILL.md との差分）

`flows/new-project/SKILL.md` は Node.js 前提で書かれているため、Flutter プロジェクトでは以下のコマンドに読み替えること。

| new-project の記述 | Flutter での読み替え |
|-------------------|-------------------|
| `mise exec -- pnpm build` | `mise exec -- flutter analyze` |
| `mise exec -- pnpm dev` | `mise exec -- flutter run` |
| `mise exec -- pnpm test` | `mise exec -- flutter test` |

### STEP 7 実装時の確認コマンド（Flutter）

```bash
# 型エラー・静的解析
mise exec -- flutter analyze

# ビルド確認（Web で早い）
mise exec -- flutter build web

# 起動確認
mise exec -- flutter run -d chrome   # Web
mise exec -- flutter run             # 接続デバイス・シミュレーター
```

### STEP 11 CLAUDE.md に含める Flutter/Firebase 固有の記載事項

通常の項目に加えて以下を必ず記載すること:

```markdown
## 実装状態（モックと本番の境界）

- **[リポジトリクラス名]:** `[ファイルパス]` の `[変数/メソッド名]` がモックデータを返している
  - 本番化時は Cloud Functions 呼び出しに差し替える

## Firebase 接続手順（アカウント取得後）

1. `npm install -g firebase-tools && firebase login`
2. `dart pub global activate flutterfire_cli && flutterfire configure`
   - 生成される `lib/firebase_options.dart` を git に追加する
3. `main.dart` に `Firebase.initializeApp()` を追加する
4. `functions/` ディレクトリを作成: `firebase init functions`
5. Cloud Functions を実装し、[リポジトリクラス名] のモックを差し替える

## 既知の設計判断

- **hive_generator 不使用:** `riverpod_generator` と `source_gen` バージョン競合のため手動アダプタ実装
- **Riverpod バージョン:** 3.x を使用。`StateNotifier` は廃止済み。`Notifier` / `NotifierProvider` を使うこと
```

---

## 実装再開フロー

`.craft/plan.md` が存在する状態から実装を始める場合のフロー。

```
1. READ .craft/plan.md
2. READ .craft/design-system.md（存在すれば）
3. 以下を確認してユーザーに提示する:
   - 完了済みのステップ（コードが存在するか確認）
   - 未着手のステップ
   - 外部依存で未接続のもの（Firebase等）
4. 未着手のステップを plan.md の順番で実装する
5. 外部依存が未接続の場合はモックで実装し、CLAUDE.md に接続手順を記録する
6. 各ステップ完了後に `flutter analyze` でエラーがないことを確認する
```

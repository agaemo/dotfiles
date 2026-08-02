# Flutter 固有メモ（new-app セットアップ後に参照）

## コマンド読み替え（new-project/SKILL.md との差分）

`flows/new-project/SKILL.md` は Node.js 前提のため、Flutter プロジェクトでは以下に読み替えること。

| new-project の記述 | Flutter での読み替え |
|-------------------|-------------------|
| `mise exec -- pnpm build` | `mise exec -- flutter analyze` |
| `mise exec -- pnpm dev` | `mise exec -- flutter run` |
| `mise exec -- pnpm test` | `mise exec -- flutter test` |

## 環境構築・プロジェクト初期化（planner が plan.md の「開発ランタイム」節に転記する情報源）

### mise.toml テンプレート

#### Firebase Cloud Functions 等の Node.js バックエンドを含まない場合

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
mise exec -- flutter create . --org <組織ID> --platforms <プラットフォーム>
```

> **注意:** `flutter = "stable"` は 404 エラーになる。必ず具体的なバージョン番号を指定すること。

#### Firebase Cloud Functions 等の Node.js バックエンドを含む場合

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
mise exec -- flutter create . --org <組織ID> --platforms <プラットフォーム>
```

**検証コマンド:** `mise exec -- flutter --version`（Node.js を含む場合は `mise exec -- node --version` も）

### パッケージ追加

`flutter pub add` で追加する（`pubspec.yaml` を手編集して `pub get` より推奨）。
例: `mise exec -- flutter pub add flutter_riverpod go_router hive_flutter`
開発用パッケージ例: `mise exec -- flutter pub add --dev build_runner riverpod_generator`

> **既知の依存競合:** `riverpod_generator`（3.x+）と `hive_generator` は `source_gen` のバージョン要件が競合するため同時利用不可。
> Hive を使う場合は `hive_generator` を使わず、`TypeAdapter` を手動実装すること（`BinaryReader` / `BinaryWriter` を使う数十行のボイラープレート）。
> 詳細: `riverpod_generator` は `source_gen ^3.0.0+` を要求するが `hive_generator` は `source_gen ^1.0.0` を要求する。

## STEP 7 実装時の確認コマンド

```bash
mise exec -- flutter analyze      # 型エラー・静的解析
mise exec -- flutter build web    # ビルド確認（Web で早い）
mise exec -- flutter run -d chrome  # 起動確認（Web）
mise exec -- flutter run            # 接続デバイス・シミュレーター
```

## STEP 11 CLAUDE.md に含める Flutter/Firebase 固有の記載事項

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

## 再開時注意点

汎用の実装フロー（初回実装・再開共通）は `flows/build/SKILL.md` に定義されている。
Flutter プロジェクトで再開する際は以下を追加で確認すること。

```
- Firebase 接続状況を確認する:
    firebase_options.dart が存在しない → モックのまま進める
    CLAUDE.md に Firebase 接続手順が記録されているか確認する
- ビルド確認コマンドは `mise exec -- flutter analyze` を使う
- Riverpod 3.x を使っている場合、StateNotifier は廃止済み
    → Notifier / NotifierProvider を使うこと
```

# Flutter 固有メモ（new-app セットアップ後に参照）

## コマンド読み替え（new-project/SKILL.md との差分）

`flows/new-project/SKILL.md` は Node.js 前提のため、Flutter プロジェクトでは以下に読み替えること。

| new-project の記述 | Flutter での読み替え |
|-------------------|-------------------|
| `mise exec -- pnpm build` | `mise exec -- flutter analyze` |
| `mise exec -- pnpm dev` | `mise exec -- flutter run` |
| `mise exec -- pnpm test` | `mise exec -- flutter test` |

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

汎用の実装再開フローは `/craft` の `SKILL.md` に定義されている。
Flutter プロジェクトで再開する際は以下を追加で確認すること。

```
- Firebase 接続状況を確認する:
    firebase_options.dart が存在しない → モックのまま進める
    CLAUDE.md に Firebase 接続手順が記録されているか確認する
- ビルド確認コマンドは `mise exec -- flutter analyze` を使う
- Riverpod 3.x を使っている場合、StateNotifier は廃止済み
    → Notifier / NotifierProvider を使うこと
```

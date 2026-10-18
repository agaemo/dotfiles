# Rust（Tauri）の CI テンプレート

Rust/Tauri 案件の GitHub Actions を組むときの標準。`STACK識別子: rust` のときだけ適用する。

- rust-cache（`Swatinem/rust-cache`）: `main` への push で保存し、PR とタグでは復元のみ（`save-if`）。キー（`prefix-key`）を `ci.yml` とリリースのワークフローで共通にする。リリースが実際にキャッシュを復元できたか、初回の実行ログで確認する。
- ジョブ分割（並列）: lint（clippy）／test／画面の検査を別ジョブにする。clippy と test が別々にコンパイルする問題は、`cargo check` と `cargo test --no-run` の分け方、または `cargo nextest` を検討する。
- `concurrency`: 同じ ref の古い実行をキャンセルする。
- `paths-ignore`: 文書だけの変更では実行しない。
- bundle（インストーラ）: 手動実行（`workflow_dispatch`）にする。目安は macOS 約 5 分、Windows 約 5 分。

## リリースのワークフロー

- 最初から `workflow_dispatch` の `dry_run` 入力（ビルドと来歴の証明までを行い、公開しない）を持たせる。タグでしか動かせない設計にしない。
- `actionlint` を `make` のターゲットにする（`make actionlint`）。
- 成果物が 0 件のとき失敗するガードを入れる（`upload-artifact` は共通の親フォルダからの相対パスを保つため、階層が深くなり、`SHA256SUMS` が空の入力のハッシュで静かに作られた実例がある）。
- シェルの部分は、成果物の階層を模したフォルダで、ローカルで動かして確認する。

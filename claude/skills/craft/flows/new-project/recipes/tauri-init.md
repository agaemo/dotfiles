# Tauri（Rust）初期化手順

デスクトップアプリ（macOS/Windows/Linux）を Rust + Tauri 2 で構築する場合の手順。`STACK識別子: rust`。

## 環境管理ツール

`mise`をデフォルトとする（`planner-checklist.md`の原則どおり）。**rustupを単体で直接使う手順を提案しないこと** — miseの`core:rust`バックエンドが内部でrustupを使って導入するため、miseに一本化した方がバージョン固定・他言語との管理方法の一貫性の両面で優れる。

```bash
cat > .mise.toml <<'EOF'
[tools]
rust = { version = "<固定バージョン>", components = "rustfmt,clippy" }
EOF
mise trust
mise install
```

## ツールチェーン導入

```bash
mise exec -- cargo install create-tauri-app --locked
mise exec -- cargo install tauri-cli --version "^2" --locked
```

## プロジェクトのscaffold

**IMPORTANT: プロジェクトルートには`.git`・`.craft`・`.claude`が既に存在するため、`cargo create-tauri-app`をカレントディレクトリへ直接実行すると非空ディレクトリと判定され、意図しない挙動になる場合がある。** 一時ディレクトリへscaffoldしてからマージすること。

```bash
mise exec -- cargo create-tauri-app _scaffold --template vanilla --manager cargo --yes
```

フロントエンドは、要件でNode.jsビルドチェーンを避ける方針が明示された場合は`--template vanilla`（素のHTML/CSS/JS）を使う。React/Vue等のフレームワークが必要な場合はNode.js導入とテンプレート選定をこの時点でユーザーに確認する。

### マージ時の衝突に注意（IMPORTANT）

`rsync -a _scaffold/ ./`のような単純なマージは、**scaffoldテンプレート側の`.gitignore`・`README.md`がcraftテンプレート側の同名ファイルを無条件に上書きする。** 特に`.gitignore`はcraftテンプレートが`.craft/`除外等を書き込み済みのため、上書きされると`.craft/`が誤ってコミット対象になりうる。

手順:
1. マージ前に既存の`.gitignore`・`README.md`の内容を退避する（Readで内容を記憶する、または別名でコピーする）
2. `rsync -a _scaffold/ ./ && rm -rf _scaffold`でマージする
3. マージ後、`.gitignore`はcraftテンプレート由来の内容（`.craft/`・`.env`等の除外）とscaffold由来の内容（`src-tauri/target/`等のビルド成果物除外）を統合して書き直す。片方を優先して上書きしない
4. `README.md`はどのみちbuildフローのステップ6で実際のプロジェクト内容に基づいて書き直すため、マージ後の内容は一時的なものとして扱ってよい

## 依存クレートの追加

必要なクレートは`cargo add`で追加する（バージョンはCargo.lockが実際の値を固定するため、Cargo.toml側は`major`バージョンの指定で十分）。

```bash
mise exec -- cargo add --manifest-path src-tauri/Cargo.toml <クレート名>@<バージョン>
```

## tauri.conf.json の調整

- `productName`・`identifier`（`com.<ドメイン等>.<アプリ名>`形式）を実際のプロジェクト名に置き換える
- ウィンドウをRust側で動的生成する設計にする場合は`app.windows`を空配列にし、`src-tauri/src/lib.rs`の`.setup()`内で`WebviewWindowBuilder`を呼ぶ
- 透過ウィンドウ（`transparent(true)`）を使う場合、macOSでは`"macOSPrivateApi": true`が必須。加えて`Cargo.toml`の`tauri`依存に`features = ["macos-private-api"]`も必要（`tauri.conf.json`側の設定だけでは`cargo build`がエラーになる）

## Cargo.toml の `[profile.release]`

Tauriのデフォルトscaffoldは`panic = "abort"`を含む。**アプリ内でパニック隔離（`catch_unwind`によるスレッド単位の防御等）を行う設計の場合、`panic = "abort"`はその防御を無効化する**（unwindせず即座にプロセスを終了させるため）。堅牢性を優先する場合はこの設定を外すこと（バイナリサイズとのトレードオフになるため、方針をplan.mdの「使用ライブラリ」または「リスク」セクションに明記する）。

## 開発コマンド（Makefile向け）

| ターゲット | 実行コマンド |
|---|---|
| `make dev` | `mise exec -- cargo tauri dev` |
| `make build` | `mise exec -- cargo build --manifest-path src-tauri/Cargo.toml --all-targets`（型・コンパイルエラー検出用。`.app`は作らない） |
| `make test` | `mise exec -- cargo test --manifest-path src-tauri/Cargo.toml` |
| `make fmt` | `mise exec -- cargo fmt --manifest-path src-tauri/Cargo.toml --all` |
| `make lint` | `mise exec -- cargo clippy --manifest-path src-tauri/Cargo.toml --all-targets -- -D warnings` |
| `make bundle` | `mise exec -- cargo tauri build`（配布用`.app`生成。数分かかるため`make build`とは分離する） |

**IMPORTANT: 一度Makefileを生成したら、以降のビルド・テスト・lint確認は必ず`make <target>`を経由すること。`mise exec -- cargo ...`を直接叩かないこと（`build/SKILL.md`の原則）。** 上記の表に無いコマンドが必要になった場合は、直接実行せず対応するMakefileターゲットを追加してから使うこと。

## 配布・署名

App Store配布・コード署名/公証を行わない場合、生成される`.app`は署名なしのため受け取った側はGatekeeperの警告が出る（右クリック→開く、または`xattr -dr com.apple.quarantine`で回避可能）。この制約はREADME.mdに明記すること。

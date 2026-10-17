# Bun / Python ランタイム設定

## Bun プロジェクト

```bash
cat > .mise.toml << 'EOF'
[tools]
bun = "1.3"
node = "lts"   # ネイティブモジュール実行用

[env]
_.path = ["./node_modules/.bin"]
EOF

mise trust && mise install
```

> 注意: better-sqlite3・drizzle-kit 等のネイティブモジュールは Node.js でしか動かない場合がある

## Python プロジェクト（uv をパッケージマネージャーとして使用）

> 注意: Pythonのバージョンは時間とともにサポート状況が変わる（3.12はバグ修正が終了済み）。
> 採用前に https://devguide.python.org/versions/ で現行のバグ修正対象版を確認し、
> 下記の `python` を更新すること。

```bash
cat > .mise.toml << 'EOF'
[tools]
python = "3.14"
uv = "latest"

[env]
_.path = [".venv/bin"]
EOF

mise trust && mise install
uv init --no-package   # アプリ・スクリプト用途（ビルドシステム不要）。ライブラリなら --lib
uv sync
```

> 注意: uv 0.12 以降、`uv init` は既定でビルドシステムを宣言する（パッケージ化前提）。
> パッケージ化が不要なら `--no-package` を付ける。

検証:
```bash
mise exec -- python --version
mise exec -- uv --version
```

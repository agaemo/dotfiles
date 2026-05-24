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

```bash
cat > .mise.toml << 'EOF'
[tools]
python = "3.12"
uv = "latest"

[env]
_.path = [".venv/bin"]
EOF

mise trust && mise install
uv venv
uv sync
```

検証:
```bash
mise exec -- python --version
mise exec -- uv --version
```

# Node.js ランタイム設定（デフォルト）

ユーザーがBun/Pythonを明示しなかった場合のデフォルト。確認不要でそのまま適用する。

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

検証:
```bash
mise exec -- node --version
mise exec -- pnpm --version
```

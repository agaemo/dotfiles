# Node.js ランタイム設定（デフォルト）

ユーザーがBun/Pythonを明示しなかった場合のデフォルト。確認不要でそのまま適用する。

> Node.js は Active LTS が約1年ごとに切り替わるため、この `node` の値を
> そのまま鵜呑みにしない。researcher呼び出し（差分確認モード、必須）で
> 最新のLTSステータスを確認してから採用すること。

```bash
cat > .mise.toml << 'EOF'
[tools]
node = "24"
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

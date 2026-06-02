# Next.js 初期化手順

`craft` ハーネス設置後のディレクトリには `.gitignore` 等が既存のため、
`pnpm create next-app .` は競合エラーになる。カレントディレクトリ内に `tmp` を作ってマージすること。

```
REQUIRE: フレームワークに Next.js を使うことが確定していること
ASSERT:  `mise exec -- node --version` が成功すること
ASSERT:  `mise exec -- pnpm --version` が成功すること
```

```bash
# NG: _tmp は npm naming restrictions（アンダースコア始まり禁止）でエラーになる
# OK: tmp を作成してマージ
mise exec -- pnpm create next-app tmp --typescript --tailwind --app --src-dir=false --import-alias "@/*" --no-git --no-eslint --yes
cp -r tmp/. . && rm -rf tmp
mise exec -- pnpm install

# Oxlint をリンターとして追加（ESLint の代替）
mise exec -- pnpm add -D oxlint
mise exec -- pnpm pkg set scripts.lint="oxlint ."
```

## バージョン管理の注意

`pnpm create next-app` は常に最新版をインストールする。メジャーバージョンが変わると
API・ファイル規約・設定形式が大きく変わる場合がある。
インストール後、`node_modules/next/dist/docs/` の変更点ドキュメントを必ず確認すること。
特定バージョンに固定したい場合: `pnpm create next-app tmp --version X.Y ...`

## Next.js 16 以降の破壊的変更

- `middleware.ts` → `proxy.ts` にリネームが必要
- エクスポート関数名も `middleware` → `proxy` に変更が必要（ファイル名だけでは不十分）

```ts
// proxy.ts（Next.js 16+）
export function proxy(req: NextRequest) { ... }  // ← "proxy" でないとビルドエラー
export const config = { matcher: [...] }
```

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
- **IMPORTANT: リネーム漏れ（`middleware.ts` が残ったまま）はビルドエラーにならず黙って無視される。**
  認証・リダイレクト等の保護ロジックを `middleware.ts` に置いたまま16系へ上げると、
  保護対象ルートが気づかないまま公開状態になる。移行時は `middleware.ts` の実在確認を
  チェックリストに含めること。

```ts
// proxy.ts（Next.js 16+）
export function proxy(req: NextRequest) { ... }  // ← "proxy" でないとビルドエラー
export const config = { matcher: [...] }
```

## セキュリティリリースの追跡

`pnpm create next-app` は常に最新版を取得するため、新規セットアップ時点では自動的に
その時点のセキュリティパッチが適用済みのバージョンが入る。ただし以下の場合は要注意:

- `--version X.Y` でバージョンを明示固定した場合、固定した時点より後のセキュリティ
  リリースを自動では拾わない。固定運用にする場合はパッチ適用状況を継続的に追跡すること
- 既存プロジェクトのアップグレード相談では、直近のセキュリティリリース（Critical CVE等）
  の有無をresearcher呼び出しで確認してから移行先バージョンを決めること

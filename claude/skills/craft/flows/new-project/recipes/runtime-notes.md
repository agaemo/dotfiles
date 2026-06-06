---
name: runtime-notes
description: ランタイムマネージャー選択・pnpm・ネイティブモジュール・型チェックツールの補足事項。new-project Step 3 からトラブル時・非標準構成時に参照する。
---

# ランタイム設定 補足事項

## ランタイムマネージャーの選択

ユーザーが明示していない場合は `mise` をデフォルトとして使用する。

| マネージャー | セットアップ | 実行prefix |
|---|---|---|
| mise（デフォルト） | `mise trust && mise install` | `mise exec --` |
| devbox | `devbox init && devbox shell` | `devbox run` |
| nix-shell | `nix-shell` | `nix-shell --run` |
| 直接インストール済み | なし | （prefixなし） |

以降のコマンド例は mise を前提として記載しているが、
他のマネージャーを使う場合は適宜 `mise exec --` 部分を読み替えること。

**mise の役割:** ランタイム（Node.js, Bun）とパッケージマネージャー（pnpm）のバージョン管理のみ。
アプリのライブラリ（React, Drizzle 等）は `pnpm add` でインストールする。

## パッケージマネージャー

**pnpm を標準として使うこと。**
pnpm はサプライチェーン攻撃への耐性が高く（`--frozen-lockfile` / `onlyBuiltDependencies` 等）、
ディスク効率も良い。インストールは `pnpm install`、追加は `pnpm add` を使うこと。

**ランタイム（Node.js・Bun・Python）のバージョンは必ず固定すること。** `"latest"` はビルド再現性がなく、本番との差異が生じる原因になる。
パッケージマネージャー（pnpm・uv 等）は `"latest"` で構わない。
mise 管理下なので `mise upgrade` で意図的にアップグレードできる。

## Apple Silicon (M1/M2/M3) の注意

ネイティブモジュール（better-sqlite3 等）がアーキテクチャ不一致でクラッシュする場合は、
`pnpm rebuild <パッケージ名>` で再ビルドすること。

## ネイティブモジュール（better-sqlite3・esbuild 等）のビルド許可

pnpm v10 以降は `pnpm approve-builds`（インタラクティブ）が必要だが、CI や自動実行では使えない。
`package.json` に以下を追加することで承認をスキップできる:

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["better-sqlite3", "esbuild"]
  }
}
```

ネイティブモジュールを追加するたびにこのリストに追記すること。
追加後は `pnpm install` を再実行してビルドを通す。

## 型チェックツールの選択

デフォルトは `tsc --noEmit`。ただし 2026年以降は tsgo（`@typescript/native-preview@beta`）が
プロダクションレディとなっており、tsc 比 10倍速い。
ユーザーが速度を重視する場合や Oxc ツールチェーンを使う場合は tsgo を提案すること。

```
インストール: pnpm add -D @typescript/native-preview@beta
スクリプト:   "typecheck": "tsgo --noEmit"
```

tsgo は `node_modules/.bin/` に入るため、mise の `_.path` 設定があればそのまま使用可能。

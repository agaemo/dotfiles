# Vite + React 初期化手順

フロントエンドのみ（SPA）の構成。Vite 8 は内部で Rolldown + Oxc を使用する。

## パッケージインストール

```bash
mise exec -- pnpm add react react-dom
mise exec -- pnpm add -D vite @vitejs/plugin-react @types/react @types/react-dom typescript oxlint oxfmt
```

> **Oxc ツールチェーン全体を試したい場合:** oxlint（リンター）・oxfmt（フォーマッター）を両方入れること。
> oxfmt は Prettier 互換で 30倍速。`pnpm format` スクリプトも追加する（後述）。

> **注意 — 2026年時点:**
> - `@vitejs/plugin-react-oxc` は **deprecated**。代わりに `@vitejs/plugin-react` v6 以降を使うこと。
>   v6 以降は Oxc で JSX 変換するため、Babel 依存がなく高速。
> - rolldown を直接使う場合: `pnpm add -D rolldown`。ただし **rolldown v1.1.0 以降 CSS バンドルは非対応**。
>   CSS は `scripts/copy-html.js` 等で静的コピーするか、Vite を使うこと。

## vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
```

## package.json scripts

```json
{
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "format": "oxfmt src/",
    "lint": "oxlint src/",
    "typecheck": "tsc --noEmit"
  }
}
```

## index.html（プロジェクトルート）

Vite はプロジェクトルートの `index.html` をエントリーポイントとして扱う。
スクリプトタグはソースファイルを直接参照する。

```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## src/vite-env.d.ts（必須）

CSS import や Vite 固有の型を使う場合に必要。

```typescript
/// <reference types="vite/client" />
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true
  },
  "include": ["src"]
}
```

## .oxlintrc.json

```json
{
  "rules": {
    "no-debugger": "error",
    "no-console": "warn"
  }
}
```

## 検証

```bash
mise exec -- pnpm dev      # localhost で起動・HMR 確認
mise exec -- pnpm build    # dist/ に出力確認
mise exec -- pnpm lint     # oxlint 通過
mise exec -- pnpm typecheck # 型エラーなし
```

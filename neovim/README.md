# Neovim

## インストール先

```
~/.config/nvim/init.lua
```

## 導入プラグイン一覧

| プラグイン | 役割 |
|-----------|------|
| [lazy.nvim](https://github.com/folke/lazy.nvim) | プラグインマネージャー |
| [tokyonight.nvim](https://github.com/folke/tokyonight.nvim) | カラースキーム |
| [nvim-tree.lua](https://github.com/nvim-tree/nvim-tree.lua) | ファイルツリー |
| [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter) | シンタックスハイライト・インデント |
| [lualine.nvim](https://github.com/nvim-lualine/lualine.nvim) | ステータスライン |
| [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim) | ファジー検索（ファイル・grep・バッファ） |
| [gitsigns.nvim](https://github.com/lewis6991/gitsigns.nvim) | Git差分表示・blame |
| [conform.nvim](https://github.com/stevearc/conform.nvim) | 保存時自動フォーマット |
| [mason.nvim](https://github.com/williamboman/mason.nvim) | LSPサーバーのインストール管理 |
| [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig) | LSP設定（補完・エラー・定義ジャンプ） |
| [nvim-cmp](https://github.com/hrsh7th/nvim-cmp) | 自動補完UI |
| [LuaSnip](https://github.com/L3MON4D3/LuaSnip) | スニペット |

## LSP（自動インストールされる言語サーバー）

| 言語サーバー | 対象言語 |
|-------------|---------|
| `ts_ls` | TypeScript / JavaScript |
| `pyright` | Python |
| `lua_ls` | Lua |

## フォーマッター（別途インストールが必要）

| ツール | 対象 |
|--------|------|
| `prettier` | JS / TS / JSON / YAML / Markdown |
| `black` | Python |
| `stylua` | Lua |

> インストール例: `npm i -g prettier` / `pip install black` / `cargo install stylua`

---

## キーマップ一覧

`<leader>` は `Space` キー。

### ファイル操作

| キー | 動作 |
|------|------|
| `<Space>e` | ファイルツリーの開閉 |
| `<Space>ff` | ファイル名で検索 |
| `<Space>fg` | プロジェクト内テキストを grep |
| `<Space>fb` | 開いているバッファ一覧 |
| `<Space>fh` | Neovimヘルプを検索 |
| `<Space>fd` | 診断（エラー・警告）一覧 |

### LSP（コード操作）

| キー | 動作 |
|------|------|
| `gd` | 定義へジャンプ |
| `gD` | 宣言へジャンプ |
| `gr` | 参照一覧を表示 |
| `gi` | 実装へジャンプ |
| `K` | ホバー情報を表示 |
| `<Space>rn` | シンボルをリネーム |
| `<Space>ca` | コードアクションを表示 |
| `<Space>f` | ファイルをフォーマット |

### 診断（エラー・警告）

| キー | 動作 |
|------|------|
| `<Space>d` | カーソル位置の診断をポップアップ表示 |
| `]d` | 次の診断へ移動 |
| `[d` | 前の診断へ移動 |

### Git (gitsigns)

| キー | 動作 |
|------|------|
| `]h` | 次の変更箇所（hunk）へ |
| `[h` | 前の変更箇所（hunk）へ |
| `<Space>hs` | hunk をステージ |
| `<Space>hr` | hunk をリセット |
| `<Space>hp` | hunk のプレビュー |
| `<Space>hb` | 現在行の git blame を表示 |

### 補完（nvim-cmp）

| キー | 動作 |
|------|------|
| `Tab` | 次の候補 / スニペットの次へ |
| `Shift+Tab` | 前の候補 / スニペットの前へ |
| `Enter` | 候補を確定 |
| `Ctrl+Space` | 補完を手動で開く |
| `Ctrl+e` | 補完を閉じる |

### ウィンドウ移動

| キー | 動作 |
|------|------|
| `Ctrl+h/j/k/l` | 左/下/上/右のウィンドウへ移動 |

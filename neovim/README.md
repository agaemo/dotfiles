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
| [nvim-autopairs](https://github.com/windwp/nvim-autopairs) | 括弧・クォートの自動補完 |
| [Comment.nvim](https://github.com/numToStr/Comment.nvim) | コメントアウト操作 |
| [which-key.nvim](https://github.com/folke/which-key.nvim) | キーマップのガイド表示 |

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

## モードについて

Neovim には複数のモードがある。画面左下に現在のモードが表示される。

| モード | 左下の表示 | 説明 | 入り方 |
|--------|-----------|------|--------|
| ノーマル | `NORMAL` | 移動・コマンド操作の基本モード | `Esc` |
| インサート | `INSERT` | 文字を入力するモード | `i`（カーソル位置）/ `a`（カーソルの次）/ `o`（次の行） |
| ビジュアル | `VISUAL` | テキストを選択するモード | `v`（文字単位）/ `V`（行単位） |
| コマンド | `:` | `:w` などのコマンドを入力するモード | `:` |

**迷ったらまず `Esc` を押す。** ノーマルモードに戻れる。

---

## ノーマルモード

> `Esc` を押すといつでも戻れる基本のモード。

### キーガイド（which-key）

`Space` を押して **0.5秒待つ** と、使えるキーの一覧がポップアップ表示される。キーを覚えていなくてもここで確認できる。

### カーソル移動

矢印キーでも動くが、以下のキーが基本。

| キー | 動作 |
|------|------|
| `h` | 左 |
| `j` | 下 |
| `k` | 上 |
| `l` | 右 |
| `0` | 行の先頭へ |
| `$` | 行の末尾へ |
| `gg` | ファイルの先頭へ |
| `G` | ファイルの末尾へ |

### 元に戻す・やり直す

| キー | 動作 |
|------|------|
| `u` | 元に戻す（Ctrl+Z 相当） |
| `Ctrl+r` | やり直す（Ctrl+Y 相当） |

### コピー・ペースト

Neovim では「コピー」を **ヤンク（yank）**、「ペースト」を **プット（put）** と呼ぶ。

| キー | 動作 |
|------|------|
| `yy` | 現在行をまるごとコピー |
| `p` | カーソルの後にペースト |
| `P` | カーソルの前にペースト |
| `"+p` | ブラウザ等からコピーしたものをペースト |

### 削除・切り取り

削除したテキストは `p` で貼り付けできる（切り取りとして使える）。

| キー | 動作 |
|------|------|
| `x` | カーソル位置の1文字を削除 |
| `dd` | 現在行を削除（切り取り） |

### ウィンドウ移動

| キー | 動作 |
|------|------|
| `Ctrl+h` | 左のウィンドウへ |
| `Ctrl+j` | 下のウィンドウへ |
| `Ctrl+k` | 上のウィンドウへ |
| `Ctrl+l` | 右のウィンドウへ |

### ファイルツリー・検索

| キー | 動作 |
|------|------|
| `Space + e` | ファイルツリーの開閉（フォーカス移動は `Ctrl+h`） |
| `Space + ff` | ファイル名で検索 |
| `Space + fg` | プロジェクト内テキストを grep |
| `Space + fb` | 開いているバッファ一覧 |
| `Space + fh` | Neovim ヘルプを検索 |
| `Space + fd` | 診断（エラー・警告）一覧 |

### LSP（コード操作）

| キー | 動作 |
|------|------|
| `gd` | 定義へジャンプ |
| `gD` | 宣言へジャンプ |
| `gr` | 参照一覧を表示 |
| `gi` | 実装へジャンプ |
| `K` | ホバー情報を表示 |
| `Space + rn` | シンボルをリネーム |
| `Space + ca` | コードアクションを表示 |
| `Space + f` | ファイルをフォーマット |

### 診断（エラー・警告）

| キー | 動作 |
|------|------|
| `Space + d` | カーソル位置の診断をポップアップ表示 |
| `]d` | 次の診断へ移動 |
| `[d` | 前の診断へ移動 |

### Git（gitsigns）

| キー | 動作 |
|------|------|
| `]h` | 次の変更箇所（hunk）へ |
| `[h` | 前の変更箇所（hunk）へ |
| `Space + hs` | hunk をステージ |
| `Space + hr` | hunk をリセット |
| `Space + hp` | hunk のプレビュー |
| `Space + hb` | 現在行の git blame を表示 |

### コメントアウト（Comment.nvim）

| キー | 動作 |
|------|------|
| `gcc` | 現在行をコメントアウト・解除 |

---

## インサートモード

> `i`（カーソル位置）/ `a`（カーソルの次）/ `o`（次の行）で入る。抜けるときは `Esc`。

### 自動補完（nvim-cmp）

コードを入力中に自動で候補が表示される。

| キー | 動作 |
|------|------|
| `Tab` | 次の候補 / スニペットの次へ |
| `Shift+Tab` | 前の候補 / スニペットの前へ |
| `Enter` | 候補を確定 |
| `Ctrl+Space` | 補完を手動で開く |
| `Ctrl+e` | 補完を閉じる |

### 括弧・クォートの自動補完（nvim-autopairs）

`(` や `"` を打つだけで自動で閉じる。何もしなくていい。

---

## ビジュアルモード

> `v`（文字単位）/ `V`（行単位）で入る。抜けるときは `Esc`。

### 範囲選択してコピー

```
1. v を押してビジュアルモードに入る
2. h/j/k/l または矢印キーで範囲を選択
3. y でコピー完了（ノーマルモードに戻る）
4. 貼り付けたい場所で p
```

| キー | 動作 |
|------|------|
| `y` | 選択範囲をコピー |
| `d` | 選択範囲を削除（切り取り） |
| `"+y` | 選択範囲をシステムクリップボードにコピー（他アプリへ貼り付けたいとき） |
| `gc` | 選択範囲をコメントアウト・解除 |

---

## コマンドモード

> ノーマルモードで `:` を押して入る。`Enter` で実行、`Esc` でキャンセル。

### ファイルの保存・終了

| キー | 動作 |
|------|------|
| `:w` + `Enter` | 保存 |
| `:q` + `Enter` | 終了 |
| `:wq` + `Enter` | 保存して終了 |
| `:q!` + `Enter` | 保存せず強制終了 |

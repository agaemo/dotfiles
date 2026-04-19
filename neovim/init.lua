-- ============================================================
-- 1. lazy.nvim セットアップ
-- ============================================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({ "git", "clone", "--filter=blob:none", "https://github.com/folke/lazy.nvim.git", "--branch=stable", lazypath })
end
vim.opt.rtp:prepend(lazypath)

-- ============================================================
-- 2. 基本設定
-- ============================================================
vim.g.mapleader = " "
vim.g.maplocalleader = " "

vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.termguicolors = true
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.smartindent = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.mouse = 'a'
vim.opt.cursorline = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 250
vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.scrolloff = 8

-- ============================================================
-- 3. プラグイン
-- ============================================================
require("lazy").setup({

  -- カラースキーム
  {
    "folke/tokyonight.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      vim.cmd([[colorscheme tokyonight-night]])
    end,
  },

  -- ファイルツリー
  {
    "nvim-tree/nvim-tree.lua",
    version = "*",
    lazy = false,
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("nvim-tree").setup({
        view = { width = 30 },
        renderer = { group_empty = true },
        filters = { dotfiles = false },
      })
    end,
  },

  -- Treesitter
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    config = function()
      local ts = require("nvim-treesitter")
      ts.setup({ install_dir = vim.fn.stdpath("data") .. "/site" })
      ts.install({ "lua", "typescript", "javascript", "tsx", "python", "json", "yaml", "markdown", "vim", "vimdoc" })
      vim.api.nvim_create_autocmd({ "FileType", "BufEnter" }, {
        callback = function()
          local lang = vim.treesitter.language.get_lang(vim.bo.filetype)
          if lang then pcall(vim.treesitter.start) end
        end,
      })
    end,
  },

  -- ステータスライン
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = {
          theme = "tokyonight",
          component_separators = "|",
          section_separators = "",
        },
        sections = {
          lualine_a = { "mode" },
          lualine_b = { "branch", "diff", "diagnostics" },
          lualine_c = { { "filename", path = 1 } },
          lualine_x = { "encoding", "fileformat", "filetype" },
          lualine_y = { "progress" },
          lualine_z = { "location" },
        },
      })
    end,
  },

  -- ファジー検索
  {
    "nvim-telescope/telescope.nvim",
    tag = "0.1.8",
    dependencies = {
      "nvim-lua/plenary.nvim",
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    },
    config = function()
      local telescope = require("telescope")
      telescope.setup({
        defaults = {
          file_ignore_patterns = { "node_modules", ".git/" },
          layout_strategy = "horizontal",
          sorting_strategy = "ascending",
          layout_config = { prompt_position = "top" },
          preview = { treesitter = false },
        },
      })
      pcall(telescope.load_extension, "fzf")
    end,
  },

  -- Git サイン
  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup({
        signs = {
          add          = { text = "▎" },
          change       = { text = "▎" },
          delete       = { text = "▁" },
          topdelete    = { text = "▔" },
          changedelete = { text = "▎" },
        },
        current_line_blame = true,
        current_line_blame_opts = { delay = 500 },
        on_attach = function(bufnr)
          local gs = package.loaded.gitsigns
          local map = function(mode, l, r, desc)
            vim.keymap.set(mode, l, r, { buffer = bufnr, desc = desc })
          end
          map("n", "]h", gs.next_hunk, "次のhunk")
          map("n", "[h", gs.prev_hunk, "前のhunk")
          map("n", "<leader>hs", gs.stage_hunk, "hunkをステージ")
          map("n", "<leader>hr", gs.reset_hunk, "hunkをリセット")
          map("n", "<leader>hp", gs.preview_hunk, "hunkをプレビュー")
          map("n", "<leader>hb", gs.blame_line, "blameを表示")
        end,
      })
    end,
  },

  -- フォーマッター
  {
    "stevearc/conform.nvim",
    event = { "BufWritePre" },
    config = function()
      require("conform").setup({
        formatters_by_ft = {
          lua        = { "stylua" },
          javascript = { "prettier" },
          typescript = { "prettier" },
          typescriptreact = { "prettier" },
          javascriptreact = { "prettier" },
          json       = { "prettier" },
          yaml       = { "prettier" },
          markdown   = { "prettier" },
          python     = { "black" },
        },
        format_on_save = {
          timeout_ms = 1000,
          lsp_fallback = true,
        },
      })
    end,
  },

  -- LSP サーバー管理
  {
    "williamboman/mason.nvim",
    config = function()
      require("mason").setup()
    end,
  },
  {
    "williamboman/mason-lspconfig.nvim",
    dependencies = { "williamboman/mason.nvim" },
    config = function()
      require("mason-lspconfig").setup({
        ensure_installed = { "ts_ls", "lua_ls", "pyright" },
        automatic_installation = true,
      })
    end,
  },

  -- LSP 設定
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason-lspconfig.nvim",
      "hrsh7th/cmp-nvim-lsp",
    },
    config = function()
      local capabilities = require("cmp_nvim_lsp").default_capabilities()

      local on_attach = function(_, bufnr)
        local map = function(keys, func, desc)
          vim.keymap.set("n", keys, func, { buffer = bufnr, desc = "LSP: " .. desc })
        end
        map("gd", vim.lsp.buf.definition, "定義へ移動")
        map("gD", vim.lsp.buf.declaration, "宣言へ移動")
        map("gr", vim.lsp.buf.references, "参照一覧")
        map("gi", vim.lsp.buf.implementation, "実装へ移動")
        map("K",  vim.lsp.buf.hover, "ホバー情報")
        map("<leader>rn", vim.lsp.buf.rename, "リネーム")
        map("<leader>ca", vim.lsp.buf.code_action, "コードアクション")
        map("<leader>f",  function() vim.lsp.buf.format({ async = true }) end, "フォーマット")
      end

      vim.lsp.config("ts_ls",  { capabilities = capabilities, on_attach = on_attach })
      vim.lsp.config("pyright", { capabilities = capabilities, on_attach = on_attach })
      vim.lsp.config("lua_ls", {
        capabilities = capabilities,
        on_attach = on_attach,
        settings = {
          Lua = {
            diagnostics = { globals = { "vim" } },
            workspace = { checkThirdParty = false },
          },
        },
      })
      vim.lsp.enable({ "ts_ls", "pyright", "lua_ls" })
    end,
  },

  -- 自動補完
  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
      "L3MON4D3/LuaSnip",
      "saadparwaiz1/cmp_luasnip",
      "rafamadriz/friendly-snippets",
    },
    config = function()
      local cmp = require("cmp")
      local luasnip = require("luasnip")
      require("luasnip.loaders.from_vscode").lazy_load()

      cmp.setup({
        snippet = {
          expand = function(args) luasnip.lsp_expand(args.body) end,
        },
        mapping = cmp.mapping.preset.insert({
          ["<C-b>"]     = cmp.mapping.scroll_docs(-4),
          ["<C-f>"]     = cmp.mapping.scroll_docs(4),
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<C-e>"]     = cmp.mapping.abort(),
          ["<CR>"]      = cmp.mapping.confirm({ select = true }),
          ["<Tab>"]     = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then luasnip.expand_or_jump()
            else fallback() end
          end, { "i", "s" }),
          ["<S-Tab>"]   = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_prev_item()
            elseif luasnip.jumpable(-1) then luasnip.jump(-1)
            else fallback() end
          end, { "i", "s" }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "luasnip" },
        }, {
          { name = "buffer" },
          { name = "path" },
        }),
        formatting = {
          format = function(entry, item)
            local source_names = {
              nvim_lsp = "[LSP]",
              luasnip  = "[Snip]",
              buffer   = "[Buf]",
              path     = "[Path]",
            }
            item.menu = source_names[entry.source.name] or ""
            return item
          end,
        },
      })
    end,
  },

}, {
  ui = { border = "rounded" },
})

-- ============================================================
-- 4. 診断設定
-- ============================================================
vim.diagnostic.config({
  virtual_text = { prefix = "●" },
  signs = true,
  underline = true,
  severity_sort = true,
  float = { border = "rounded" },
})

vim.api.nvim_set_hl(0, "DiagnosticError", { fg = "#ff4444", bg = "NONE" })
vim.api.nvim_set_hl(0, "DiagnosticWarn",  { fg = "#ffaa00", bg = "NONE" })

local signs = { Error = "󰅚 ", Warn = "󰀪 ", Hint = "󰌶 ", Info = "󰋽 " }
for type, icon in pairs(signs) do
  local hl = "Diagnostic" .. type
  vim.fn.sign_define(hl, { text = icon, texthl = hl, numhl = hl })
end

-- ============================================================
-- 5. キーマップ
-- ============================================================
local map = vim.keymap.set

-- ファイルツリー
map("n", "<leader>e", "<cmd>NvimTreeToggle<CR>", { desc = "ファイルツリー開閉" })

-- Telescope
local tb = require("telescope.builtin")
map("n", "<leader>ff", tb.find_files,  { desc = "ファイル検索" })
map("n", "<leader>fg", tb.live_grep,   { desc = "文字列 grep" })
map("n", "<leader>fb", tb.buffers,     { desc = "バッファ一覧" })
map("n", "<leader>fh", tb.help_tags,   { desc = "ヘルプ検索" })
map("n", "<leader>fd", tb.diagnostics, { desc = "診断一覧" })

-- 診断
map("n", "<leader>d",  vim.diagnostic.open_float, { desc = "診断をフロートで表示" })
map("n", "]d",         vim.diagnostic.goto_next,  { desc = "次の診断" })
map("n", "[d",         vim.diagnostic.goto_prev,  { desc = "前の診断" })

-- ウィンドウ移動
map("n", "<C-h>", "<C-w>h", { desc = "左へ" })
map("n", "<C-j>", "<C-w>j", { desc = "下へ" })
map("n", "<C-k>", "<C-w>k", { desc = "上へ" })
map("n", "<C-l>", "<C-w>l", { desc = "右へ" })

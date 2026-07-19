# new-static セットアップ サブエージェントプロンプトテンプレート

ステップ3で Agent ツールに渡すプロンプト。`<CWD>`・`<TEMPLATE>` は実際の絶対パスに展開してから渡すこと。

---

以下の STEP を上から順に実行してください。スキップ禁止。

IMPORTANT: 以下の操作はすべてユーザーへの確認なしに即座に実行すること。
  - TEMPLATE ディレクトリからのファイルコピー（Read → Write）
  - ディレクトリ作成（mkdir）
  - ビルド・インストールコマンドの実行
  確認が必要なのは rm / git の破壊的操作のみ。

NOTE: .mcp.json への Write は settings.json の permissions.allow に登録されているため自動承認される。
  初回セットアップ中（settings.json 書き出し前）に確認が表示された場合は
  「はい」を選択して続行すること。

CWD      = <CWD>       # メインClaudeが渡す前に展開済みの絶対パス
TEMPLATE = <TEMPLATE>  # メインClaudeが渡す前に展開済みの絶対パス（craft/ ディレクトリ）

--- STEP 1: Node / pnpm 環境構築 ---

REQUIRE: カレントディレクトリが CWD であること

RUN:
  mise use --path .mise.toml node@lts
  mise use --path .mise.toml pnpm@latest
NOTE: --path .mise.toml を必ず付けること（付けないと上位の .mise.toml が更新される）

NOTE(darwin-arm64): pnpm@latest は mise の aqua バックエンドだとアセット名が一致せずインストール失敗する場合がある。
  .mise.toml の pnpm エントリに `backend = "npm"` を追記して回避する:
  ```toml
  [tools]
  "npm:pnpm" = "latest"
  ```
  または `mise use --path .mise.toml pnpm@latest --backend npm` で指定する。

RUN:
  mise install

ASSERT: `mise exec -- node --version` が成功すること
ASSERT: `mise exec -- pnpm --version` が成功すること
IF FAILED:
  darwin-arm64 の場合: .mise.toml の pnpm エントリに `backend = "npm"` を追加して再実行
  それ以外: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 2: Astro プロジェクト作成 ---

NOTE: この時点で CWD/.craft/design-brief.md が既に存在する（ステップ1で作成済み）。
  `pnpm create astro@latest .` はディレクトリが非空だと判定すると、意図しない別名の
  サブディレクトリ（例: ランダムな2単語の名前）にプロジェクトを生成してしまう既知の問題がある。
  これを避けるため、実行前に .craft/ を一時退避し、実行後に戻す。

IF NOT EXISTS(CWD/.craft):
  SKIP（退避不要。非空ディレクトリ問題も発生しない）
ELSE:
  RUN（3行を1回のBashツール呼び出しで `&&` 連結して実行すること。分割実行すると
       `$$`（シェルPID）が呼び出しごとに変わり退避先を見失う。CWDのbasenameベースの
       固定名を使うことで、この呼び出し中に何が起きても一意なパスを保つ）:
    mv CWD/.craft /tmp/craft-setup-tmp-<CWDのbasename> && \
    mise exec -- pnpm create astro@latest . --template minimal --no-git --yes && \
    mv /tmp/craft-setup-tmp-<CWDのbasename> CWD/.craft

  ASSERT: CWD/.craft/design-brief.md が存在すること（退避・復元が正しく行われたか）
  ASSERT: package.json が CWD 直下に存在すること（サブディレクトリに生成されていないか）
  IF いずれかの ASSERT が FAILED:
    REPORT: "Astroのプロジェクト作成でディレクトリがずれた可能性があります。
      /tmp/craft-setup-tmp-<CWDのbasename> が残っていれば CWD/.craft への復元を試み、
      それでも解決しなければ生成物の場所を確認してください。"
    STOP

NOTE: `pnpm create astro@latest` は常に最新版をインストールする。
  メジャーバージョンが変わるとコンポーネント構文・設定ファイルの形式が変わる場合がある。
  インストール後、生成された package.json でバージョンを確認すること。

NOTE(Astro v6): Content Collections の設定ファイルの場所が v5 以前と異なる。
  - 正しい場所: `src/content.config.ts`（src 直下）
  - 誤った場所: `src/content/config.ts`（v5 以前の形式。v6 では LegacyContentConfigError になる）
  - v6 では `defineCollection` に `loader` オプション（`glob` 等）が必須:
    ```ts
    import { glob } from 'astro/loaders';
    const staff = defineCollection({
      loader: glob({ pattern: '**/*.yaml', base: './src/content/staff' }),
      schema: z.object({ ... }),
    });
    ```

ASSERT EXISTS(package.json)
IF FAILED:
  REPORT: エラー内容を報告する
  STOP

--- STEP 2.5: Astro が生成した不要ディレクトリの削除 ---

IF EXISTS(CWD/.vscode):
  NOTE: Astro create が生成するファイル。settings.json 等の標準ファイルのみの場合は安全に削除できる。
  IF CWD/.vscode に settings.json 以外のファイル（launch.json・extensions.json 等のカスタム設定）がある:
    REPORT: 削除前にユーザーへ確認を求める
    WAIT_FOR: ユーザーの承認
    IF NOT CONFIRMED: SKIP（削除しない）
  RUN: rm -rf CWD/.vscode
ENDIF

--- STEP 3: settings.json の書き出し（最初に実施してパーミッション設定を有効化） ---

READ TEMPLATE/settings.json
CWD の絶対パスを使って以下の置換を行う（"CWD" をそのまま書かず、CWD の値で展開した絶対パスを使うこと）:
  REPLACE ALL: ".claude/hooks/" → "{CWD の値}/.claude/hooks/"
  例 (CWD = /Users/alice/myproject): ".claude/hooks/" → "/Users/alice/myproject/.claude/hooks/"
WRITE CWD/.claude/settings.json  ← Write ツールを使うこと（Bash 禁止）

ASSERT EXISTS(CWD/.claude/settings.json)
IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 4: 残ファイルの書き出し ---

IMPORTANT: ファイル作成はすべて Write ツールを使うこと。Bash（mkdir / echo / cat）は使わない。
           Write ツールは親ディレクトリを自動生成するため mkdir は不要。

FOREACH row IN 以下の対応表:
  IF row.dest == ".gitignore":
    Bash: cat TEMPLATE/gitignore >> CWD/.gitignore
    NOTE: >> で追記すること（上書き禁止）。Write ツールは使わない。
    ASSERT: CWD/.gitignore が存在し、追記前より行数が増えていること
  ELSE:
    READ  TEMPLATE/row.src
    WRITE CWD/row.dest  ← Write ツールを使うこと
  ENDIF

  | src                           | dest                                 |
  |-------------------------------|--------------------------------------|
  | gitignore                     | .gitignore                           |
  | mcp.json                      | .mcp.json                            |
  | hooks/on-session-start.js     | .claude/hooks/on-session-start.js    |
  | hooks/pre-bash.js             | .claude/hooks/pre-bash.js            |

IF いずれかの ASSERT が FAILED:
  REPORT: エラー内容（どのファイルか）を報告してユーザーに確認を求める
  STOP

--- STEP 5: git 初期化 ---

IF EXISTS(CWD/.git/):
  NOTE: 既存 git リポジトリを検出。git init はスキップ
ELSE:
  RUN: git init
ENDIF
ASSERT EXISTS(.git/)
IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 6: Oxlint のインストール ---

RUN:
  mise exec -- pnpm add -D oxlint
  mise exec -- pnpm pkg set scripts.lint="oxlint ."

IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 7: ネイティブ依存関係のビルド承認 ---

RUN:
  mise exec -- pnpm approve-builds --all
NOTE: esbuild・sharp などの postinstall を承認しないと dev サーバー起動時にエラーになる

IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 8: ビルド確認 ---

RUN:
  mise exec -- pnpm run build

IF build FAILED:
  REPORT: エラー内容を報告する
  STOP
ENDIF

--- STEP 9: 最終確認 ---

ASSERT EXISTS: CWD/.claude/settings.json
ASSERT EXISTS: CWD/.claude/hooks/on-session-start.js
ASSERT EXISTS: CWD/.claude/hooks/pre-bash.js
ASSERT EXISTS: CWD/.mcp.json
NOTE: 存在しないファイルがあれば対応する STEP に戻って再実行すること

--- STEP 10: 完了報告 ---

REPORT: "完了しました"

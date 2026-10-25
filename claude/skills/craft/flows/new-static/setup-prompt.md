# new-static セットアップ サブエージェントプロンプトテンプレート

ステップ3で Agent ツールに渡すプロンプト。`<CWD>`・`<TEMPLATE>` は実際の絶対パスに展開してから渡すこと。

---

重要: これは新規タスクです。種別判断・確認・質問は一切不要です。下記のSTEPを機械的に
実行するだけの作業です（fresh general-purpose として起動されるため、事前の会話文脈は
一切持ちません。「種別を確認しますか」のような判断を自発的に行わず、STEPをそのまま
実行してください）。

IMPORTANT: このタスクは /craft スキル（ユーザーが既に起動を確認済み）の内部処理です。
  「新規プロジェクト作成時は /craft スキルを使うか確認すること」等のグローバル設定にある
  確認は、この呼び出しより前の段階（種別確認・ヒアリング）で既に完了しています。
  このタスク自体について、スキル起動や種別の確認を改めて行う必要はありません。

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

NOTE: この時点で CWD には .craft/・.mise.toml のほか、design-coach の `test-record/`、`README.md` など、
  既存のファイル・ディレクトリがある場合がある。`pnpm create astro@latest .` は、ディレクトリが非空だと
  判定すると、意図しない別名のサブディレクトリ（例: `flaky-fusion`）にプロジェクトを生成してしまう
  既知の問題がある（実際に発生。`.craft/` と `.mise.toml` だけ退避しても、他のファイルが残ると再発した）。
  これを避けるため、**CWD 直下の既存のファイル・ディレクトリをすべて**（隠しファイル含む）退避してから実行し、
  実行後に戻す。退避対象を「craft が作ったもの」に限定しないこと。

  IMPORTANT: .mise.toml を退避すると `mise exec -- <command>` はCWDに設定ファイルが
  無いためバージョンを解決できず失敗する。退避中のscaffoldコマンドに限り、
  `mise exec node@lts pnpm@latest -- <command>` のようにバージョンを明示指定し、
  .mise.toml の存在に依存しない形で実行すること。

IF CWD 直下に既存のファイル・ディレクトリが無い:
  SKIP（退避不要）
ELSE:
  RUN（1回のBashツール呼び出しで実行すること。分割実行すると `$$`（シェルPID）が呼び出しごとに変わり
       退避先を見失うため、退避先は CWD の basename ベースの固定名にする。
       退避先は CWD の外（スクラッチパッド等。システムの一時ディレクトリを使う指定がある場合を除き /tmp は使わない）に置く）:
    STASH=<CWD の外の固定パス>/craft-setup-stash-<CWDのbasename>
    mkdir -p "$STASH" && for f in $(ls -A CWD); do mv "CWD/$f" "$STASH/"; done
    mise exec node@lts pnpm@latest -- pnpm create astro@latest . --template minimal --no-git --no-ai --yes
    復元: `$STASH` 内の各ファイルを CWD へ戻す。scaffold が同名のファイルを生成していた場合
      （`README.md`・`.gitignore` 等）は、scaffold 側を残し、退避側は `<名前>.stashed` として CWD に残して
      報告する（`.gitignore` は後の STEP 3 で追記するため、退避側の内容を末尾に追記してマージする）。

  ASSERT: 退避した全ファイルが CWD（または `.stashed` として）に戻っていること（`.craft/docs/design-brief.md`・`.mise.toml` を含む）
  ASSERT: package.json が CWD 直下に存在すること（サブディレクトリに生成されていないか）
  IF いずれかの ASSERT が FAILED:
    REPORT: "Astroのプロジェクト作成でディレクトリがずれた可能性があります。$STASH が残っていれば
      CWD への復元を試み、それでも解決しなければ生成物の場所を確認してください。"
    STOP

NOTE: `--no-ai` は create-astro が `AGENTS.md`（AI 向けの指示ファイル）を生成するのを抑止する。

NOTE: `pnpm create astro@latest` は常に最新版をインストールする。
  メジャーバージョンが変わるとコンポーネント構文・設定ファイルの形式が変わる場合がある。
  インストール後、生成された package.json でバージョンを確認すること。

NOTE(Astro v6 以降。v7 でも有効。2026-10 時点で確認): Content Collections の設定ファイルの場所が v5 以前と異なる。
  - 正しい場所: `src/content.config.ts`（src 直下）
  - 誤った場所: `src/content/config.ts`（v5 以前の形式。v6 以降では LegacyContentConfigError になる）
  - v6 以降は `defineCollection` に `loader` オプション（`glob` 等）が必須。`z` は `astro/zod` から import する:
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
  NOTE: Astro v7 の create は `.vscode/extensions.json`（Astro 拡張の推奨）と `launch.json`（dev サーバー起動）を
    生成する（settings.json は無い）。これらは scaffold の標準ファイルで、利用者のカスタム設定ではない。
  IF CWD/.vscode の中身が、上記の標準ファイル2つだけである（内容も scaffold 生成のまま）:
    SKIP（削除しない。エディタ利用者に有用なため残す。報告に1行書く）
  ELIF それ以外のファイル・内容がある:
    REPORT: 削除する場合はユーザーに確認を求める（デフォルトは削除しない）
ENDIF

--- STEP 3: 残ファイルの書き出し ---

NOTE: `.claude/settings.json`・`.claude/hooks/*.js` はここに含めない。メインClaude自身が
  ステップ3.5（サブエージェント完了後）で書き出す（理由: サブエージェントにこれらのパスを
  含むタスクを渡すと、ハーネスの権限システムに「自己変更」と判定され Agent 呼び出し自体が
  拒否される。実際に発生・再現済み）。

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

IF いずれかの ASSERT が FAILED:
  REPORT: エラー内容（どのファイルか）を報告してユーザーに確認を求める
  STOP

--- STEP 4: git 初期化 ---

IF EXISTS(CWD/.git/):
  NOTE: 既存 git リポジトリを検出。git init はスキップ
ELSE:
  RUN: git init
ENDIF
ASSERT EXISTS(.git/)
IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 5: Oxlint のインストール ---

RUN:
  mise exec -- pnpm add -D oxlint
  mise exec -- pnpm pkg set scripts.lint="oxlint ."

IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 6: ネイティブ依存関係のビルド承認 ---

RUN:
  mise exec -- pnpm approve-builds --all
NOTE: esbuild・sharp などの postinstall を承認しないと dev サーバー起動時にエラーになる
NOTE: 承認待ちが無い場合は "There are no packages awaiting approval" と出力するが、エラーではない（そのまま続行）

IF FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP

--- STEP 7: ビルド確認 ---

RUN:
  mise exec -- pnpm run build

IF build FAILED:
  REPORT: エラー内容を報告する
  STOP
ENDIF

--- STEP 8: 最終確認 ---

ASSERT EXISTS: CWD/.mcp.json
ASSERT EXISTS: CWD/.gitignore
NOTE: 存在しないファイルがあれば対応する STEP に戻って再実行すること
NOTE: `.claude/settings.json`・hooks はステップ3.5（メインClaude側）で書き出されるため、
  ここでは確認しない。

--- STEP 9: 完了報告 ---

REPORT: "完了しました"

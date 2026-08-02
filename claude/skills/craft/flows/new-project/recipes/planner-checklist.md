# planner へ渡すべき設計判断の確認事項

planner を呼び出す前に、以下の判断をユーザーに確認すること。これらは後から変更するとコストが大きい。

## フロントエンドがある場合

- ログイン窓口は統一するか分けるか
  - 統一（`/login` → ロールに応じてリダイレクト）← 推奨
  - 分離（`/admin/login` と `/customer/login` を別々に）
- 管理者と顧客でドメインを分けるか（`admin.example.com` / `example.com`）

## バックエンドがある場合

- 公開エンドポイント（認証不要）と保護エンドポイント（認証必要）の境界線
  - 特に「ログイン前の顧客がアクセスできる情報」を明確にする

## 主要ライブラリの選定方針（DB・認証・ORM等を伴う場合）

plan.md 本文を書く前に、後から変更すると計画全体の再生成が必要になる以下のカテゴリだけを
先に候補提示してユーザー確認を済ませること（plan.md執筆後の個別確認だと手戻りが大きい）:

- DB ドライバ / ORM（例: better-sqlite3 + Drizzle / Prisma / 生SQL）
- 認証ライブラリ・認証方式（例: 自前JWT実装 / Auth.js / 他のIdP連携）
- UIコンポーネントライブラリ（採用する場合）

確認手順:
1. 各カテゴリについて推奨案 + 代替案を1〜2行の理由付きで提示する（plan.md執筆前の軽量な提示でよい）
   IMPORTANT: 既知のリスク（ネイティブモジュールのビルド問題等）があれば、この時点で併記する
   （詳細は agents/planner.md の「ライブラリ・フレームワーク選定ルール」参照）
2. ユーザーが推奨と異なる選択をした場合、その選択を前提にしてから planner を呼び出す
   （= plan.md は最初から確定済みの技術選定で1回で書く。書き直しを前提にしない）

## 認証機能を含む場合の Makefile 追加ターゲット

plan.md の「開発コマンド」表に以下を追加すること。

| ターゲット | 内容 | 実行コマンド（例） |
|-----------|------|-----------------|
| `make seed` | テストユーザーを1件作成し、ユーザー名とパスワードを標準出力へ表示する | 言語・スタックに応じた実装コマンド（例: `docker compose run --rm app go run ./cmd/seed/`、`mise exec -- pnpm tsx scripts/seed.ts` 等） |

seed コマンドの要件:
- テストユーザーのユーザー名・パスワードは固定値でよい（例: `test` / `test1234`）
- 既に同ユーザーが存在する場合はエラーではなく警告を出し、ユーザー名・パスワードを表示して終了する（冪等性）
- サーバーが起動していなくても実行できること（DB への直接接続 or seed API 等）

NOTE: seed ターゲットは build フローの「完了報告」ステップで自動実行される。
  ユーザーが「確認してください」と言われた時点でログインできるアカウントを持っていることを保証するために必要。

## 開発ランタイムの選定方針（必須）

IMPORTANT: plan.md の「開発ランタイム」節に書く内容を、plan.md 本文を書く前に確定させること。
この節がbuildフローが実際に環境構築（ランタイムのインストール・フレームワークのscaffold等）を行う唯一の情報源になるため、
空欄や曖昧な記載は許されない。

1. **環境管理ツールの決定**
   - 既存リポジトリに `devbox.json` / `shell.nix` / `docker-compose.yml` がある場合はそれに従う
     （新規プロジェクトでは通常該当しない。既存システムへの機能追加時に該当する）
   - ユーザーがDockerでの完結を希望する場合はそれに従う
   - 上記いずれもない場合は `mise` をデフォルトとする（バージョン固定によるグローバル環境汚染防止のため）

2. **言語・ランタイムのバージョン決定**
   - 既知の組み合わせ（Bun / Python(uv) / Node.js / Flutter / React Native）は
     `{SKILL_DIR}/flows/new-project/recipes/runtime-*.md`（Node.js系）・
     `{SKILL_DIR}/flows/new-app/flutter-notes.md`（Flutter）の該当テンプレートに従う
   - それ以外の言語（Go・Rust・Java 等）は以下の手順で決定する:
     1. 選定したマネージャーのレジストリで対応バージョンを確認する
        （例: `mise registry | grep -i <言語>` または公式ドキュメント）
     2. ランタイムは固定バージョンを指定する（`"latest"` はビルド再現性がなく禁止。
        パッケージマネージャーは `"latest"` で構わない）
     3. インストール・検証コマンドを確定する（例: `mise exec -- go version`）

3. **フレームワーク・アプリのscaffold決定**（HAS_FRONTEND == true の場合。new-app 由来の Flutter・React Native も含む）

   | フレームワーク | scaffold手順 |
   |---|---|
   | Next.js | `{SKILL_DIR}/flows/new-project/recipes/nextjs-init.md` を読み、scaffoldコマンドを確認する |
   | Vite + React | `{SKILL_DIR}/flows/new-project/recipes/vite-react.md` を読み、scaffoldコマンドを確認する |
   | Hono / Express | 専用recipeが無いため、公式ドキュメントの最小scaffold手順（`pnpm create hono@latest` / `pnpm init` + `pnpm add express` 等）を確認し、セットアップコマンドとして明記する。頻出するようなら recipes/ 配下に専用recipeを追加することを検討する |
   | Flutter | `{SKILL_DIR}/flows/new-app/flutter-notes.md` を読み、`flutter create` コマンド・バージョン固定の注意点（`stable` 指定は404になる）を確認する |
   | React Native (Expo・既定) | `.mise.toml`（`node = "22"`, `pnpm = "latest"`）作成後、`pnpm create expo-app . --template blank-typescript && pnpm install` |
   | React Native (CLI) | ユーザーがCLI構成を明示的に希望した場合のみ選ぶ。同じ `.mise.toml` 作成後、`pnpm dlx @react-native-community/cli init <アプリ名> --directory . && pnpm install` |

   Webアプリの場合、会話の文脈から Next.js / Vite + React / Hono / Express 等を推定する。判断できない場合はユーザーに確認する。
   リアルタイム通信（WebSocket・チャット・通知）が要件にある場合は
   `{SKILL_DIR}/flows/new-project/recipes/socketio.md` を読み、実装ステップに組み込む

4. **plan.md への転記**
   - 1・2で確定した内容 → 「開発ランタイム」節の「環境管理ツール」「セットアップコマンド」「検証コマンド」
   - 3で確認したscaffoldコマンド → 同じく「開発ランタイム」節の「セットアップコマンド」に追記する
     （ランタイムのインストールとフレームワークのscaffoldは、buildフローが同じタイミングで
     一度に実行する一続きの初期化コマンド列として記載すること）
   - STACK識別子（英小文字・言語名のみ。例: node / flutter / rust / go。「Node.js」等の表記は不可）も明記する。
     既存の特別扱い値（static・flutter・node）と衝突しないよう注意する

> **設計判断の記録:** 確認した内容は `.craft/plan.md` の「設計判断」セクションに記録すること。

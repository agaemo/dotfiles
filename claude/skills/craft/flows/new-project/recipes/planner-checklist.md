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
- **実行環境構成（Docker利用時）**: Dockerベースイメージ（例: `node:24-slim` / `postgres:18-alpine`
  等の具体的なタグ）、コンテナ構成（サービス数・各サービスの役割・ボリューム・ネットワーク）。
  ベースイメージのメジャーバージョンはDBイメージのデータディレクトリ形式・OS依存パッケージの
  有無等、後から変えるとコストが高い決定を伴うため、他のライブラリ選定と同様に候補提示して
  確認する。承認ゲートが1つ増えることを理由に省略しない
  IMPORTANT: DBを使う自動テスト（統合テスト等）がある場合、開発用DBとテスト用DBを分離するか
  確認する。同一DBを共有すると、テストのセットアップ/クリーンアップ処理が手動で投入した
  開発用データを誤って削除する事故につながる。分離方法は、同一Postgresサービス内で
  データベース名を分ける（例: `app_dev` / `app_test`）簡易な方法で足りることが多い
  （サービス自体を分ける必要は通常ない）

確認手順:
1. 各カテゴリについて推奨案 + 代替案を1〜2行の理由付きで提示する（plan.md執筆前の軽量な提示でよい）
   IMPORTANT: 既知のリスク（ネイティブモジュールのビルド問題等）があれば、この時点で併記する
   （詳細は agents/planner.md の「ライブラリ・フレームワーク選定ルール」参照）
2. ユーザーが推奨と異なる選択をした場合、その選択を前提にしてから planner を呼び出す
   （= plan.md は最初から確定済みの技術選定で1回で書く。書き直しを前提にしない）
3. 実行環境構成（Docker利用時）は、確定後に `.craft/docs/plan.md` の「開発ランタイム」節へ
   コンテナ構成図（mermaid。サービス間の関係・ポート・ボリュームを図示）として記録すること
   （下記「開発ランタイムの選定方針」のplan.mdへの転記手順を参照）

## 認証機能を含む場合の必須実装ファイル

認証ライブラリ（Auth.js等）は、設定ファイル（`auth.ts`等）だけでなく、フレームワークが
要求するエントリーポイント（APIルートハンドラ・ミドルウェア登録・型定義拡張等）を
別途必要とすることが多い。実装ステップに設定ファイルのみを書き、エントリーポイントの
作成を書き漏らすと、実際にログインを試すまで気づけない
（実例: Next.js + Auth.jsで`auth.ts`のみを実装ステップに含め、
`app/api/auth/[...nextauth]/route.ts`の作成を書き漏らした）。

IMPORTANT: 認証ライブラリを採用する際は、公式ドキュメントの「セットアップ手順」を
最初から最後まで確認し、設定ファイル以外に必要な副次ファイルをすべて実装ステップに
明記すること。「認証基盤」のようなステップ名だけで済ませず、作成するファイルパスを
列挙する。

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
   - ユーザーがDockerでの完結を希望する場合はそれに従う。
     IMPORTANT: 「Dockerで完結」が指示された場合、開発時の型補完・CLI実行の利便性を理由に
     ホストへ言語ランタイムを併設する妥協案（mise併用等）を確認なしで提案しないこと。
     全コマンド（scaffold・パッケージ追加・DB操作等）をコンテナ経由（`docker compose run`/
     `exec`）で実行する構成を既定とし、ホスト側にも置きたい場合はユーザーから明示的に
     求められたときのみ検討する
   - IMPORTANT: ユーザーが「環境を汚さない」等の分離要件を述べているが、具体的な
     ツール（mise/Docker/devbox等）を明示していない場合は、確認せずmiseへ倒さない。
     ASK USER: 環境分離の方法を確認する
       例:「mise（プロジェクト単位で言語バージョンを切り替える軽量な方式）」と
          「Docker（コンテナで完全に分離する方式。Docker/Rancher Desktop等が必要）」の
          どちらを希望するか
     WAIT_FOR: ユーザーの回答
   - IMPORTANT: 上記いずれにも該当しない場合のみ `mise` をデフォルトとする。個別の言語専用バージョンマネージャー
     （rustup単体・pyenv単体・nvm単体等）を先に提案しないこと — miseの`core`バックエンドが
     大半の言語をカバーし、内部でその言語の標準ツール（rustup等）を使って導入する。
     「miseで対応できるか」を必ず最初に確認してから、対応できない場合のみ個別ツールを検討する

2. **技術調査（researcher呼び出し、必須）**

   IMPORTANT: バージョン・scaffold手順は時間とともに変わる。recipeやIMPORTANTの一般原則
   （公式ドキュメント確認等）だけに頼らず、確定させる直前に必ず `researcher` エージェント
   （`{SKILL_DIR}/agents/researcher.md`）を呼び出して現状を調べさせること。

   - 対象: 言語・ランタイム、（HAS_FRONTEND == true の場合）採用予定フレームワーク、
     **および一緒に使う主要な周辺ツール（DBエンジンのDockerイメージ・ORM・パッケージ
     マネージャーの主要バージョン等、後述「主要ライブラリの選定方針」で候補提示する対象）。**
     IMPORTANT: フレームワーク本体だけを調べて満足しないこと。フレームワークと組み合わせて
     使うORM・DBイメージ・ビルドツールは、それぞれ独立にメジャーバージョンの仕様変更
     （設定ファイル形式・出力先・配布方法等）を起こしうる。実際に「Next.js/Node.jsは
     差分確認済みだが、一緒に使うPrisma・PostgreSQLイメージ・pnpmの仕様変更が未調査だった」
     という事例が発生している。対象を1つに絞らず、技術スタック表に載る主要コンポーネント
     全てを対象にする
   - モードの判定:
     - 専用recipeがある技術（Bun / Python(uv) / Node.js / Flutter / React Native、
       および下記ステップ3の表にあるフレームワーク）→ **差分確認モード**。該当recipe
       ファイルの内容を読み、researcherへの指示に含めて渡す
     - それ以外（Go・Rust・Java 等の言語、表に無いフレームワーク、DBイメージ・ORM等の
       周辺ツール）→ **フル調査モード**
   - Agent ツールでresearcherを起動し、完了報告（`.craft/docs/tech-research.md` への保存）
     を受け取ってから次に進む
   - IF READ FAILED（researcher.mdが見つからない）:
     NOTE: 読めない場合でも省略せず、WebSearch/WebFetchで同等の調査（quickstart・
     破壊的変更・既知の罠・メンテナンス状況）をこの場で行うこと
   - IMPORTANT: researcherは「懸念なし」であっても客観的な差分（バージョンステータスの
     変化・新たなセキュリティリリース・破壊的変更・新たな既知の罠等）を報告に含めてくる。
     「懸念」という評価語の有無で判断せず、recipe記載時点からの差分そのものがあるかどうかで
     判断すること（フル調査モードでは常に該当ありとして扱う）。
   - 差分がある場合、その内容をそのままユーザーに提示してから次のステップへ進む
     （代替への変更を提案するかはユーザー次第。提示せず進めることを禁止する）
     WAIT_FOR: ユーザーの回答（差分がある場合のみ。recipe内容と完全に一致し差分皆無の場合は提示不要）

3. **言語・ランタイムのバージョン決定**
   - `.craft/docs/tech-research.md`（ステップ2で得た調査結果）の推奨構成を踏まえて確定する
   - 既知の組み合わせ（Bun / Python(uv) / Node.js / Flutter / React Native）は
     `{SKILL_DIR}/flows/new-project/recipes/runtime-*.md`（Node.js系）・
     `{SKILL_DIR}/flows/new-app/flutter-notes.md`（Flutter）の該当テンプレートをベースに、
     tech-research.md の差分確認結果（変更点があれば）を反映する
   - それ以外の言語（Go・Rust・Java 等）は以下の手順で決定する:
     1. tech-research.md の推奨バージョンを起点に、選定したマネージャーのレジストリで
        対応可否を確認する（例: `mise registry | grep -i <言語>`）
     2. ランタイムは固定バージョンを指定する（`"latest"` はビルド再現性がなく禁止。
        パッケージマネージャーは `"latest"` で構わない）
     3. インストール・検証コマンドを確定する（例: `mise exec -- go version`）

4. **フレームワーク・アプリのscaffold決定**（何らかのアプリケーションフレームワークを採用する場合に実施する。
   フロントエンドフレームワーク（HAS_FRONTEND == true）に限らない — UIなしのバックエンドAPI専用
   プロジェクトでもExpress・Fastify・Hono等のフレームワーク選定は後から変更コストが高いため対象に含める。
   new-app 由来の Flutter・React Native も含む）

   `.craft/docs/tech-research.md` に記載のscaffold手順・破壊的変更を優先し、下表の記載と食い違う場合は
   tech-research.md（＝現時点の調査結果）を採用する。

   | フレームワーク | scaffold手順 |
   |---|---|
   | Next.js | `{SKILL_DIR}/flows/new-project/recipes/nextjs-init.md` を読み、scaffoldコマンドを確認する |
   | Vite + React | `{SKILL_DIR}/flows/new-project/recipes/vite-react.md` を読み、scaffoldコマンドを確認する |
   | Hono / Express | 専用recipeが無いため、公式ドキュメントの最小scaffold手順（`pnpm create hono@latest` / `pnpm init` + `pnpm add express` 等）を確認し、セットアップコマンドとして明記する。頻出するようなら recipes/ 配下に専用recipeを追加することを検討する |
   | Flutter | `{SKILL_DIR}/flows/new-app/flutter-notes.md` を読み、`flutter create` コマンド・バージョン固定の注意点（`stable` 指定は404になる）を確認する |
   | React Native (Expo・既定) | `.mise.toml`（`node = "22"`, `pnpm = "latest"`）作成後、`pnpm create expo-app . --template blank-typescript && pnpm install` |
   | React Native (CLI) | ユーザーがCLI構成を明示的に希望した場合のみ選ぶ。同じ `.mise.toml` 作成後、`pnpm dlx @react-native-community/cli init <アプリ名> --directory . && pnpm install` |
   | Tauri（Rust製デスクトップアプリ） | `{SKILL_DIR}/flows/new-project/recipes/tauri-init.md` を読み、scaffoldコマンド・マージ時の`.gitignore`衝突対策・`panic="abort"`の扱いを確認する |

   会話の文脈から Next.js / Vite + React / Hono / Express 等を推定する（UI有無を問わない）。判断できない場合はユーザーに確認する。
   リアルタイム通信（WebSocket・チャット・通知）が要件にある場合は
   `{SKILL_DIR}/flows/new-project/recipes/socketio.md` を読み、実装ステップに組み込む

5. **plan.md への転記**
   - 1・3で確定した内容 → 「開発ランタイム」節の「環境管理ツール」「セットアップコマンド」「検証コマンド」
   - 4で確認したscaffoldコマンド → 同じく「開発ランタイム」節の「セットアップコマンド」に追記する
     （ランタイムのインストールとフレームワークのscaffoldは、buildフローが同じタイミングで
     一度に実行する一続きの初期化コマンド列として記載すること）
   - STACK識別子（英小文字・言語名のみ。例: node / flutter / rust / go。「Node.js」等の表記は不可）も明記する。
     既存の特別扱い値（static・flutter・node）と衝突しないよう注意する
   - Dockerを使う場合、「開発ランタイム」節に**コンテナ構成図**（mermaid flowchart）を追加する。
     各サービス（app・db等）をノードにし、利用者からのアクセス経路・サービス間の依存
     （`depends_on`）・主要なボリュームマウントを矢印で示す。空欄・省略は禁止（該当しない
     場合＝Docker不使用の場合のみこの図自体を省略する）

> **設計判断の記録:** 確認した内容は `.craft/docs/plan.md` の「設計判断」セクションに記録すること。

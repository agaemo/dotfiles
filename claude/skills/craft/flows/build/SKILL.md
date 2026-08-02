---
name: build
description: .craft/plan.md に基づいて実装を進める共通エンジン。設計フェーズ（intake〜planner、またはヒアリング→design-brief）完了直後の初回実装、または別セッションでの再開時に呼び出される。new-project・new-static・new-app から共通で利用する。
---

# build（実装フェーズ・共通エンジン）

```
SKILL_DIR = このSKILL.md（craft/flows/build/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/build/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft

入力（呼び出し元が渡す変数。設計フェーズ完了直後の呼び出しでは必須。渡された場合は下記 AUTO-DETECT より優先する）:
  STACK            = "node" | "flutter" | "static" | その他の言語識別子（例: "rust"・"go"。
                      plan.md の「開発ランタイム」節の STACK識別子に由来する。この3値以外は
                      本ファイル内で汎用パス（分岐なし）を通る）
  HAS_REVIEW_CHAIN = true（static以外） / false（static）
  HAS_FRONTEND     = true / false（フロントエンドUIがあるか）

IF 変数が渡されていない（再開時・トップレベル SKILL.md から直接呼ばれた場合のみ）:
  AUTO-DETECT:
    IF EXISTS(pubspec.yaml):                                  SET STACK = "flutter"
    ELIF EXISTS(.craft/design-brief.md) AND NOT EXISTS(.craft/stories.md): SET STACK = "static"
    ELIF EXISTS(.craft/plan.md) の「開発ランタイム」節に STACK識別子がある: SET STACK = その値
    ELSE:                                                      SET STACK = "node"
  SET HAS_REVIEW_CHAIN = (STACK != "static")
  SET HAS_FRONTEND     = EXISTS(.craft/design-brief.md) OR EXISTS(.craft/design-system.md)
ENDIF

ASSERT EXISTS(.craft/plan.md)
IF NOT EXISTS:
  REPORT: "plan.mdが見つかりません。設計フェーズ（intake〜planner、またはヒアリング→design-brief）を先に完了してください。"
  STOP

IMPORTANT: .craft/plan.md は呼び出し元フローで既にユーザー承認済みの計画である前提のため、
  本フロー内の実装・commit・ファイル生成・public/ クリーンアップはユーザーへの確認なしに進めること。
  PROHIBITED: plan.md に記載のないファイル・スコープ外の変更を加えること
```

---

## 手順

### ステップ 0: 前提確認

```
READ .craft/plan.md
READ .craft/design-system.md（存在すれば）

REPORT TO USER: 完了状況
  - 完了済みのステップ（対応するコード・ファイルが存在するか確認）
  - 未着手のステップ
  - 外部依存で未接続のもの（Firebase・外部API・認証基盤等）
```

### ステップ 0.5: 完成条件の実現可能性チェック（該当する場合のみ）

```
READ .craft/plan.md・.craft/design-brief.md（存在すれば）の完成条件を確認する

IF 完成条件が「特定の出力・振る舞いが得られること」を明記しており、
   かつその達成が今から設計する新規のロジック・アルゴリズム・独自フォーマット・DSL等
   （このプロジェクトで初めて作る核となる仕組み）に依存する:
   # 例: 独自の記法・エンコード方式・ゲームルール・計算アルゴリズムなど、
   #     ライブラリやフレームワークの標準機能だけでは実現できないもの
   # 該当しない例: 標準的なCRUD画面・フォーム・一覧表示

  IMPORTANT: セクション単位のUI実装に入る前に、その核となる仕組みを最小構成で試作し、
    完成条件を満たせることをスクリプト等で検証すること。
    PROHIBITED: 検証しないまま完成条件に合わせたUI（サンプル読み込みボタン等）を作り込むこと
    理由: 後から「仕様上その出力が原理的に出せない」と判明すると、UI実装が手戻りになる

  IF 検証できた:
    .craft/plan.md に検証方法・結果を1〜2文で記録してから通常の実装に進む
  IF 検証できなかった（完成条件を満たせない、または見積もりで大幅な追加設計が必要と分かった）:
    REPORT TO USER: 検証結果（何が・なぜ困難か）と選択肢
      1. 完成条件を実現可能な範囲に調整する
      2. 設計（核となる仕組み）を見直す
      3. 追加コスト（時間・複雑さ）を許容してこのまま進める
    WAIT_FOR: ユーザーの判断
    PROHIBITED: ユーザーの判断を待たずに実装へ進むこと
ENDIF
```

### ステップ 0.6: 開発ランタイムの構築（初回実装時のみ。再開時はスキップ）

```
IMPORTANT: このステップも言語・ランタイムマネージャー・Docker利用有無に関わらず共通で実行する。
  対応するのは planner が「開発ランタイム」節に書くセットアップコマンドの中身だけであり、
  このファイル（build/SKILL.md）自体は変更しない。

READ .craft/plan.md の「開発ランタイム」セクション

IF セクションが存在しない、または空欄（旧形式のplan.md等）:
  NOTE: 環境構築の情報源がない。既に環境構築済みの可能性が高い（再開時）。
  SKIP → ステップ0.7へ

ELIF 「環境管理ツール」の設定ファイル（.mise.toml・devbox.json・docker-compose.yml 等、
      記載された環境管理ツールに対応するファイル）が既に存在する:
  SKIP（再開時。既に構築済みのため再実行しない）→ ステップ0.7へ

ELSE（初回。環境管理ツールの設定ファイルがまだ存在しない）:
  RUN: 「セットアップコマンド」に記載のコマンドをそのまま実行する
    （ランタイムのインストール・（フロントエンドがあれば）フレームワークのscaffold等を含む）
  ASSERT: 「検証コマンド」が成功すること

  IF FAILED:
    NOTE: 「開発ランタイム」節は planner 呼び出し時点の想定に基づく設計判断であり、
      実際に構築して初めて判明する相性問題（バージョン指定がレジストリに存在しない・
      OS/アーキテクチャ依存のビルド失敗等）が起こりうる。設計ミスとは限らないため、
      即座にユーザーへ丸投げせず、まず自己診断・軽微な修正を試みること（最大2回まで）。

    ANALYZE: エラー内容から原因を推定する（バージョン指定ミス・レジストリ未登録・
      OS依存のビルド失敗・ネットワーク等）
    IF 原因を特定でき、修正が軽微（バージョン変更・コマンドの誤り修正等）と判断できる:
      FIX: .craft/plan.md の「開発ランタイム」節を実際に機能する内容に更新する
        （例: 固定バージョンをレジストリに実在する値に修正する）
      RETRY: セットアップコマンドを再実行する
      IF 2回試しても解決しない、または原因が特定できない:
        FOLLOW: 下記「エスカレーション」
    ELSE:
      FOLLOW: 下記「エスカレーション」

    --- エスカレーション ---
    REPORT TO USER: 何が・なぜ失敗したか（試した内容を含む）と選択肢
      1. 別のバージョン・ランタイムマネージャーに変更して再試行する
      2. 環境構築なしで進められる範囲（型チェック無し等）に一時的に縮小する
      3. 手動で環境構築してから再開する
    WAIT_FOR: ユーザーの判断
    IF 1（変更して再試行）:
      .craft/plan.md の「開発ランタイム」節をユーザー指定の内容に更新してから、本ステップの先頭に戻る
    PROHIBITED: ユーザーの判断を待たずに次のステップへ進むこと
```

### ステップ 0.7: Makefile の準備

```
IMPORTANT: このステップは言語・ランタイムマネージャー・Docker利用有無に関わらず共通で実行する。
  以降のステップ（動作確認・ビルド確認・実画面レビュー等）は、言語別に分岐せず
  常に `make <target>` を呼ぶ。新しい言語・ランタイム・仮想化パターンが増えても、
  対応するのは planner が「開発コマンド」表に書く実行コマンドの中身だけであり、
  このファイル（build/SKILL.md）自体は変更しない。

READ .craft/plan.md の「開発コマンド」セクション

IF EXISTS(Makefile):
  既存のMakefileを尊重する（上書きしない）。
  plan.mdの「開発コマンド」表とターゲット名が食い違う場合は、plan.md側を実態に合わせて修正する。

ELIF 「開発コマンド」セクションが存在し、表の「実行コマンド」列が埋まっている:
  表の内容から Makefile を生成する（dev/build/test/fmt/lint の5ターゲット、パターンは共通）:
    .PHONY: dev build test fmt lint
    <ターゲット名>:
    	<表の `make <ターゲット名>` 行の実行コマンド>
    （dev/build/test/fmt/lint の5つ全てについて上記パターンを展開する）

  VERIFY: 生成した Makefile に対して `make build` を試しに実行し、コマンド自体が見つかる
    （"No such file or directory" 等のシェルレベルのエラーにならない）ことを確認する。
    ビルド自体の成否は問わない（実装前のため失敗は正常）。シェルコマンドの記述自体が
    不正な場合は、該当行をユーザーに提示し修正を依頼する。

ELIF 「開発コマンド」セクションが存在するが、表の「実行コマンド」列が一部のみ埋まっている:
  埋まっている項目のみで Makefile を生成する。空欄のターゲットは
  `@echo '<ターゲット名>: plan.mdの開発コマンドセクションに実行コマンドが未記載です' && exit 1`
  をコマンドにする。
  REPORT TO USER: 空欄だったターゲット名を伝え、plan.mdの更新を提案する。

ELSE （「開発コマンド」セクションが無い、または完全に空欄 — 旧形式のplan.md・再開時等）:
  Makefileを生成しない。以降のステップでは下記「ステップ2 #フォールバック」の
  STACK別コマンドを使う。
```

### ステップ 1: テスト戦略の決定（STACK != "static" の場合のみ）

```
IF テスト環境が未セットアップ:
  RUN: tester エージェントを Agent ツール（サブエージェント、fresh general-purpose 等）で呼び出して
       テスト環境をセットアップする（vitest / pytest のセットアップ手順を案内する。Node.js のデフォルトは vitest 推奨）
       NOTE: tester はユーザーとの対話（ヒアリング）を必要としない機械的なタスクのため、
         Agent ツールでサブエージェントとして起動する（intake・designer とは異なり、
         メインClaudeが直接担当しない）。プロンプトにはこのセッションで把握済みの
         要件・技術スタック等を渡し、対象プロジェクトへのパスを明記すること。
  NOTE: 後付けでテスト環境を追加するとモック設計が困難になり、テストの書けないコードが残る。

  READ {SKILL_DIR}/flows/build/tdd-policy.md ← 対象別のTDD必須/推奨判断を確認してから実装する
  IF READ FAILED:
    WARN: "tdd-policy.md が見つかりません。"
    以下の基準で代替判断する: ビジネスロジック・API・DB操作を含むステップは実装前にtester（TDDモード）を呼ぶ。UIコンポーネント・外部サービスの薄いラッパーは実装後にtester（補完モード）で良い。
```

### ステップ 2: 実装

```
IF .craft/plan.md に「フィーチャートラック設計」セクションがある:
  FOLLOW: 下記「A. フェーズ実装（トラック設計あり）」
ELSE （トラック設計なし・小規模、または static）:
  FOLLOW: 下記「B. シンプルループ（トラック設計なし）」
```

#### A. フェーズ実装（トラック設計あり）

```
--- フェーズ1: クリティカルパス（シリアル） ---

.craft/plan.md の「フェーズ1」ステップを順番に実装する。
各ステップ完了ごとに `make build` で型エラーがないことを確認する（Makefileが無い場合は
下記「#フォールバック」を参照）。

フェーズ1完了後:
  1. `make dev` で開発サーバーを起動し、ログイン〜基本ナビゲーションが動作することを確認する
  2. バグが見つかった場合は Bug-fix TDD 手順（{SKILL_DIR}/flows/build/tdd-policy.md）で修正してから commit すること
  3. 問題なければフェーズ1の成果を git commit する（フェーズ2の起点になる）

  git add -p  # 変更を確認しながらステージング
  git commit -m "フェーズ1: クリティカルパス実装完了"
  # 実際に実装した内容に合わせてメッセージを調整すること

--- フェーズ2: 並列フィーチャートラック（worktree 分離） ---

.craft/plan.md の「フェーズ2」に定義された各トラックを、
**isolation: "worktree" + run_in_background: true** でバックグラウンド並列実行する。

各トラックに渡すプロンプト:
READ {SKILL_DIR}/flows/new-project/phase2-prompt.md  ← フェーズ2開始直前に読む
IF READ FAILED:
  REPORT: "phase2-prompt.md が見つかりません。フェーズ2を開始できません。"
  STOP
（テンプレート内の [TRACK_NAME]・[ABSOLUTE_PATH] 等を実際の値に展開してから渡すこと）

WAIT_FOR: 全トラックエージェントの完了報告を受け取ってから続きに進む

全トラック完了後:
  FOR EACH completed_track:
    1. worktree で作成されたブランチの差分を確認する
    2. main ブランチにマージする
    3. コンフリクトがあれば解消する
    4. `make build` で統合ビルドを確認する

--- フェーズ3: 統合確認 ---

全トラックのマージ完了後:
  1. `make dev` で開発サーバーを起動する
  2. 主要フローを実機で確認する（一覧→登録→詳細→操作→ダッシュボード）
     IF 認証機能を含む:
       確認前にテストアカウントを作成し、メールアドレス・パスワード（またはログインURL）を
       ユーザーに提示すること。「ログインして確認してください」とだけ伝えて、
       ログイン可能なアカウントの提示を怠らないこと。
  3. バグが見つかった場合は Bug-fix TDD 手順で修正すること:
     READ {SKILL_DIR}/flows/build/tdd-policy.md の「Bug-fix TDD 手順」
  4. `git commit` で統合完了を記録する

フェーズ3完了後にステップ4（HAS_REVIEW_CHAINがtrueの場合のレビューチェーン）へ進む。
```

#### B. シンプルループ（トラック設計なし）

```
REPEAT:
  未着手のステップを .craft/plan.md の順番で1件選ぶ
  実装する
    IF STACK == "static":
      セクション単位（.astro コンポーネント）で実装する。
      一気に全セクションを実装しない（問題の原因特定が困難になるため）。
      レスポンシブ対応は必ずモバイルファーストで実装する:
        - iPhone の論理ピクセル幅は 375〜430px。`@media (max-width: 480px)` は機能しないことがある
        - ブレークポイントは `768px`（タブレット境界）を基準にする
        - `width` / `max-width` に CSS カスタムプロパティを `calc()` で使う場合は展開後の値で検証する
        - CTA ボタンが画面幅を超えない保証: `max-width: 90%` + `box-sizing: border-box` を基本形にする
    IF 外部依存（Firebase・外部API・認証基盤等）が未接続:
      モックで実装し、CLAUDE.md に接続手順を記録する

  動作確認: `make dev` で起動・表示確認（Makefileが無い場合は下記「#フォールバック」）

  `make build` を実行する
  IF 失敗:
    REPORT: エラー内容を報告する
    修正してから次に進む

  IF .craft/plan.md の該当ステップを「完了」にマークする

  IF STACK == "static" かつ 今回のステップでユーザーが直接目にする画面要素
     （新規ページ・大きな新規コンポーネント・見た目や操作が変わる変更）を実装した:
    IF Puppeteer MCP が使える:
      スクリーンショットを撮影してユーザーに共有する
    ELSE:
      dev サーバーが未起動なら起動してから（既に起動中ならそのまま使う）、URLと
      何を確認できる状態か（例:「◯◯セクションが表示できます」）を1〜2文で共有する
    NOTE: 大がかりな承認は不要。全セクション実装し終えてから初めて画面を見せる、という
      進め方を避け、進捗が随時見える状態を保つことが目的。ユーザーからの割り込み・
      軌道修正があれば都度反映してから次のステップに進む
    IF 認証機能を含む画面を実装した:
      確認前にテストアカウントを作成し、メールアドレス・パスワード（またはログインURL）を
      ユーザーに提示すること。「ログインして確認してください」とだけ伝えないこと。
UNTIL 未着手のステップがなくなる
```

#### フォールバック（.craft/plan.md に「開発コマンド」セクションが無い場合のみ）

ステップ0.7でMakefileが生成できなかった場合（旧形式のplan.md・再開時等）に限り使う。
通常は `make build` / `make dev` を使うこと。

| STACK | ビルド確認 | 補足 |
|---|---|---|
| node | `mise exec -- pnpm build` | Node.js固有の再開時注意点: `{SKILL_DIR}/flows/new-project/agent-chain.md` の「Node.js / Webアプリ固有の再開時注意点」を参照 |
| flutter | `mise exec -- flutter analyze` | コマンド読み替え・既知の依存競合: `{SKILL_DIR}/flows/new-app/flutter-notes.md` を参照 |
| static | `mise exec -- pnpm build` | — |
| その他（Rust等） | 言語標準のビルドコマンド（例: `cargo build`）をmise経由等で実行 | plan.mdの「開発コマンド」セクションが本来の情報源。フォールバックが発生した場合はplan.mdの再生成を検討する |

### ステップ 3: 実画面レビュー（HAS_FRONTEND == true の場合）

```
IF STACK == "static":
  全セクション完了後、Puppeteer MCP が使える場合はスクリーンショットで最終確認する
ELSE （フロントエンドあり）:
  RUN: designer エージェントを呼び出す
    NOTE: designer は Agent ツール（サブエージェント）で起動禁止。メインClaudeが直接担当する
      （ユーザーとの対話・デザイン判断の連続性が必要なため。intake と同じ扱い）。
    a. Puppeteer MCP でスクリーンショットを撮影
    b. デザインブリーフ・デザインシステムとの差異を確認・修正する

IF Puppeteer MCP が使えない（未起動・未承認等）:
  FALLBACK: `make dev` でサーバーを起動し、curl 等でHTTPレベルの動作確認を行う
    （リクエスト送信 → レスポンスのステータス・本文に想定した要素が含まれるかを確認）
  REPORT TO USER: スクリーンショットではなくHTTPフロー確認で代替したことを明記する
  IF 認証機能を含む:
    テストアカウントを作成し、メールアドレス・パスワードをユーザーに提示してから確認すること
```

### ステップ 4: /ultrareview（オプション、HAS_REVIEW_CHAIN == true の場合のみ）

```
IF /ultrareview が利用可能:
  RUN: /ultrareview
ELSE:
  SKIP → ステップ5へ
CHECK: コンポーネント設計・アクセシビリティ・型安全性
```

### ステップ 5: レビューチェーン（HAS_REVIEW_CHAIN == true の場合のみ）

```
.craft/plan.md 冒頭の「レビュートラック」宣言（A/B/C）を確認する。
IF 宣言が見つからない（トラック未宣言の計画）:
  SET レビュートラック = "C"（安全側に倒し、フルチェーンを適用する）

レビュートラックに応じて以下の順に呼び出す（各エージェントは直列に、前の完了を待ってから次を呼び出す。並列実行はしない）:
  A（軽量）: verify → code-reviewer
  B（標準）: verify → qa → code-reviewer
  C（フル）: verify → security-reviewer → qa → code-reviewer → adversarial-reviewer

NOTE: これらのレビュー系エージェントは全て Agent ツール（サブエージェント、fresh general-purpose 等）
  で起動すること。intake・designer と異なりユーザーとの対話を必要とせず、むしろ
  「このセッションでの実装の経緯を知らない、独立した視点」であることが指摘の質に直結する
  （特に adversarial-reviewer は他エージェントの結果を参照せず自身の分析のみで判断する設計）。
  各エージェントへのプロンプトには、そのエージェントファイル（agents/<name>.md）の役割定義を
  貼り込み、対象プロジェクトへの絶対パスと、前段エージェントの指摘内容（再レビュー時のみ）を渡すこと。

NOTE: adversarial-reviewer（トラックCのみ）は他エージェントの承認結果に関わらず独立して判定するため、
      先行エージェントが全て承認済みでも省略しないこと。

IF いずれかのエージェントが「要修正」「非承認」「要対応」を報告した:
  REPORT TO USER: 指摘内容の要約と、対応してからステップ6に進むか・現状のまま進めるかの確認
  WAIT_FOR: ユーザーの判断
  IF 対応する: 修正してから該当エージェントを再度呼び出し、承認を得てからステップ6へ進む
```

### ステップ 6: CLAUDE.md・README.md 生成 + クリーンアップ

```
--- CLAUDE.md ---

NOTE(STACK == "static"): `pnpm create astro@latest` はCLAUDE.md（AGENTS.mdへのsymlink）を
  必ず生成するため、NOT EXISTS のみで判定すると常にスキップされプロジェクト固有の記載が
  一切残らない。EXISTS の場合でも中身を確認し、プロジェクト名・目的など固有の情報が
  含まれていなければ「汎用スキャフォールドのみ」とみなし追記対象とする。

IF NOT EXISTS(CLAUDE.md) OR （EXISTS するが プロジェクト名・目的など固有の情報を含まない汎用スキャフォールドのみ）:
  IF EXISTS(CLAUDE.md):
    READ CLAUDE.md（symlink先。通常は AGENTS.md）
    PREPEND（既存内容の前に、プロジェクト固有セクションとして挿入する。既存の汎用ガイドは保持する）
  ELSE:
    WRITE CLAUDE.md based on actual session context.

  INCLUDE（実際の値のみ。プレースホルダー禁止）:
    - プロジェクト名・目的（1〜2文）
    - スタック（実際に使う言語・フレームワーク・主要ライブラリ）
    - 開発コマンド（`make dev`/`make test`/`make build`等。.craft/plan.md の「開発コマンド」セクション参照）
    - IF HAS_REVIEW_CHAIN: アーキテクチャ（採用パターン名・ディレクトリ構造のポイント・レイヤー間の依存の向き）
    - プロジェクト固有の制約（DBエンジン・実行環境の制限など）
    - .craft/plan.md を参照するよう一言書く
    - IF STACK == "flutter": Flutter/Firebase 固有の記載事項
      READ {SKILL_DIR}/flows/new-app/flutter-notes.md の「STEP 11 CLAUDE.md に含める Flutter/Firebase 固有の記載事項」

  OMIT（書かない）:
    - 本番の認証情報・APIキー・パスワード・実在するユーザー情報
    - TODO・プレースホルダー
    - IF STACK == "static": DB・API・TDD・リリースプランナーなど不要なルール

  LIMIT: STACK == "static" なら40行以内、それ以外は60行以内
  ASSERT EXISTS(CLAUDE.md)

--- README.md ---

IF NOT EXISTS(README.md):
  WRITE README.md based on actual session context.

  INCLUDE:
    - 概要（1〜2文）
    - 前提条件（mise・実際のランタイムバージョン）
    - セットアップ手順（git clone 〜 依存インストール 〜 .env 設定（あれば））
    - コマンド一覧（dev / build / test 等）
    - IF STACK == "node": 環境変数（キー名と説明のみ。実際の値は書かない）

  OMIT: 本番の認証情報・APIキー・パスワード
  ASSERT EXISTS(README.md)

--- .craft/plan.md の更新 ---

完了したステップをすべて「完了」にマークしてから保存する。
NOTE: build フローの再開（/craft で「続きをお願いします」）は .craft/plan.md の存在に依存する。

--- public/ クリーンアップ（HAS_FRONTEND == true かつ STACK == "node" の場合） ---

FOREACH file IN [vercel.svg, next.svg, window.svg, file.svg, globe.svg]:
  IF EXISTS(public/<file>):
    IF NOT REFERENCED IN src/（Grep による静的文字列一致。動的パス構築の参照は検出できない場合がある）:
      候補に追加
    ENDIF
  ENDIF
ENDFOREACH
IF 削除候補が1件以上ある:
  REPORT TO USER: 削除候補ファイル一覧と「Grepでの参照チェックのみのため、動的にパスを組み立てて参照している場合は検出できない」旨を伝える
  WAIT_FOR: ユーザーの承認
  IF 承認: 候補を削除する

--- 完了報告 ---

ASSERT: CLAUDE.md・README.md・.craft/plan.md が全て存在すること（自己検証。いずれか欠けている場合は該当セクションに戻って再実行する）
REPORT TO USER:
  実装が完了しました。
  IF 未完了タスクが残っている状態で終了する場合:
    SAVE TO MEMORY（auto-memory に記録）は不要（.craft/plan.md に記録済みのため）
```

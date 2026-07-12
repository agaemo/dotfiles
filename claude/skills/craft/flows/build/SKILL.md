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
  STACK            = "node" | "flutter" | "static"
  HAS_REVIEW_CHAIN = true（node・flutter） / false（static）
  HAS_FRONTEND     = true / false（フロントエンドUIがあるか）

IF 変数が渡されていない（再開時・トップレベル SKILL.md から直接呼ばれた場合のみ）:
  AUTO-DETECT:
    IF EXISTS(pubspec.yaml):                                  SET STACK = "flutter"
    ELIF EXISTS(.craft/design-brief.md) AND NOT EXISTS(.craft/stories.md): SET STACK = "static"
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

### ステップ 1: テスト戦略の決定（STACK != "static" の場合のみ）

```
IF テスト環境が未セットアップ:
  RUN: tester エージェントを呼び出してテスト環境をセットアップする
       （vitest / pytest のセットアップ手順を案内する。Node.js のデフォルトは vitest 推奨）
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
各ステップ完了ごとにビルド確認コマンド（下記「スタック別ビルド確認コマンド」）で型エラーがないことを確認する。

フェーズ1完了後:
  1. 開発サーバーを起動し、ログイン〜基本ナビゲーションが動作することを確認する
     （node: `mise exec -- pnpm dev` / flutter: `mise exec -- flutter run`）
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
    4. ビルド確認コマンドで統合ビルドを確認する

--- フェーズ3: 統合確認 ---

全トラックのマージ完了後:
  1. 開発サーバーを起動する
  2. 主要フローを実機で確認する（一覧→登録→詳細→操作→ダッシュボード）
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

  動作確認:
    node:    `mise exec -- pnpm dev` で表示確認
    flutter: `mise exec -- flutter run` で起動確認
    static:  `mise exec -- pnpm dev` で表示確認

  ビルド確認（下記「スタック別ビルド確認コマンド」）を実行する
  IF 失敗:
    REPORT: エラー内容を報告する
    修正してから次に進む

  IF .craft/plan.md の該当ステップを「完了」にマークする
UNTIL 未着手のステップがなくなる
```

#### スタック別ビルド確認コマンド

| STACK | ビルド確認 | 補足 |
|---|---|---|
| node | `mise exec -- pnpm build` | Node.js固有の再開時注意点: `{SKILL_DIR}/flows/new-project/agent-chain.md` の「Node.js / Webアプリ固有の再開時注意点」を参照 |
| flutter | `mise exec -- flutter analyze` | コマンド読み替え・既知の依存競合: `{SKILL_DIR}/flows/new-app/flutter-notes.md` を参照 |
| static | `mise exec -- pnpm build` | — |

### ステップ 3: 実画面レビュー（HAS_FRONTEND == true の場合）

```
IF STACK == "static":
  全セクション完了後、Puppeteer MCP が使える場合はスクリーンショットで最終確認する
ELSE （node・flutter のフロントエンドあり）:
  RUN: designer エージェントを呼び出す
    a. Puppeteer MCP でスクリーンショットを撮影
    b. デザインブリーフ・デザインシステムとの差異を確認・修正する
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

IF NOT EXISTS(CLAUDE.md):
  WRITE CLAUDE.md based on actual session context.

  INCLUDE（実際の値のみ。プレースホルダー禁止）:
    - プロジェクト名・目的（1〜2文）
    - スタック（実際に使う言語・フレームワーク・主要ライブラリ）
    - 開発コマンド（dev / test / build の実際のコマンド）
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

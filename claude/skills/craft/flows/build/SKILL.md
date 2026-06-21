---
name: build
description: .craft/plan.md に基づいて実装を進める共通エンジン。設計フェーズ（intake〜planner、またはヒアリング→design-brief）完了直後の初回実装、または別セッションでの再開時に呼び出される。new-project・new-static・new-app から共通で利用する。
---

# build（実装フェーズ・共通エンジン）

```
SKILL_DIR = このSKILL.md（craft/flows/build/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/build/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft

入力（呼び出し元が渡す変数。設計フェーズ完了直後の呼び出しでは必須）:
  STACK            = "node" | "flutter" | "static"
  HAS_REVIEW_CHAIN = true（node・flutter） / false（static）
  HAS_FRONTEND     = true / false（フロントエンドUIがあるか）

IF 変数が渡されていない（再開時・トップレベル SKILL.md から直接呼ばれた場合）:
  AUTO-DETECT:
    IF EXISTS(pubspec.yaml):                                  SET STACK = "flutter"
    ELIF EXISTS(docs/design-brief.md) AND NOT EXISTS(.craft/stories.md): SET STACK = "static"
    ELSE:                                                      SET STACK = "node"
  SET HAS_REVIEW_CHAIN = (STACK != "static")
  SET HAS_FRONTEND     = EXISTS(.craft/design-brief.md) OR EXISTS(.craft/design-system.md) OR EXISTS(docs/design-brief.md)
ENDIF

ASSERT EXISTS(.craft/plan.md)
IF NOT EXISTS:
  REPORT: "plan.mdが見つかりません。設計フェーズ（intake〜planner、またはヒアリング→design-brief）を先に完了してください。"
  STOP
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

  | 対象 | 方針 | 理由 |
  |------|------|------|
  | API ルート・ミドルウェア・認証ロジック | **TDD 必須** | DBバグ・認証バイパスの温床。後から追加しにくい |
  | DBクエリ・マイグレーション | **TDD 必須** | スキーマ変更後に追加すると既存動作の担保が取れない |
  | バリデーション・状態遷移関数 | **TDD 必須** | 境界値バグが本番で発覚しやすく、修正コストが高い |
  | その他のビジネスロジック関数 | TDD 推奨 | ロジックの複雑度に応じて判断 |
  | UI コンポーネント | 任意 | 実画面確認で代替可能 |
  | サーバーレスエッジ関数 | ローカルエミュレーターで統合テスト | ユニットテストでは実行環境を再現できない |
  | WebSocket・リアルタイムイベント | 統合テスト推奨 | イベントループの非同期性がユニットテストでは再現困難 |
  | 外部API連携 | モックで単体テスト | 実APIへの依存を排除してFastを保つ |

  TDD 必須の層を実装するときは `tester` エージェントを「TDDモード」で先に呼び出すこと。
  `tester` が Red（失敗）を確認したら実装に進み、Green になったら次の層へ。

  バグが見つかった場合は**フェーズを問わず**ステップ2の Bug-fix TDD 手順で修正すること。
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
  2. バグが見つかった場合は Bug-fix TDD 手順（フェーズ3参照）で修正してから commit すること
  3. 問題なければフェーズ1の成果を git commit する（フェーズ2の起点になる）

  git add -p  # 変更を確認しながらステージング
  git commit -m "フェーズ1: クリティカルパス実装完了"
  # 実際に実装した内容に合わせてメッセージを調整すること

--- フェーズ2: 並列フィーチャートラック（worktree 分離） ---

.craft/plan.md の「フェーズ2」に定義された各トラックを、
**isolation: "worktree" + run_in_background: true** でバックグラウンド並列実行する。

各トラックに渡すプロンプト:
READ {SKILL_DIR}/flows/new-project/phase2-prompt.md  ← フェーズ2開始直前に読む
（テンプレート内の [TRACK_NAME]・[ABSOLUTE_PATH] 等を実際の値に展開してから渡すこと）

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
  3. バグが見つかった場合は以下の **Bug-fix TDD** 手順で修正すること:
     a. `tester` エージェントを「バグ修正TDDモード」で呼び出し、バグを再現するテストを書く
     b. テストが Red（失敗）になることを確認する（再現できない場合は再現手順を精査する）
     c. バグを修正する
     d. テストが Green になることを確認する
     e. 補完モードで `tester` を再度呼び出してリグレッションテストを追加する
     ⚠️ PROHIBITED: テストを書かずに直接修正すること（同じバグが再発しても検出できなくなる）
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
verify → security-reviewer → qa → code-reviewer の順に呼び出す
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
    IF NOT REFERENCED IN src/:
      DELETE public/file
    ENDIF
  ENDIF
ENDFOREACH
NOTE: 要件検討中にロゴ等を public/ に置いている場合があるため、参照チェックを必ず行ってから削除すること

--- 完了報告 ---

REPORT TO USER:
  実装が完了しました。
  IF 未完了タスクが残っている状態で終了する場合:
    SAVE TO MEMORY（auto-memory に記録）は不要（.craft/plan.md に記録済みのため）
```

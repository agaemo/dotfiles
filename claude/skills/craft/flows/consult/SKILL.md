---
name: consult
description: 既存システムの課題・移行・リファクタについて相談し、選択肢の整理から実行・PRまでを行う。/craft で「既存システムの相談」を選択したときに実行される。
---

# consult（相談フロー）

「なんか遅くなってきた」「認証まわりが複雑になってきた」など、
現状のシステムへの漠然とした課題感から相談できる。
移行先が決まっていなくても、移行しない結論になっても構わない。

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/consult/SKILL.md で読んだ場合
  # → SKILL_DIR = /Users/alice/.claude/skills/craft
```

---

## 手順

### ステップ 1: 相談

```
ASK USER:
  現在のシステムについて、気になっていることや困っていることを
  自由に話してください。

WAIT_FOR: ユーザーの話

# テスト・品質・QAに関する相談であれば qa フローに委譲する
IF 相談内容がテスト・品質・QA基盤・カバレッジに関するもの:
  READ {SKILL_DIR}/flows/qa/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP

IF 話が漠然としている・追加情報が必要:
  ASK: 状況を深掘りする質問を1件ずつ行う
    例: 「それはどのくらいの頻度で起きていますか？」
        「現在の構成はどうなっていますか？」
  REPEAT: 課題の輪郭が掴めるまで繰り返す
```

### ステップ 2: 現状調査

```
READ: コードベースを調査し、相談内容に関連する箇所を把握する
  調査手順:
    1. Glob / Bash(find) でプロジェクト構造・依存パッケージ（package.json 等）を把握する
    2. 課題に関係するファイルを Read で読む（深さは課題の複雑度に応じて調整）
    3. Bash(grep) で関連するシンボル・エラーメッセージを横断検索する
  確認すべき観点:
    - 課題に関係するファイル・設定・依存パッケージのバージョン
    - テストカバレッジの有無（test/ ディレクトリ・package.json の test スクリプト）
    - 関連する複雑度・技術的負債の箇所

REPORT: 調査結果をユーザーに共有する
  - 課題の根本原因として考えられること
  - 影響を受けている範囲
```

### ステップ 3: 選択肢の整理・提案

```
ANALYZE: 課題と調査結果をもとに、取りうる選択肢を整理する

PRESENT: 以下の形式で選択肢を提示する

  ## 現状の課題
  [課題を1〜2文で整理]

  ## 選択肢

  ### A. [移行・刷新する場合]
  - 内容: FROM → TO
  - メリット: ...
  - デメリット・リスク: ...
  - 工数感: ...

  ### B. [リファクタ・改善で対応する場合]
  - 内容: ...
  - メリット: ...
  - デメリット・リスク: ...
  - 工数感: ...

  ### C. [今は対応しない場合]
  - 理由: ...
  - 今後どうなるか: ...

  ## 推奨
  [状況をふまえたおすすめとその理由]

GATE: ユーザーの判断を仰ぐ
  → 今は対応しない・相談だけで終わる選択も同等に扱う
```

### ステップ 4: 実行（移行・刷新を選んだ場合のみ）

```
IF ユーザーが「今は対応しない」「相談だけ」を選択:
  STOP: 選択肢の整理・推奨の提示をもって完了とする

IF ユーザーが移行・リファクタを選択:

  PLAN:
    作業をフェーズに分割する。各フェーズは以下の条件を満たすこと：
      - 独立してテスト・検証できる単位
      - ロールバック手順が明確
      - 前のフェーズが成功しないと次に進まない

    計画フォーマット：
      ## 実行計画

      ### フェーズ 1: [名称]
      - 変更内容: ...
      - 変更ファイル: ...
      - 検証方法: ...
      - ロールバック: ...

      ### フェーズ N: ...

      ### 残作業（手動対応が必要なもの）
      - ...

  GATE: 計画の承認を得る
    → 修正要望があれば計画を更新して再提示する
  PROHIBITED: 承認前に実行フェーズへ進むこと

  ASK USER:
    実行にあたって以下を確認します。
    1. GitHub issue を作成しますか？（変更の背景・経緯を記録）
    2. 完了後に PR を作成しますか？
    ※ サンプル・学習目的など「ローカル作業のみ」の場合は両方不要で構いません。

  WAIT_FOR: ユーザーの回答

  CREATE_ISSUE = ユーザーが issue 作成を希望した場合
  CREATE_PR    = ユーザーが PR 作成を希望した場合
  LOCAL_ONLY   = ユーザーが issue も PR も不要と回答した場合

  IF CREATE_ISSUE:
    READ {SKILL_DIR}/flows/consult/issue-template.md  ← issue本文フォーマットを確認してから作成する
    gh issue create \
      --title "[consult] <課題を端的に>" \
      --body "$(issue-template.md のフォーマットに従って記載)"
    ISSUE_NUMBER = 作成した issue の番号
    ASSERT: ISSUE_NUMBER が取得できたこと（gh コマンドが成功したこと）
    IF FAILED: REPORT "issue 作成に失敗しました。gh auth status を確認してください。" → STOP
  ELSE:
    ISSUE_NUMBER = なし

  # ブランチは issue・PR の有無に関わらず常に作成する（変更の分離のため）
  IF git remote がない（ローカルのみリポジトリ）:
    RUN: DEFAULT_BRANCH=$(git symbolic-ref HEAD | sed 's@^refs/heads/@@')
    NOTE: リモートなしのため pull はスキップ
  ELSE:
    RUN: DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
    RUN: git checkout ${DEFAULT_BRANCH} && git pull
    IF 失敗:
      REPORT: pull に失敗した旨を伝え、コンフリクトや認証問題がないか確認を促す
      STOP
  ENDIF

  BRANCH = consult/<slug>
    例: consult/sqlite-to-mysql、consult/auth-refactor
  RUN: git checkout -b {BRANCH}
  ASSERT: ブランチが作成されて切り替わっていること（`git branch --show-current` = {BRANCH}）
  IF FAILED: REPORT "ブランチ作成に失敗しました。既存ブランチと競合している可能性があります。" → STOP

  FOREACH phase IN 計画:
    REPORT: 「フェーズ N を開始します」と通知
    EXECUTE: そのフェーズの変更を適用する
    VERIFY:
      ビルド・lint・型チェックのうち利用可能なものを実行する
    IF 検証失敗:
      ROLLBACK: git checkout -- .
      REPORT: 失敗内容と原因をユーザーに報告する
      STOP: ユーザーの判断を仰ぐ
    GATE: 次フェーズへの進行承認を得る
```

### ステップ 5: 完了・PR 作成（実行した場合のみ）

```
IF CREATE_PR == false:
  REPORT: 変更内容のサマリーを表示して完了とする
  STOP

READ {SKILL_DIR}/flows/consult/pr-template.md  ← PR本文フォーマットを確認してから作成する

CREATE PR:
  タイトル: [変更内容を端的に]（例: migrate: SQLite → MySQL）
  本文: pr-template.md のフォーマットに従って記載
    IF ISSUE_NUMBER != なし: 最後に "Closes #ISSUE_NUMBER" を追加

  # PR 作成後にレビュースキルで自動レビューを実行する
  PR_NUMBER = 作成した PR の番号
  INVOKE SKILL: /review {PR_NUMBER}  ← Skill ツールで review スキルを呼び出す（bash RUN ではない）

  # デフォルトブランチに戻す
  RUN: git checkout {DEFAULT_BRANCH}
```

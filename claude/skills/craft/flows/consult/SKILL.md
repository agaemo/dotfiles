---
name: consult
description: 既存システムの課題・移行・リファクタ、または新規構築だが既存レシピ（static/project/app）に当てはまらない技術の相談を受け、選択肢の整理から実行・PRまでを行う。テスト・品質・QAの相談は内容に応じて qa / qa-consult に委譲する。/craft で「既存システムの相談」を選択したとき、または scope フローで対応レシピが見つからなかったときに実行される。
---

# consult（相談フロー）

「なんか遅くなってきた」「認証まわりが複雑になってきた」など、
現状のシステムへの漠然とした課題感から相談できる。
移行先が決まっていなくても、移行しない結論になっても構わない。

既存システムに限らず、GASのように新規構築だが既存レシピに当てはまらない
技術の相談も受け付ける（SIerのように「型にはまらない依頼」を広く受け持つ役割）。

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/consult/SKILL.md で読んだ場合
  # → SKILL_DIR = /Users/alice/.claude/skills/craft
```

---

## 手順

### ステップ 1: 相談

```
IF scope フローから SUMMARY（要望・制約・対象技術カテゴリ）を渡されて起動された:
  SUMMARY の内容を前提として扱う（再ヒアリングしない）
  SET 相談対象 = "新規構築（対応レシピなし）"
  SKIP TO ステップ2

ASK USER:
  現在のシステムについて、または実現したいが既存の型（静的サイト・Webアプリ・
  クロスプラットフォームアプリ）に当てはまらない新規構築について、
  気になっていることや実現したいことを自由に話してください。

WAIT_FOR: ユーザーの話

IF 話が漠然としている・追加情報が必要:
  ASK: 状況を深掘りする質問を1件ずつ行う
    例: 「それはどのくらいの頻度で起きていますか？」
        「現在の構成はどうなっていますか？」
  REPEAT: 課題の輪郭が掴めるまで繰り返す

SET 相談対象 = 話の内容から判定する（"既存システム" または "新規構築（対応レシピなし）"）

# テスト・品質・QAに関する相談は、実装を伴うかどうかで委譲先を分ける
IF 相談内容がテスト・品質・QAに関するもの:
  IF まだ「実装まで進めたいか／相談のみか」が不明確:
    ASK USER: 「テストコードを書く・ツールを導入するところまで一緒に進めたいか、
                まずは方針や体制を相談したいか」
    WAIT_FOR: ユーザーの回答
  SUMMARY = ここまでの相談内容を要約したもの（課題・現状・希望する進め方）

  IF ユーザーが実装（テストコード追加・フレームワーク導入・CI組み込み等）まで進めたいと明言:
    READ {SKILL_DIR}/flows/qa/SKILL.md
    FOLLOW: そこに記述されたすべての手順を実行する。
            ステップ1（ブリーフィング）には SUMMARY を渡し、不足している点のみ質問させる。
    STOP
  ELSE （テスト計画・戦略立案、QA体制・プロセス構築、品質指標・バグ管理など相談のみ、または未確定）:
    READ {SKILL_DIR}/flows/qa-consult/SKILL.md
    FOLLOW: そこに記述されたすべての手順を実行する。SUMMARY を相談の前提として渡す。
    STOP
```

### ステップ 2: 現状調査

```
IF 相談対象 == "既存システム":
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

ELSE （相談対象 == "新規構築（対応レシピなし）"）:
  RESEARCH: WebSearch で対象技術のセットアップ手順・制約・既知の問題を調査する
    調査観点:
      - 公式のセットアップ・スカフォルディング手順
      - craft の既存レシピ（mise・Node.js等）と組み合わせられるか
      - 典型的な落とし穴・既知の制約

  REPORT: 調査結果をユーザーに共有する
    - 実現可能性
    - 必要な前提条件・制約
    - 想定される技術的リスク
```

### ステップ 3: 選択肢の整理・提案

```
ANALYZE: 課題と調査結果をもとに、取りうる選択肢を整理する

IF 相談対象 == "既存システム":
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

ELSE （相談対象 == "新規構築（対応レシピなし）"）:
  PRESENT: 以下の形式で選択肢を提示する

    ## 実現したいこと
    [要望を1〜2文で整理]

    ## 選択肢

    ### A. 自前で構築を進める
    - 内容: 調査した手順に沿って手動セットアップする
    - メリット: ...
    - デメリット・リスク: ...
    - 工数感: ...

    ### B. 近い既存カテゴリ（レシピ）で妥協する
    - 内容: static / project / app のうち最も近いものを使う
    - メリット: ...
    - デメリット・リスク: ...

    ### C. [今は対応しない場合]
    - 理由: ...
    - 今後どうなるか: ...

    ## 推奨
    [状況をふまえたおすすめとその理由]

GATE: ユーザーの判断を仰ぐ
  → 今は対応しない・相談だけで終わる選択も同等に扱う
```

### ステップ 4: 実行（移行・刷新、または自前で構築を選んだ場合のみ）

```
IF ユーザーが「今は対応しない」「相談だけ」を選択:
  STOP: 選択肢の整理・推奨の提示をもって完了とする

IF ユーザーが移行・リファクタ、または自前で構築を選択:

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

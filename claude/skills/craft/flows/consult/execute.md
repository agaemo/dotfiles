---
name: consult-execute
description: consultフローで「移行・刷新」または「自前で構築を進める」を選んだ場合の実行フェーズ（計画作成〜フェーズ実行〜完了・PR作成）。flows/consult/SKILL.md ステップ4から、選択された場合のみ読み込まれる。
---

# consult 実行フェーズ

（本ファイルは consult/SKILL.md から、ユーザーが「移行・リファクタ」または「自前で構築を進める」を
選んだ場合のみ READ される。SKILL_DIR・相談対象 は呼び出し元で定義済みの値をそのまま使う）

```
# 環境構築（ランタイム・パッケージマネージャーのインストール等）を伴う計画の場合、
# new-project と同じ選定方針を PLAN 作成前に適用する（mise 優先の原則を徹底するため）
IF 相談対象 == "新規構築（対応レシピなし）" AND 選択した対応方針にランタイム・パッケージマネージャー等のインストールが伴うと判断される場合:
  READ {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md
  IF READ FAILED:
    NOTE: 読めない場合でも以下の原則に従うこと — 環境管理ツールはデフォルトを mise とし、
          未知の言語・ツールはまず mise registry で対応可否を確認してから個別インストールを
          検討する
  APPLY: 「開発ランタイムの選定方針」に従い、環境管理ツール・言語バージョン・
    セットアップコマンド・検証コマンドを確定する
    IMPORTANT: 公式ドキュメントが特定のツール（例: pixi）を推奨していても、
    まず mise 管理下に置けないか（例: `mise registry | grep <言語>`）を確認すること。
    mise で対応できない場合のみ個別ツールの直接インストールを検討し、その理由を
    PLAN の該当フェーズに明記する。Web検索で見つけた「公式推奨手順」をそのまま
    採用する前に、必ずこの確認を経ること。

PLAN:
  作業をフェーズに分割する。各フェーズは以下の条件を満たすこと：
    - 独立してテスト・検証できる単位
    - ロールバック手順が明確
    - 前のフェーズが成功しないと次に進まない
  IF 環境構築を伴う場合:
    該当フェーズに、上記で確定した「環境管理ツール」「セットアップコマンド」「検証コマンド」を
    明記すること（new-project の plan.md「開発ランタイム」節と同等の粒度で書く）

  計画フォーマット：
    ## 実行計画

    ### フェーズ 1: [名称]
    - 変更内容: ...
    - 変更ファイル: ...
    - 検証方法: ...（自動検証できないもの は「手動確認」と明記する）
    - ロールバック: ...

    ### フェーズ N: ...

    ### 残作業（手動確認が必要なもの）
    # 以下は自動検証が困難なため、ブラウザ・実機での手動確認が必要と明記すること:
    #   - ドラッグ＆ドロップ操作（dnd-kit 等のPointerEvent依存UI）
    #   - IME入力（日本語変換中のEnterキー挙動）
    #   - アニメーション・トランジション
    #   - ホバー・フォーカス等のインタラクティブ状態
    - ...

REPEAT:
  SELF_EVALUATE: 計画を提示する前に、相談内容の理解度を以下の5項目で1〜5点採点する
    スケール: 1=全く不明 / 2=断片的 / 3=概ね把握 / 4=ほぼ確信 / 5=完全に理解

    | # | 評価項目                                                          | スコア |
    |---|--------------------------------------------------------------------|--------|
    | 1 | 相談対象・課題（何を解決・実現したいか）                          |        |
    | 2 | 制約・前提（実行環境・入出力形式・環境分離方式・依存エコシステム等）|       |
    | 3 | 選定した対応方針とその理由（なぜこの選択肢を選んだか）            |        |
    | 4 | 実行計画の妥当性（フェーズ分割・検証方法・ロールバック）          |        |
    | 5 | 完了条件（何をもって完了とするか、残作業の扱い）                  |        |

  IF ANY(score < 4):
    ASK USER: スコアが4未満の項目について不明点を質問する
    APPLY: 得られた回答を計画に反映する
  ENDIF
UNTIL ALL(score >= 4)

GATE: 計画の承認を得る
  → 修正要望があれば計画を更新して再提示する
PROHIBITED: 承認前に実行フェーズへ進むこと

# .craft/ はプロジェクトの内部管理用ディレクトリ（相談経緯・技術選定理由等を含む）であり、
# リポジトリにコミットしない。new-project/new-static/new-app は共通gitignoreテンプレートで
# 除外済みだが、consult は .craft/docs を書き込む前にここで確実に除外する
IF .gitignore が存在しない、または `.craft/` を除外する行が無い:
  IF {SKILL_DIR}/gitignore が読める:
    APPEND: {SKILL_DIR}/gitignore の内容を .gitignore に追記（.gitignore が無ければ新規作成）
  ELSE:
    APPEND: `.craft/` を .gitignore に追記（.gitignore が無ければ新規作成）
  ASSERT: .gitignore に `.craft/` を除外する行が含まれること

# 承認された計画を .craft/docs/plan.md に保存する（実行前の計画として必ず残す。
# 後述の fix ファイルとは役割が異なる: plan.md は実行前の設計、fix ファイルは実行後の変更記録）
IF .craft/docs/plan.md が存在しない:
  WRITE .craft/docs/plan.md:
    ## 相談内容
    [相談対象・要望を1〜2文]

    ## 開発ランタイム（環境構築を伴う場合のみ。上記で確定した内容をそのまま転記）
    **環境管理ツール:** ...
    **セットアップコマンド:** ...
    **検証コマンド:** ...

    [PLAN で作成した「## 実行計画」以下をそのまま続けて記載]
ELSE:
  .craft/docs/plan.md の末尾に「## 追加計画（{YYYY-MM-DD}）」として、上記と同じ内容を追記する
ASSERT EXISTS(.craft/docs/plan.md)

# git リポジトリが無ければ初期化する（以降の git 操作の前提のため）
IF .git が存在しない:
  RUN: git init -b main
  SET NEW_REPO = true
  NOTE: 新規作成したリポジトリのため、後述のブランチ作成では consult 用のブランチ分離を行わず
        main のまま進める
ELSE:
  SET NEW_REPO = false

IF git remote がない（ローカルのみリポジトリ）:
  REPORT: 「GitHubリポジトリが未設定のため、issue/PR作成はスキップします」
  CREATE_ISSUE = false
  CREATE_PR    = false
  LOCAL_ONLY   = true
ELSE:
  ASK USER:
    実行にあたって以下を確認します。
    1. GitHub issue を作成しますか？（変更の背景・経緯を記録）
    2. 完了後に PR を作成しますか？
    ※ サンプル・学習目的など「ローカル作業のみ」の場合は両方不要で構いません。

  WAIT_FOR: ユーザーの回答

  CREATE_ISSUE = ユーザーが issue 作成を希望した場合
  CREATE_PR    = ユーザーが PR 作成を希望した場合
  LOCAL_ONLY   = ユーザーが issue も PR も不要と回答した場合

# fix ファイルを作成して .craft/docs/plan.md に追記する（issue/PR の有無にかかわらず常に実施）
IF .craft/docs/ ディレクトリが存在する:
  FIX_FILE = .craft/docs/{YYYYMMDD}-{slug}.md
    # YYYYMMDD: 今日の日付, slug: 変更内容を英数字+ハイフンで短く表現（例: kanban-fixes）
  WRITE {FIX_FILE}: 以下の内容を記録する
    - ## 課題: 今回対応した問題の概要
    - ## 実行計画: フェーズ一覧と変更ファイル
    - ## 残作業（手動確認）: 自動検証できなかった項目
  IF .craft/docs/plan.md に「## 修正ファイル一覧」セクションが存在する:
    そのセクションに「| [{FIX_FILE}]({FIX_FILE}) | {概要1行} |」を追記する
  ELSE:
    .craft/docs/plan.md の末尾に以下を追記する:
      ## 修正ファイル一覧
      | ファイル | 概要 |
      |---|---|
      | [{FIX_FILE}]({FIX_FILE}) | {概要1行} |

IF CREATE_ISSUE:
  READ {SKILL_DIR}/flows/consult/issue-template.md  ← issue本文フォーマットを確認してから作成する
  BODY = issue-template.md のフォーマットに従って本文を作成する
  RUN: gh issue create --title "[consult] <課題を端的に>" --body "<BODY の内容>"
  ISSUE_NUMBER = 作成した issue の番号
  ASSERT: ISSUE_NUMBER が取得できたこと（gh コマンドが成功したこと）
  IF FAILED: REPORT "issue 作成に失敗しました。gh auth status を確認してください。" → STOP
ELSE:
  ISSUE_NUMBER = なし

# ブランチ作成。ただしリポジトリが新規（今回 git init した）、または
# 既存リポジトリでもコミットが1つも無い場合は、ブランチ分離を行わずそのまま進める
IF NEW_REPO == true:
  SET DEFAULT_BRANCH = "main"
  SET BRANCH = "main"
ELIF `git rev-parse HEAD` が失敗する（コミットが1つも無い）:
  RUN: DEFAULT_BRANCH=$(git symbolic-ref HEAD | sed 's@^refs/heads/@@')
  SET BRANCH = DEFAULT_BRANCH
  NOTE: 初回コミット前のため、ブランチ分離は行わない
ELIF git remote がない（ローカルのみリポジトリ）:
  RUN: DEFAULT_BRANCH=$(git symbolic-ref HEAD | sed 's@^refs/heads/@@')
  NOTE: リモートなしのため pull はスキップ
  BRANCH = consult/<slug>
    例: consult/sqlite-to-mysql、consult/auth-refactor
  RUN: git checkout -b {BRANCH}
ELSE:
  RUN: DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
  RUN: git checkout ${DEFAULT_BRANCH} && git pull
  IF 失敗:
    REPORT: pull に失敗した旨を伝え、コンフリクトや認証問題がないか確認を促す
    STOP
  BRANCH = consult/<slug>
    例: consult/sqlite-to-mysql、consult/auth-refactor
  RUN: git checkout -b {BRANCH}
ENDIF

IF BRANCH != DEFAULT_BRANCH:
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

## 完了・PR 作成

```
# テストが通った・ビルドが成功した、は「残作業（手動確認）」の完了を意味しない。
# 計画時に自動検証できないと明記した項目（実機確認・目視確認等）は、ここで
# 個別に確認しないまま完了報告をしない
IF 計画（plan.md または FIX_FILE）に「残作業（手動確認）」の項目がある:
  PRESENT: 残作業（手動確認）の一覧
  ASK USER: 各項目を確認済みか、それとも未確認のまま完了としてよいか
  WAIT_FOR: ユーザーの回答
  NOTE: 未確認のまま完了する場合も、その旨を次の完了報告に明記する（確認済みと誤認させない）

IF CREATE_PR == false:
  REPORT: 変更内容のサマリーを表示して完了とする（ISSUE_NUMBER != なし の場合は作成した issue へのリンクも含める）
  STOP

READ {SKILL_DIR}/flows/consult/pr-template.md  ← PR本文フォーマットを確認してから作成する

CREATE PR:
  タイトル: [変更内容を端的に]（例: migrate: SQLite → MySQL）
  本文: pr-template.md のフォーマットに従って記載
    IF ISSUE_NUMBER != なし: 最後に "Closes #ISSUE_NUMBER" を追加

  # PR 作成後にレビュースキルで自動レビューを実行する
  PR_NUMBER = 作成した PR の番号
  INVOKE SKILL: /review {PR_NUMBER}  ← Skill ツールで review スキルを呼び出す（bash RUN ではない）
  IF レビューで重大な指摘がある:
    REPORT: 指摘内容をユーザーに共有し、対応するか確認する
    WAIT_FOR: ユーザーの判断

  # デフォルトブランチに戻す
  RUN: git checkout {DEFAULT_BRANCH}
```

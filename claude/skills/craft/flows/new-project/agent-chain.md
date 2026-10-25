---
name: new-project-agent-chain
description: new-project セットアップ完了後の設計フェーズ・エージェントチェーン（STEP 1-7、STEP7はbuildフローへ委譲）・オプションエージェント・Node.js 再開時注意点。既存の設計書のレビュー・検証には使わない
---

# 標準エージェントチェーン（新規プロジェクト・新機能）

セットアップ完了後は以下の順で必ず実行すること。

> **IMPORTANT — PROHIBITED:** `intake`・`designer` を Agent ツール（サブエージェント）で起動すること
> 理由: ユーザーとの対話が必要。`{SKILL_DIR}/agents/<name>.md` を READ し、その指示に従って
> メインClaude自身が直接実行すること（Agentツールは使わない）。`refiner` も、未解決の疑問をユーザーに
> 確認する場合があるため、同様にメインClaude自身が実行する。
> 一方 `planner` と、レビュー系エージェント（build フローが起動する）は、ユーザー対話を必要としない
> 機械的なタスクのため、Agent ツール（サブエージェント）で起動する。

```
# SKILL_DIR は呼び出し元（new-project/SKILL.md 等）で定義済みの絶対パス（craftディレクトリを指す）。
# このファイル自身では定義しない。
# HAS_FRONTEND は呼び出し元（new-project/SKILL.md ステップ1、または new-app/SKILL.md ステップ1）で
# 設定済みの変数（このチェーン全体で参照する）。このファイル自身のSTEP1（intake）では設定されない。
# true  → STEP 3（デザイン）・build フロー内の実画面レビューを実施
# false → STEP 3・実画面レビューをスキップ
```

NOTE: 各 GATE で承認を求める前に以下の形式で進捗を必ず表示すること（N はフロントあり4・なし3）:
  ── 承認 [N/N]: <ページ名> ──────────────────────
  ✅ 01 要件定義（承認済み）
  👉 02 ユーザーストーリー（承認待ち）
  ⬜ 03・04 画面モック・デザインシステム（未着手）
  ⬜ 05 実装計画（未着手）
  NOTE: 項目の番号と名前は、確認用ページのメニュー（承認ゲートの6スロット。preview-generation.md の表）と同じものを使う。
        06 統合設計書は承認を求めないため、この進捗には載せない（N にも数えない）。
  ──────────────────────────────────────────
  NOTE: HAS_FRONTEND == false の場合は「STEP 3: デザイン」の行を省き、Nは3に読み替える

共通ルール（ASSERT）: 各 STEP の ASSERT が失敗した場合は、原因を報告して該当の出力を再作成する（最大1回）。
  解消しなければ、ユーザーに報告して STOP する。

共通ルール（プレビュー生成）: 以下の各STEPで「プレビュー生成（共通ルール参照）」と書かれた箇所は、
  GATEの前に必ず次を実施する:
    READ {SKILL_DIR}/flows/new-project/preview-generation.md（このプレビュー生成チェーン中に
    未読の場合のみ。セッションが変わった場合は再度READする。共通ルール・CDN方針・
    ASSERT/失敗時の代替導線が定義されている）
  その後、各STEPに書かれた固有の内容でHTMLを作成し、指定の出力先に保存する。
  保存のたびに、preview-generation.md の「index.html の生成と更新」に従って
  .craft/review/index.html のメニュー（review_index.py の set / skip / extra）を更新し、
  ユーザーには index.html を開いて提示する。ファイル名と番号は、同ファイルの固定スロットの表に従う（変えない）。
  初回（STEP 1 の保存時）に index.html を init し、HAS_FRONTEND == false なら design を「UI なし」で skip にする。

```
STEP 1: intake
  OUTPUT: .craft/docs/requirements.md
  ASSERT EXISTS(.craft/docs/requirements.md)

  プレビュー生成（共通ルール参照）:
    python3 -I {SKILL_DIR}/flows/new-project/scripts/md2html.py .craft/review/gates/01-requirements.html 要件定義 .craft/docs/requirements.md
      - 形式は固定（requirements.md の章立てを、そのまま共通の見た目で出す）。HTML を手で書かない
      - 追加したい補足があれば、requirements.md に節を足す（足した節もそのまま表示される）
    出力先: .craft/review/gates/01-requirements.html

  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

STEP 2: refiner
  INPUT:  .craft/docs/requirements.md
  OUTPUT: .craft/docs/stories.md
  ASSERT EXISTS(.craft/docs/stories.md)
  NOTE: 未解決の疑問はユーザーから回答を得た後も削除しない。
        以下の形式でチェック済みにして残すこと（意思決定の根拠として保持）:
        - [x] [疑問の内容]
              → **回答（YYYY-MM-DD）:** [回答内容]

  プレビュー生成（共通ルール参照）:
    python3 -I {SKILL_DIR}/flows/new-project/scripts/md2html.py .craft/review/gates/02-stories.html ユーザーストーリー .craft/docs/stories.md
      - 形式は固定。変換スクリプトが、US をカード（誰が・何をしたい・なぜ・受け入れ条件・サイズ・依存）にし、
        「未解決の疑問」を回答済み（緑の✓）/未回答（□）で区別する。HTML を手で書かない
      - 補足は stories.md に書く（カード以外の節は、通常の見出しと本文で表示される）
    出力先: .craft/review/gates/02-stories.html

  GATE: 承認進捗を表示してからユーザーに内容を提示し、承認を得ること
  PROHIBITED: 承認前に次ステップへ進むこと

IF HAS_FRONTEND == true:
  STEP 3: designer ← 省略禁止・planner より先に実施すること
    a. READ {SKILL_DIR}/agents/designer.md → メインClaude自身が「テンプレート: デザインブリーフ」に従い実行する → .craft/docs/design-brief.md
    b. 同様に「テンプレート: デザインシステム」に従い実行する → .craft/docs/design-system.md
    c. 画面構成・コンポーネント構成を .craft/docs/design.md に記録
       INCLUDE: 画面遷移（どの画面からどの画面へ・何をトリガーに遷移するか）を
                表または箇条書きで明記すること（例: 一覧画面 → [詳細を開く] → 詳細画面）
                → 基本設計書の画面遷移図はこの記録を元に生成する
       IMPORTANT: design-brief.md に「UI の型と対象」がある場合、画面構成はその型に従って書く。
                  OOUI なら、画面は「対象の一覧／対象の詳細」を単位にし、操作は詳細画面内に置く。
                  新規作成は一覧から行う。手順型にした作成（登録ウィザード等）は、design.md に
                  「手順型の画面」の節を設けて書き、遷移も併記する。
                  ダッシュボード等の集約画面は、対象ではなく集約画面として書く（下記の確認項目に従う）。
                  「UI の型と対象」が無い場合は、下記の確認項目だけに従って書く。
                  画面が1つの場合、画面遷移と戻る導線は「なし」と書いてよい
       IMPORTANT: 画面構成を記録する際、以下の情報設計上のよくある抜け漏れを確認し、
                  該当する場合は対応方針をdesign.mdに明記すること（実装後の手戻りが大きいため
                  実装前のこの時点で確認する）:
                  - 複数の状態・件数を集約する画面（ダッシュボード・管理画面等）は、対象データの
                    生一覧をそのまま表示するのではなく、件数サマリー＋クリックでフィルタ済み
                    一覧へドリルダウンする構成を優先する
                  - 全ての画面遷移について、前進導線（新規作成・詳細を開く等）だけでなく
                    戻る導線（パンくず・戻るボタン・一覧へ戻るリンク等）も併記されているか確認する
                  - 詳細画面で長文表示される自由記述フィールド（説明・備考等）を一覧画面にも
                    表示する場合、そのまま流用せず一覧表示用の短い要約/タイトル用フィールドを
                    別に設ける
                  - 添付ファイル・画像を一覧/詳細画面に表示する場合、サムネイル表示＋クリックで
                    モーダル（ライトボックス）拡大表示を標準パターンとする（新規タブでの
                    表示のみにしない）

    ASSERT EXISTS(.craft/docs/design-brief.md)
    ASSERT EXISTS(.craft/docs/design-system.md)
    ASSERT EXISTS(.craft/docs/design.md)

    c2. 主要画面のワイヤーフレーム生成（省略禁止）:
       .craft/docs/design.md の画面一覧から、ユーザーが最も長く滞在する主要画面を1〜2枚選び（design-brief.md に「UI の型と対象」があり OOUI の場合は、対象の一覧と詳細から選ぶ）、
       design-system.md のトークン（実際の色・タイポ）を使ったラフなレイアウトHTMLを作成する。
       IMPORTANT: 高精細なモックアップではなく、レイアウトの骨格（ヘッダー・ナビ・主要コンポーネントの
       配置）が伝わる粒度でよい。作り込みすぎない（1画面あたり実装時間5分以内を目安にする）
       出力先: .craft/review/extras/wireframe.html

    d. プレビュー生成（共通ルール参照）:
       {SKILL_DIR}/flows/new-project/templates/review/design-system.html を .craft/review/gates/04-design.html に
       コピーし、.craft/docs/design-brief.md・.craft/docs/design-system.md の実際の値で置き換える
       （節の構成と並びは固定。カラーパレット（実際のスウォッチ）・タイポグラフィスケール・
       ブランドアーキタイプ・FEEL/ANTI-FEELワードが含まれる。補足は「7 補足」に書く）
         - ライト/ダーク両テーマに対応する場合、実際に切り替えて確認できるボタンをプレビュー右上に
           設置すること（例: `<html data-theme="light">` をJSでトグルする）。
           「両テーマに対応」と文書だけに書いて実物を見せない状態を禁止する
         - 治療は実務資料（memo/plan相当）: 誇張したヒーロー等は避け、パレット・タイポの実物大提示を主目的にする
       出力先: .craft/review/gates/04-design.html

    c3. 画面モック生成（省略禁止）:
       preview-generation.md の「画面モックの作り方」に従い、主要画面を操作できる実寸モックにする。
       アプリの種類（Web ページ型 / ウィンドウ型）に合う骨組みを、preview-generation.md の
       「画面モックの作り方」から選んで .craft/review/gates/03-mock.html にコピーし、
       design-system.md の実トークン・design.md の主要画面・ダミーデータで置き換える。
       画面の見た目を画像で貼らない（HTML/CSSで組む）
       出力先: .craft/review/gates/03-mock.html

    GATE: 承認進捗を表示してからユーザーに提示し、承認を得ること（03-mock.html と 04-design.html を
          提示する。wireframe.html は補助資料として `review_index.py extra` でメニューに載せる）
    PROHIBITED: デザイン承認前にコンポーネントを1行も書くこと
    NOTE: デザインによってAPIの形・DBフィールドが変わる場合があるため、planner より前に確定させること
ELSE:
  STEP 3 をスキップし STEP 4 へ進む（design-brief.md・design-system.md・design.md は生成しない）
  確認用ページでは、03 と 04 を「UI なし」で対象外（`skip`）にする。API・CLI の使い方は補助資料 `usage`（利用イメージ）として、STEP 4 の後に作る（下記）
ENDIF

STEP 4: planner ← 基本設計を含む場合、このGATEが実質的な基本設計承認になる（DBスキーマ・API設計・セキュリティ設計を含む）
  INPUT:  .craft/docs/stories.md（+ .craft/docs/design-brief.md・.craft/docs/design.md があれば）
  OUTPUT: .craft/docs/plan.md
  ASSERT EXISTS(.craft/docs/plan.md)
  NOTE: 呼び出し前に「planner へ渡すべき設計判断の確認事項」を参照し、ユーザーに確認すること
        → READ {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md
        IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/new-project/recipes/planner-checklist.md" → STOP

  プレビュー生成（共通ルール参照）:
    python3 -I {SKILL_DIR}/flows/new-project/scripts/md2html.py .craft/review/gates/05-plan.html 実装計画 .craft/docs/plan.md
    （plan.md の章立てを、そのまま共通の見た目で出す。これを固定の土台にする）。
    plan.md に書かれた mermaid の図（システム構成図・コンテナ構成図・画面遷移図など）は、変換スクリプトが自動で描画する。
    次の図解は、plan.md に図が無い場合や、図で補いたい場合だけ、該当する節の近くに追記する:

    （「基本設計」セクションがある場合の追加提示。下記フィーチャートラックの有無とは独立に判定する）
    IF 「基本設計」セクションがある:
      DBスキーマ設計（テーブル一覧・リレーション）・API設計（エンドポイント一覧）・
      画面遷移図（ボックス＋矢印）・セキュリティ設計（脅威と対策）を提示する
    ENDIF

    IF 「インフラ構成」セクションがある（本番クラウド公開を伴う場合）:
      mermaid flowchart でシステム構成図を描く。各ノードはクラウドサービス名を主体とし、
      利用者・フロントエンド配信・認証・API/実行基盤・データストアの関係をデータフローの
      矢印でつなぐ（参考: 認証はどこで発行され、どこで検証されるか。認可判定はどの層で行うか）。
      各ノードの直下または横に、そのサービスの役割を1行で添える（例:「Cloud Run — 認可・API処理」）。
      色分け・サブグラフ（フロントエンド配信／認証／API・データ の3系統程度）で見やすくする。
      CDN失敗時のフォールバックとして、図の下に「インフラ構成」節の元テキストを併記する
      （preview-generation.md のCDN利用方針に従う）。
    ENDIF

    IF 「開発ランタイム」節に「コンテナ構成図」がある（Dockerを使う場合）:
      mermaid flowchartをそのまま描画対象に含める。各サービスの役割（app・db等）が
      一目でわかるよう、ノードの直下または横に短い説明を添える。
      CDN失敗時のフォールバックとして、図の下に元のmermaidソースを併記する
      （preview-generation.md のCDN利用方針に従う）。
    ENDIF

    IF 「フィーチャートラック設計」セクションがある:
      レビュートラック(A/B/C)バッジ・フェーズ1(クリティカルパス)の手順（番号付き縦リスト）・
      フェーズ2の並列トラック（カード形式・トラックごとに色分け）とその担当ファイル範囲・
      フェーズ1→フェーズ2への依存関係の分岐線を図解する
    ELSE:
      レビュートラック・実装ステップ・使用ライブラリ・リスクを整理して提示する
    ENDIF

    - 治療は実務資料（plan相当）: 図解による理解のしやすさを優先し、誇張した装飾は避ける
    出力先: .craft/review/gates/05-plan.html

    IF HAS_FRONTEND == false:
      利用イメージ（補助資料 `usage`）を作る: plan.md の API・CLI の設計から、実際に使う様子を HTML にまとめる。
        - API: エンドポイントごとのリクエストとレスポンスの例（`curl` の実行例を含む。正常系とエラーの両方）
        - CLI: 主要なコマンドと、その出力例
        - 画像でなく HTML/CSS（ターミナル風の等幅表示）で作る。ダミーデータは実在の情報にしない
      出力先: .craft/review/extras/usage.html（`review_index.py extra` で `usage`・タイトル「利用イメージ」として登録する。承認ゲートではない）
      ワイヤーフレームは作らない
    ENDIF

  GATE: 承認進捗を表示してからユーザーに計画を提示し、承認を得ること（UI なしの場合は、補助資料の利用イメージも一緒に提示する）
    この承認は、統合設計書の自動生成と実装の開始（STEP 6・7）に進む合意を兼ねる。提示時にその旨を一言添えること
    NOTE: DB・API・認証を伴う場合、ここでDBスキーマ・API設計・セキュリティ設計が確定する。
          以降のSTEP6は、この内容を文書として整形するのみで新たな設計判断は行わない。
  PROHIBITED: 承認前に実装を開始すること

STEP 5: 理解度チェック（Early Stop）← 統合設計書生成前の確認ゲート

  REPEAT:
    SELF_EVALUATE: 以下の5項目を 1〜5 で採点する
      スケール: 1=全く不明 / 2=断片的 / 3=概ね把握 / 4=ほぼ確信 / 5=完全に理解

      | # | 評価項目                                                 | スコア |
      |---|----------------------------------------------------------|--------|
      | 1 | 目的・ゴール（何を達成するプロジェクトか）                |        |
      | 2 | ユーザー・利用シーン（誰が・どう使うか）                  |        |
      | 3 | 主要機能・要件（何を作るか、スコープの境界線）            |        |
      | 4 | 技術的制約・設計判断（認証・DB・API など後から変えにくい部分）|     |
      | 5 | 完了条件・受け入れ基準（何をもって完成とするか）          |        |

    IF ANY(score < 4):
      ASK USER: スコアが4未満の項目について不明点を質問する
      回答により plan.md の「基本設計」または要件が変わる場合は、STEP 4 に戻って planner に反映させ、再承認を得る。
      変わらない場合は、そのまま次へ進む
    ENDIF
  UNTIL ALL(score >= 4)

STEP 6: 統合設計書生成 ← 承認ゲートなし（自動生成と確認用ページのみ）

  目的: STEP 1〜4で既に承認済みの要求・要件・基本設計（DBスキーマ・API設計・
       セキュリティ設計・画面遷移を含む）を1つの整合した文書群として出力する。
       開発の入力として、設計内容を1か所で参照できる状態にする（承認は STEP 4 で済んでいる）。
  IMPORTANT: このSTEPで新たな設計判断を行わないこと。plan.md の「基本設計」セクションに
       ない内容（DBスキーマ・API設計等）が必要になった場合は、STEP4に戻って
       planner に追記させ、再承認を得ること。

  READ {SKILL_DIR}/flows/new-project/templates.md  ← 3つのテンプレートが定義されている（SKILL_DIR はファイル先頭で定義済み）
  IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/new-project/templates.md" → STOP

  生成する3文書:
    a. templates.md の「テンプレート: 要求定義書」を参照 → .craft/docs/01_requirements_doc.md
       入力: .craft/docs/requirements.md
    b. templates.md の「テンプレート: 要件定義書」を参照 → .craft/docs/02_specifications_doc.md
       入力: .craft/docs/stories.md
    c. templates.md の「テンプレート: 基本設計書」を参照 → .craft/docs/03_basic_design_doc.md
       入力: .craft/docs/plan.md の「基本設計」セクション（DBスキーマ・API設計・画面遷移図・
       セキュリティ設計を転記するのみ）+ design-system.md があれば

  ASSERT EXISTS(.craft/docs/01_requirements_doc.md)
  ASSERT EXISTS(.craft/docs/02_specifications_doc.md)
  ASSERT EXISTS(.craft/docs/03_basic_design_doc.md)

  承認ゲートは設けない。3文書は、既に承認した STEP 1〜4 の内容の転記であり、新しい情報がないため
  （承認を取ると、確認の手間に対して、得られるものが少ない）。
  ただし、読みやすく確認できるよう、3文書を1枚にまとめた確認用ページを出す（承認は求めない）:
    python3 -I {SKILL_DIR}/flows/new-project/scripts/md2html.py .craft/review/gates/06-spec.html 統合設計書 \
      .craft/docs/01_requirements_doc.md .craft/docs/02_specifications_doc.md .craft/docs/03_basic_design_doc.md
    その後、`review_index.py set .craft/review/index.html spec "要求・要件・基本設計(確認のみ。承認は不要)"` で、
    メニューの 06 を「ページあり」にする。
  生成後に、3文書の場所（.craft/docs/）と、確認用ページ（.craft/review/index.html の 06）を一言知らせて、STEP 7 へ進む。
  PROHIBITED: 生成物への承認ゲートの要求（確認用ページを出すことは禁止しない。矛盾の報告と確認は除く。下記 NOTE に従う）
  NOTE: 文書の内容に矛盾が見つかった場合は、承認済みの元ドキュメントを自分で書き換えず、矛盾の内容と修正案を
        ユーザーに報告して確認を得る。確認後に、該当する元ドキュメント（requirements.md 等）を修正してから再生成する

STEP 7: build フローへ委譲

  READ .craft/docs/plan.md の「開発ランタイム」節の STACK識別子
  IF 見つからない（旧形式のplan.md等）:
    WARN: "「開発ランタイム」節にSTACK識別子が見つかりません。デフォルトの node を使用します。"
    SET STACK = "node"
  ELSE:
    SET STACK = plan.mdに記載のSTACK識別子

  READ {SKILL_DIR}/flows/build/SKILL.md
  IF READ FAILED: REPORT "フローファイルが見つかりません: {SKILL_DIR}/flows/build/SKILL.md" → STOP
  FOLLOW: そこに記述されたすべての手順を実行する
    STACK = <上記で確定した値>
    HAS_REVIEW_CHAIN = true
    HAS_FRONTEND = <このチェーン冒頭で設定済みの変数>

  NOTE: 実装（フェーズ1〜3 or シンプルループ）・designerによる実画面レビュー・
        /ultrareview・レビューチェーン（構成は plan.mdのレビュートラックと build フローに従う）・
        CLAUDE.md/README.md生成は build フロー側で実行される。
```

---

## オプションエージェント（必要に応じて追加）

| エージェント | 用途 |
|-------------|------|
| `ideator` | 何を作るか決まっていないときのアイデア探索 |
| `debugger` | 複雑なデバッグ（エラーの根本原因特定） |
| `tester` | テストコードの自動実装 |
| `scorer` | コードベース健全性の定期評価 |

---

## Node.js / Webアプリ固有の再開時注意点

汎用の実装フロー（初回実装・再開共通）は `{SKILL_DIR}/flows/build/SKILL.md` に定義されている。
Node.js 系プロジェクトで再開する際は以下を追加で確認すること。

```
- .env ファイルが存在するか確認する:
    存在しない → .env.example をもとに作成が必要かユーザーに確認する
- DBマイグレーション状態を確認する:
    `pnpm db:migrate` 等のマイグレーションコマンドが未実行でないか確認する
    スキーマと実際のDBがずれている場合はマイグレーションを先に実行する
- ビルド確認コマンドは `mise exec -- pnpm build` を使う
- `node_modules/` が存在しない場合は `mise exec -- pnpm install` を先に実行する
```

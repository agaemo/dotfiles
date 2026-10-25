# プレビュー生成（共通ルール）

craft の new-project・new-app フロー（agent-chain.md）・new-static フローの各GATE（design-brief・plan.md。統合設計書は承認ゲートなしで、確認用ページだけ出す）で、承認前にローカルHTMLで確認用ページを生成する際の共通手順。メインClaudeが行う。呼び出し元のSTEPからは、このファイルをプレビュー生成チェーン中に未読の場合のみ読み込み（セッションが変わった場合は再度READする）、対象ファイル・図解内容の差分のみを実行すること。

## Artifact を使わない理由

Artifact は外部ホストへのリクエストが厳格にブロックされる（CSP制約）ため使用しない。ローカルHTMLファイルとして出力する。

## CDN（外部ライブラリ）の利用方針

- 装飾目的（Webフォント等、見た目の向上のみに関わるもの）でのCDN利用は許容する
- 図解目的（mermaid.js・PlantUML等によるER図・シーケンス図・画面遷移図）でのCDN利用も許容する。
  ただし以下を満たすこと:
  - `<script>` 読み込み失敗時のフォールバック（例: 図の直下に元のテキスト表現やMarkdownソースを
    `<pre>` で併記する）を必ず用意し、オフライン時も内容確認ができる状態を維持する
  - 生成直後にメインClaudeが実際にブラウザで開き、図が描画されていることを目視確認する
    （CDN失敗時にフォールバックへ切り替わっているかもここで確認する）
- 上記いずれでもない自作のボックス＋矢印によるSVG/CSS図解も、要件が単純な場合は
  引き続き選択肢とする（画面遷移図が3〜4ステップ程度など、mermaidを使うまでもない場合）

## テーマ対応プレビューの共通ルール

「ライト/ダーク両テーマに対応」等、対象文書が複数の見た目パターンを持つ場合、
プレビューHTML側に実際に切り替えられるUIを必ず設置すること（記述のみで済ませない）。

## 出力先の構成（.craft/review/）

確認用ページは `.craft/review/` にまとめ、入口を `index.html`（左メニュー＋iframe）の1つにする。
承認ゲートは**6つの固定スロット**で、番号・ファイル名・タイトルは変えない（成果物として揃えるため）。補助資料は自由に追加・削除できる。

| 番号 | id | ファイル | タイトル | 元の文書 | 出す条件 |
|---|---|---|---|---|---|
| 01 | requirements | `gates/01-requirements.html` | 要件定義 | `requirements.md` | 常に |
| 02 | stories | `gates/02-stories.html` | ユーザーストーリー | `stories.md` | 常に |
| 03 | mock | `gates/03-mock.html` | 画面モック | `design.md`・`design-system.md` | UI あり。UI なしは対象外（`skip`。下記） |
| 04 | design | `gates/04-design.html` | デザインシステム | `design-brief.md`・`design-system.md` | UI あり。UI なしは対象外 |
| 05 | plan | `gates/05-plan.html` | 実装計画 | `plan.md`（基本設計・テスト・リスクを含む） | 常に |
| 06 | spec | `gates/06-spec.html` | 統合設計書 | `01_`〜`03_` の3文書 | 常に（承認は求めない。確認のみ） |

```
.craft/review/
  index.html       入口。メニューは scripts/review_index.py で更新する
  gates/           上の6スロット
  extras/          補助資料（自由。ファイル名は <名前>.html）
```

- メニューには6スロットを常に並べ、状態を3つで示す: ページあり（リンク）/ 対象外（灰色。理由つき）/ 未作成（灰色）。欠番にして番号を詰めない。メニューの番号は、ファイル名の番号と同じ。
- UI なしの案件: 03 と 04 は「対象外（UI なし）」で `skip` にする（画面がないので画面モックは出さない。ゲートのタイトルは書き換えない）。API・CLI の使い方を見せたいときは、承認ゲートではなく補助資料 `usage`（`extras/usage.html`、タイトル「利用イメージ」）として出す。API なら、リクエストとレスポンスの例（`curl` の実行例を含む）、CLI なら、コマンドと出力例を、HTML にまとめる。内容は plan.md の API・CLI の設計から作り、05 の承認ゲートで一緒に提示する（planner の後に作る。承認の対象ではない）。ワイヤーフレームは作らない。
- 補助資料の例（推奨）: `wireframe`（UI あり）、`tech`（技術調査。`tech-research.md`）、`icon`（アイコン案）、`adr`（設計判断の記録）。増減は自由で、承認の対象ではない。
- `.craft/review/` 以外（旧 `.craft/previews/` 等）には出力しない。

### 各ページの作り方（形式は固定）

| 番号 | 作り方 | 形式を決めているもの |
|---|---|---|
| 01 要件定義 | `md2html.py`（`requirements.md` を変換） | requirements.md の章立て（intake.md のテンプレート） |
| 02 ストーリー | `md2html.py`（`stories.md` を変換。US をカード、疑問を回答済み/未回答で区別） | stories.md の書式（refiner.md） |
| 03 画面モック | 骨組み（Web 型 / ウィンドウ型）をコピーして置き換える。UI なしは作らない（`skip`） | 骨組みの HTML |
| 04 デザインシステム | `templates/review/design-system.html` をコピーして置き換える | 雛形の節構成（7節。並びは変えない） |
| 05 実装計画 | `md2html.py`（`plan.md` を変換）+ 必要な図解の追記 | plan.md の章立て（planner.md） |
| 06 統合設計書 | `md2html.py`（3文書を連結） | 3文書のテンプレート（templates.md） |

- 内容の追加は自由。md に節を足すか（01・02・05・06）、雛形の「7 補足」に書く（04）。節の構成と並びは変えない。
- ページの HTML を、毎回ゼロから手で書かない。

## index.html の生成と更新

メニュー（`index.html` の `PROJECT`・`PAGES`）は、手で書き換えず、更新スクリプトで操作する。
`{SCRIPT}` = `python3 -I {SKILL_DIR}/flows/new-project/scripts/review_index.py`、`{INDEX}` = `.craft/review/index.html`

1. 初回: `{SCRIPT} init {INDEX} <プロジェクト名>`（雛形をコピーし、6スロットを「未作成」で作る。既にあれば何もしない）。
2. ページを保存するたびに: `{SCRIPT} set {INDEX} <スロットid> [補足 [タイトル]]`
   （ゲートのタイトルは変えないので、通常はタイトルを指定しない。ファイルが無いと失敗する）。
3. 対象外のスロット: `{SCRIPT} skip {INDEX} <スロットid> <理由>`（例: `skip {INDEX} design "UI なし"`）。
   UI なしの案件では、承認ゲートの最初（STEP 1 の保存時）に `design` を対象外にしておく。
4. 補助資料: `{SCRIPT} extra {INDEX} <id> extras/<名前>.html <タイトル> [補足]`、消すときは `{SCRIPT} remove {INDEX} <id>`。
   現在の状態は `{SCRIPT} list {INDEX}`。
5. 各ページには戻りリンクを入れる。`<body>` の直後に `<p id="back-nav"><a href="../index.html">&larr; 一覧へ</a></p>`、`</body>` の直前に
   `<script>if(window.top!==window){var b=document.getElementById("back-nav");if(b)b.hidden=true;}</script>`
   を置く（iframe の中では隠れ、単体で開いたときだけ出る）。Markdown 変換スクリプトの出力には入っている。
6. ユーザーへは `.craft/review/index.html` を開いて提示する（`#mock` のように hash で該当ページを指定できる）。
7. テーマ切替は各ページ内のボタンで行う（`file://` では iframe の中身を外から変えられない）。

## 画面モックの作り方

UI のある案件では、承認ゲートに操作できる画面モック（`gates/03-mock.html`）を出す。

- 画面は画像（PNG・スクリーンショット・貼り付けた図）にしない。HTML/CSS で実寸に近い大きさで組み、ダミーデータを入れる。
- 骨組みは種類で選び、`.craft/review/gates/03-mock.html` にコピーして置き換える。色・書体・寸法は `design-system.md` の実トークンを使う。
  - Web ページ型（ブラウザで開く Web アプリ・サイト）: `{SKILL_DIR}/flows/new-project/templates/review/mock-skeleton-web.html`（一覧と詳細の2画面。追加フォーム・検索・状態変更・明細の追加と削除・削除ダイアログ・空状態。ハッシュで画面を切り替える。画面が1つなら詳細を消す）
  - ウィンドウ型（デスクトップアプリ・常駐ツール）: `{SKILL_DIR}/flows/new-project/templates/review/mock-skeleton.html`（小型ウィンドウ、キー操作、設定の折りたたみ）
  - どちらも合わない画面は、骨組みのテーマ切替・戻りリンク・確認ダイアログの型だけ借りて、画面を HTML/CSS で組む。
- 動かすのは、その画面の主要な操作だけでよい（一覧の選択、検索の絞り込み、開閉、確認ダイアログなど。キー操作が中心のアプリはキーボードも）。全画面・全操作は作り込まない。
- ダミーデータは実在の情報にしない。ページの冒頭に「表示している内容はサンプル」と書く。

## Markdown からの変換スクリプト

Markdown 主体の文書（要件定義・ストーリー・plan.md 等）は、毎回HTMLを手で書かず、同梱のスクリプトで変換する。
標準ライブラリだけで動く（見出し・箇条書き・表・コード・強調・リンク・左のセクションナビ）。

```
python3 -I {SKILL_DIR}/flows/new-project/scripts/md2html.py <出力パス> <タイトル> <Markdown...>
```

- 複数のMarkdownを渡すと、1枚のHTMLにまとめる（ファイルごとに章として並べる）。
- デザイン（04）は、変換せず、雛形（templates/review/design-system.html）をコピーして置き換える。
- md の中の mermaid（```mermaid / ~~~mermaid）は、変換スクリプトが図として描画する（CDN の mermaid を使い、読み込めない・描画できないときは、注意書きと図のソースを表示する）。md に書いた図は、HTML に追記しなくてよい。
  - mermaid を書くときの注意: 図の記法は、図のソースに書く。エッジのラベルに括弧や記号を含むときは `|"ラベル(任意)"|` のように引用符で囲む（スクリプトも、構文エラーのときに自動で引用符を付けて再試行する）。ノードの文言も、括弧を含むなら `["…"]` で囲む。
  - md に書けない図（独自の図解）が必要な場合だけ、変換後の HTML に追記する（上記のCDN方針に従う）。

## 手順

呼び出し元STEPが示す「出力先: <パス>」の値を、以下の `<出力パス>` として使う。
対象ファイルが複数の場合も、呼び出し元の指示に従い単一のHTMLにまとめる。
保存後は「index.html の生成と更新」を行う。

```
Skill ツールで artifact-design を読み込んでから作成する
<対象Markdownファイル（複数の場合は呼び出し元の指示に従い1枚に統合）> の内容から確認用HTMLを作成する
  [各STEP固有の図解内容・レイアウトは呼び出し元STEPの指示に従う]
WRITE <出力パス>
ASSERT EXISTS(<出力パス>)
IF NOT EXISTS:
  REPORT: "プレビューHTMLの生成に失敗しました。内容確認は元のMarkdownファイルで行いますか、再試行しますか？"
  WAIT_FOR: ユーザーの判断
  IF 再試行: 最初からやり直す
  ELSE: 元のMarkdownファイルのパスを伝えて次に進む（プレビュー確認はスキップ）
ELSE:
  <出力パス> のパスをユーザーに伝える。
  ローカル環境でブラウザを自動起動できる場合（例: macOSの `open` コマンド）はメインClaudeが実行し、
  できない場合はパスのみ伝えてユーザー自身に開いてもらう
ENDIF
```

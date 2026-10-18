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

```
.craft/review/
  index.html            入口。雛形から作り、メニューは PAGES 配列で定義する
  gates/                承認ゲートの資料。メニューの順に番号を付ける
    01-requirements.html  02-stories.html  03-mock.html  04-design.html  05-plan.html  06-spec.html（統合設計書）
  extras/               補助資料（承認ゲートではないもの）
    wireframe.html  icon.html など
```

- 番号は枠として固定する。その案件で作らないページは欠番のままにし、PAGES 配列からも消す（例: HAS_FRONTEND == false なら 03・04 は無い）。
- 承認ゲートでない資料（ワイヤー、アイコン案など）は `extras/` に置き、PAGES では `group: "extra"` にする。
- 06-spec.html（統合設計書）はメニューの承認ゲート欄に載せるが、承認は求めない（確認のみ。補足にそう書く）。作り方は agent-chain.md の STEP 6。
- `.craft/review/` 以外（旧 `.craft/previews/` 等）には出力しない。

## index.html の生成と更新

メニュー（`index.html` の `PROJECT`・`PAGES`）は、手で書き換えず、更新スクリプトで操作する。
`{SCRIPT}` = `python3 -I {SKILL_DIR}/flows/new-project/scripts/review_index.py`

1. 初回: `{SCRIPT} init .craft/review/index.html <プロジェクト名>`（雛形をコピーする。既にあれば何もしない）。
2. ページを保存するたびに: `{SCRIPT} set .craft/review/index.html <id> <file> <gate|extra> <タイトル> [補足]`
   （`<file>` は `index.html` からの相対パス。ファイルが無いと失敗する。同じ id は置き換わる。
   並びは、承認ゲートと補助資料をそれぞれファイル名の順にそろえる）。
   作らないことにしたページは `{SCRIPT} remove .craft/review/index.html <id>`、確認は `{SCRIPT} list .craft/review/index.html`。
   id の例: requirements / stories / mock / design / plan / spec / wireframe / icon。
3. 各ページには戻りリンクを入れる。`<body>` の直後に `<p id="back-nav"><a href="../index.html">&larr; 一覧へ</a></p>`、`</body>` の直前に
   `<script>if(window.top!==window){var b=document.getElementById("back-nav");if(b)b.hidden=true;}</script>`
   を置く（iframe の中では隠れ、単体で開いたときだけ出る）。Markdown 変換スクリプトの出力には入っている。
4. ユーザーへは `.craft/review/index.html` を開いて提示する（`#mock` のように hash で該当ページを指定できる）。
5. テーマ切替は各ページ内のボタンで行う（`file://` では iframe の中身を外から変えられない）。

## 画面モックの作り方

UI のある案件では、承認ゲートに操作できる画面モック（`gates/03-mock.html`）を出す。

- 画面は画像（PNG・スクリーンショット・貼り付けた図）にしない。HTML/CSS で実寸に近い大きさで組み、ダミーデータを入れる。
- 骨組みは種類で選び、`.craft/review/gates/03-mock.html` にコピーして置き換える。色・書体・寸法は `design-system.md` の実トークンを使う。
  - Web ページ型（ブラウザで開く Web アプリ・サイト）: `{SKILL_DIR}/flows/new-project/templates/review/mock-skeleton-web.html`（追加フォーム・検索・一覧・削除ダイアログ・空状態）
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
- デザインのプレビュー（色・フォント・レイアウトの見た目）は、変換せず、手で書く。
- 図解（mermaid等）が必要な場合は、変換後のHTMLに追記する（上記のCDN方針に従う）。

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

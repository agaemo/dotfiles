# 図解・HTML詳細（output-briefから参照）

出力形式がHTML、または図解（Mermaid/viz-*）を含める場合にのみ読む。CSV/JSON/プレーンMarkdownでは不要。

## 図解を含める場合

**HTML出力の場合、まず `$SKILL_DIR/assets/component-library.html` の viz-*コンポーネント（外部ライブラリ不使用・CSS/HTML/インラインSVGのみ）で代替できないか検討する。保存先を問わず（Artifact公開でもファイル保存でも）こちらを優先する:**

| 図の種類 | 代替コンポーネント |
|---|---|
| 線形フロー | `.flow`/`.flow-step`/`.flow-arrow`（既存）または 9番の分岐パターンを直線に簡略化 |
| 条件分岐（if/else） | component-library.html 9番（`.viz-diagram` + SVG） |
| シーケンス図 | component-library.html 10番 |
| 階層・組織図 | component-library.html 11番（`.viz-tree`、ネストした`<ul>`） |
| 状態遷移図 | component-library.html 12番 |
| ガントチャート | component-library.html 13番（`.viz-gantt`） |
| 画面遷移図 | component-library.html 14番 |
| クラス図（UML） | component-library.html 15番 |
| ER図（エンティティ関連図） | component-library.html 16番 |
| ユースケース図（UML） | component-library.html 17番 |
| アクティビティ図（UML） | component-library.html 18番 |
| コンポーネント図（UML） | component-library.html 19番 |

`Read` で component-library.html を参照し、該当するSVG/HTMLパターンをコピーして、ノード・ラベル・座標を内容に合わせて調整する。クラスは `viz-` 名前空間なのでレイアウトサンプルの既存クラスと衝突しない。CSS変数（--accent 等）を通じて選択済みのカラーテーマに自動追従するため色指定は不要。

**上記でカバーできない図（クラス図・ER図・複雑な依存関係グラフ等）が必要な場合、またはMarkdown出力の場合のみ**、以下の通りMermaidを検討する:

IF 保存先が「Artifactとして公開」を含む:
  **PROHIBITED: MermaidのCDN読み込み（`<script src="https://cdn.jsdelivr.net/...">`）を使うこと。**
  理由: SKILL.md Step4のArtifact外部CDN禁止ルールに同じ（CSPでブロックされ、同じ`<script>`ブロック内の他の初期化コードも巻き添えで止まる）。
  viz-*コンポーネントでも表現できない図が必要な場合は、Mermaid図を諦めるかArtifact公開を諦めるかをユーザーに確認する。
ELSE:
  - **HTML**: `<head>` に `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>` を追加し、本文に `<div class="mermaid">...</div>` で図を記述する。出力用 `<script>` に `mermaid.initialize({startOnLoad:true, theme:'neutral'})` を含める。
  - **Markdown**: ` ```mermaid ` フェンスドコードブロックで記述する（GitHub/GitLab 等のビューアでネイティブ表示される）。Markdown出力ではviz-*コンポーネント（HTML/CSS）が使えないため、図解が必要な場合は常にMermaidを使う。
  - 図の種類（flowchart / sequenceDiagram / classDiagram 等）は内容に応じて選択する。
  - **quadrantChart の文字エンコーディング**: title・axis・quadrant・ポイント名に日本語等のUnicode文字を使う場合はダブルクォートで囲む（`"テキスト"`）。囲まないと `Syntax error in text` になる（flowchart 等の他の図種では不要）。
  - **HTML でのキャプション**: 図の読み方や補足を添える場合は `<div class="mermaid">` の直後に `<span class="mermaid-caption">補足テキスト</span>` を置く。CSS は全テーマに組み込み済み。

## HTML の場合

レイアウト選択 → カラー選択の **2 段階** で行う。

**ステップ 2-1: レイアウト選択**

まず各レイアウトのプレビュー画像（`light` カラー）を `Read` ツールで読み込んで表示し、視覚的にイメージを伝える:
- `$SKILL_DIR/assets/previews/simple-list-light.png`
- `$SKILL_DIR/assets/previews/panel-light.png`
- `$SKILL_DIR/assets/previews/article-light.png`
- `$SKILL_DIR/assets/previews/table-light.png`
- `$SKILL_DIR/assets/previews/slide-light.png`
IF 画像が読み込めない場合は表示をスキップし、テキストでレイアウトの特徴を説明する。

次に番号リストでレイアウトを選んでもらう:
- `simple-list` — 一覧・縦。テキスト中心・情報量が多いコンテンツ向き
- `panel` — 一覧・カード。同程度の重要度の項目を視覚的に並べる向き
- `article` — 文書。見出し・本文・コード・引用など Markdown 的な構造向き
- `table` — 表。複数項目を列で比較するデータ表向き
- `slide` — プレゼン資料。1セクション1枚の枠付きカードを横スクロール（矢印キー可）で送るスライド形式。全画面表示トグル（Fキー / 右上ボタン）付き。提案・報告・ピッチ向き

**ステップ 2-2: カラー選択**

レイアウトが決まったら、ステップ2-1で選択した layout 値を `<layout>` に代入して全 6 色プレビューを `Read` ツールで読み込んで表示する:
- `$SKILL_DIR/assets/previews/<layout>-warm.png`
- `$SKILL_DIR/assets/previews/<layout>-cool.png`
- `$SKILL_DIR/assets/previews/<layout>-blue.png`
- `$SKILL_DIR/assets/previews/<layout>-green.png`
- `$SKILL_DIR/assets/previews/<layout>-dark.png`
- `$SKILL_DIR/assets/previews/<layout>-light.png`
IF 画像が読み込めない場合は表示をスキップし、テキストでカラーテーマの特徴を説明する。

次に番号リストで6色すべてを一度に提示してカラーテーマを選んでもらう:
```
[1]: warm — オレンジ・ベージュ。温かみがある
[2]: cool — パープル・ラベンダー。落ち着いた印象
[3]: blue — 青系。清潔感・信頼感
[4]: green — 緑系。自然・安心感
[5]: dark — 暗い背景。モダン・集中感
[6]: light — 白ベース。シンプル・クリーン
```

全 30 種のサンプルは `$SKILL_DIR/assets/samples/<layout>-<color>.html` に保存されている。
`open "$SKILL_DIR/assets/samples/<layout>-<color>.html"` でブラウザから詳細確認できることをユーザーに伝える。

**グラフィック要素（viz-* コンポーネント）**

外部ライブラリ不使用（CSS/HTML/インラインSVGのみ）のグラフィカル要素一式が、全レイアウト・全カラーの `<style>` に組み込み済み（`viz-` 名前空間、既存クラスと衝突しない）。内容に数値・進捗・状態・階層・手順など可視化できる要素が含まれる場合、装飾の追加として使ってよい:

| 種別 | クラス | 用途 |
|---|---|---|
| 統計タイル | `.viz-stat` / `.viz-stat-row` | 数値＋ラベル＋前月比の要約 |
| メーター | `.viz-meter` / `.viz-meter-fill` | 進捗・達成率 |
| ドーナツ | `.viz-donut`（`conic-gradient`） | 単一割合の強調表示 |
| 簡易棒グラフ | `.viz-barchart` | 単系列の比較 |
| スパークライン | `.viz-sparkline`（インラインSVG） | 文中の小さなトレンド表示 |
| 星評価 | `.viz-stars` | 5段階評価 |
| ヒートマップ | `.viz-heatmap` | 強弱のグリッド表示 |
| ステータスバッジ | `.viz-badge-good` / `-warn` / `-crit` | 正常・要確認・エラーの状態表示 |
| 分岐フロー図・シーケンス図・状態遷移図・画面遷移図・クラス図・ER図・ユースケース図・アクティビティ図・コンポーネント図 | `.viz-diagram`（インラインSVG） | Mermaid代替（詳細は上記参照） |
| 階層ツリー | `.viz-tree` | 組織図・カテゴリ階層 |
| ガントチャート風 | `.viz-gantt` | 期間・スケジュール |

具体的なマークアップは `$SKILL_DIR/assets/component-library.html` を `Read` して参照する（全19種のコード例が1ページにまとまっている。9〜19番は図解、詳細な対応表は上記参照）。CSS変数（--accent, --good/--warn/--crit 等）を通じて選択済みのカラーテーマに自動追従するため、コピーする際に色の指定は不要。無理に全種類を使う必要はなく、内容に合うものだけを選ぶ。

**viz-diagram（複数ノードのインラインSVG手描き図）の検証**

分岐フロー・シーケンス・状態遷移・階層ツリー・ガントチャートなど、ノードや矢印を複数含む図は座標を手計算で配置するため、ノード数が増えるほど描画ミス（矢印が対象ノードまで届いていない、要素がviewBox外にはみ出して非表示になる等）が起きやすい。自分の目視確認だけでは「全体が大きく崩れていないか」しか追えず、個々の矢印の接続先までは見逃すことがある。

以下の手順で確認してから完成として扱う:
1. `Bash` + Playwright でレンダリング結果をスクリーンショットする（`/tmp/`配下に一時インストールして実行）。インストールに失敗した場合は、目視確認（座標のみのレビュー）で代替する旨をユーザーに一言添えてから先に進む。
2. `Read` でスクリーンショットを読み込み、矢印が実際に対象ノードへ到達しているか、要素が枠内に収まっているかを1つずつ確認する
3. 問題があれば座標を修正し、1〜2を再実行する
4. 確認後のスクリーンショットをユーザーに提示し、意図通りに表示されているか確認を得る

WAIT_FOR: ユーザーの確認。修正が必要な場合は座標を直して再度提示する。
**PROHIBITED: スクリーンショットで自己確認しただけで「確認済み」とユーザーに報告し、画像を見せずに次に進むこと。**
単純な線形フロー（`.flow`系）やノード1〜2個程度の単純な図はこの限りではない。

**カスタマイズ範囲**

ステップ2-1で選択した layout 値とステップ2-2で選択した color 値を代入した
`$SKILL_DIR/assets/samples/<layout>-<color>.html` を Read してサンプルの構造を参照し、以下の範囲でカスタマイズしてよい:
- フォントファミリー・サイズ・行間
- 余白（padding / margin）
- アイコン・装飾（リストマーカー・ボーダー・シャドウ）
- セクション構成（追加・削除・並び替え）
- グラフィック要素（viz-*コンポーネント）の追加

**PROHIBITED: レイアウト骨格（グリッド・サイドバー有無・ヘッダー構造）を変更すること。**
**PROHIBITED: カラーテーマのパレット（色相・彩度）を大幅に変えること（アクセントカラーの微調整のみ許容）。**

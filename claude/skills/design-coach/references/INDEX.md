# references 索引

必要な分だけ Read する（全部は読まない）。状況の凡例: ◎ 出典を取得して確認済み / ○ 一部確認（詳細は各ファイル冒頭）/ △ 未検証（経験則・私の知識。数値は断定せず「要確認」と添える）

## 情報設計 ia/
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `ia/ooui.md` | 画面構成を対象（名詞）から組み立てる、業務システムの設計 | ○ |
| `ia/task-vs-object.md` | OOUI かタスク指向かの選択、ウィザードとの併用 | ○ |
| `ia/navigation.md` | メニュー・サイドバー・パンくず・現在地 | ◎ |
| `ia/user-flow.md` | 主要タスクの流れの整理、ジャーニーとフロー | ◎ |

## 業務系パターン patterns/
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `patterns/forms.md` | フォーム、検証、ラベル、エラー表示 | ◎ |
| `patterns/tables.md` | 一覧、テーブル、ソート、行選択、一括操作 | ◎（数値は Carbon の例） |
| `patterns/search-filter.md` | 検索ボックス、フィルタ、ファセット | ○ |
| `patterns/wizard.md` | 段階入力の要否と設計 | ◎ |
| `patterns/errors-undo.md` | エラー文言、確認ダイアログ、Undo、フェイルセーフ | ◎ |
| `patterns/empty-states.md` | 0件・初回・エラー時の表示 | ◎ |
| `patterns/permissions-audit.md` | 権限による無効・非表示、監査ログ | △ |
| `patterns/keyboard.md` | キーボード操作、フォーカス、ショートカット | ○ |

## 原理 theory/
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `theory/laws.md` | ヒック、ミラー、ヤコブ、フィッツ、ドハティ | ◎ |
| `theory/gestalt.md` | 近接・共通領域・類似によるグルーピング | ◎ |
| `theory/cognitive-load.md` | 認知負荷、段階的開示 | ◎ |
| `theory/visual-hierarchy.md` | 視覚階層、スクイントテスト | ◎ |
| `theory/heuristics.md` | ニールセンの10原則、画面レビューの観点 | ◎ |

## アクセシビリティ a11y/
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `a11y/wcag.md` | コントラスト、ターゲットサイズ、フォーカス、フォーム、リフロー、テキスト間隔（WCAG 2.2 AA） | ◎（JIS との対応は一部） |
| `a11y/aria.md` | 独自部品の実装方針、ネイティブHTMLと ARIA | ◎ |

## 日本語 ja/ ・視覚 visual/
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `ja/typesetting.md` | 日本語のサイズ・行高・組版（デジタル庁DS の数値） | ○（JLReq は冒頭のみ） |
| `ja/ux-writing.md` | ボタン・エラー・空状態の文言 | △（日本語固有は未検証） |
| `visual/color-theory.md` | OKLCH、パレットの構成、役割と比率 | ◎ |

## システム化・評価・画面種別
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `system/tokens-handoff.md` | トークン、コンポーネント分割、実装への引き渡し | ◎（トークン仕様はドラフト） |
| `process/evaluation.md` | ヒューリスティック評価、ユーザビリティテスト | ◎ |
| `process/measure.md` | 画面の実測（フォント、ターゲット、コントラスト、320px）の手順 | ○（経験則） |
| `recipes/screens.md` | 管理画面・入力画面・ダッシュボード・LP・モバイルの組み合わせ方 | ○ |

## ビジュアル・表現（直下。コントラストとタップ領域以外は未検証）
| ファイル | いつ読むか | 状況 |
|---------|-----------|------|
| `typography.md` | 欧文と和文のフォント選定、スケール | △（サイズ・行高は `ja/typesetting.md` を優先） |
| `color.md` | 配色の実践、ダーク対応 | △（基準値は `a11y/wcag.md`、構成は `visual/color-theory.md`） |
| `spacing-layout.md` | 余白、グリッド、レスポンシブ | △ |
| `expression.md` | LP・ブランドサイトの表現 | △ |
| `business-ui.md` | 業務系の概要（食い違いは `patterns/` が正） | △ |
| `anti-generic.md` | AIっぽさの点検 | △ |
| `brand-system.md` | モチーフ、一貫性 | △ |
| `motion-interaction.md` | 動き（時間は NN/g で確認済み） | ○ |
| `benchmarks.md` | 参考サイトの分解（コクヨの観察例） | ○ |
| `assets-and-limits.md` | できること/できないこと、素材・ライセンス | △ |
| `maintenance.md` | references の追記・修正・出典の扱い（更新時のみ） | - |
| `gaps.md` | 未対応の不足 | - |

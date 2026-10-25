# 画面種別レシピ（どのファイルを組み合わせるか）

確認状況: 新しい主張は置かず、確認済みのファイルの**組み合わせ方**を示す。ダッシュボードのグラフの選び方のみ、NN/g「Dashboards」を取得して確認済み。

## 管理画面・業務システム（SaaS）

1. 構成: `ia/ooui.md` で対象を抽出 → ルートナビを対象中心に（`ia/navigation.md`: 左サイドバー）
2. 一覧: `patterns/tables.md`（先頭列は識別子、有効なフィルタを明示、一括操作）+ `patterns/search-filter.md`
3. 詳細: 対象名と状態を最上部に（`theory/visual-hierarchy.md`）。操作は詳細に。履歴は `patterns/permissions-audit.md`
4. 登録・編集: `patterns/forms.md`（単純ならまとめて1画面、低頻度で複雑ならウィザード `patterns/wizard.md`）
5. 状態: 空・エラー・ローディング・権限なし（`patterns/empty-states.md`、`patterns/errors-undo.md`）
6. 見た目: 文字は `ja/typesetting.md`（Dense スタイル）、色は `visual/color-theory.md` + `a11y/wcag.md`
7. 引き渡し: `system/tokens-handoff.md`

## 入力が主役の画面（申請・登録）

- 1画面にまとめるか、段階にするかは、**頻度と複雑さ**（`patterns/wizard.md`、`theory/cognitive-load.md`）
- 入力済み情報を再入力させない（`a11y/wcag.md` 3.3.7）
- 完了後は、対象の詳細へ（`ia/task-vs-object.md`）

## ダッシュボード

NN/g の整理（取得済み）:
- 目的は、**探索でなく、少ない操作と認知負荷で素早く読み取れる**こと。単一画面で見渡せ、行動につながる情報を載せる
- 運用型（時間的に緊急な判断）と分析型（後で深く検討）を区別する
- 人が素早く知覚する**前注意属性**: 長さ・面積・角度・2D位置・色。**長さと2D位置**が量の比較に最も正確。面積と角度は差は分かるが大きさは正確に分からない。色は順序がなく、数値の大小には向かない
- **推奨**: 棒グラフ、折れ線グラフ、散布図（並べ替えるとさらに比較しやすい）
- **避ける**: 円・ドーナツ（極端な構成比の差を除く）、ツリーマップ（簡潔なダッシュボードには不向き）、ゲージ（バレットグラフが適する）、3D
- 色は数値の大小の主手段にしない。**形や配置を主、色は補強**。色と形の併用で強い信号になる
- 関連する要素は近くに（近接。`theory/gestalt.md`）

実装・配色の詳細は `dataviz` スキルに従う（色の検証、アクセシビリティ）。

## LP・ブランドサイト

- `expression.md`（構成、印象の手法）、`brand-system.md`、`motion-interaction.md`
- 文字: `typography.md`、`ja/typesetting.md`。コントラスト、ターゲットサイズ、フォーカスは `a11y/wcag.md`
- モーション: `prefers-reduced-motion` を尊重（`motion-interaction.md`）、パララックスや自動送りのカルーセルは避ける

## モバイル・レスポンシブ

- 幅 320px で二次元スクロールなし（WCAG 1.4.10。データテーブルなどは例外）
- ターゲットは最低24px、重要な操作は44px（`a11y/wcag.md`）
- ナビ: 大画面では隠さない。小画面のみハンバーガー（`ia/navigation.md`）
- フィッツの法則: タッチでは画面端が有利とは限らない。送信ボタンは入力欄の近くに（`theory/laws.md`）
- 詳細（モバイル固有の操作パターン、プラットフォーム別の指針）は未取得（`gaps.md`）

## 出典

- NN/g「Dashboards: Making Charts and Graphs Easier to Understand」
- 各ファイルの出典を参照

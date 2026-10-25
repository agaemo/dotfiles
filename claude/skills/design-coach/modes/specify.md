# 仕様化モード

決まった方向性を、craft の designer が読めるデザイン仕様ファイルにする。

## 前提

- 方向性が決まっていること（探索モードの選択結果、または相談で確定した内容）。未確定なら探索モードか相談モードに戻る
- 出力先は `.craft/docs/`（なければ作成してよいか確認する。craft プロジェクト外ならユーザーに保存先を聞く）

## 手順

1. 既存ファイルの確認: `.craft/docs/design-brief.md` / `design-system.md` が既にあれば、**上書きしてよいか確認**する。
   WAIT_FOR: ユーザーの回答

2. **craft のテンプレートを Read する**（複製せず、実行時に読む）。見つからなければ、そのパスを示してユーザーに場所を確認する。
   - `$HOME/.claude/skills/craft/agents/templates/design-brief.md`
   - `$HOME/.claude/skills/craft/agents/templates/design-system.md`

3. **design-brief.md を生成**: テンプレートの節構成（1〜8、必要なら9）に沿って記入する。
   - 全ての項目を埋める。不明な項目は推測せずユーザーに聞く（TODOを残さない）
   - 冒頭に `<!-- generated-by: design-coach -->` を入れる
   - 「8. デザインプロとしての懸念・調整事項」に、このスキルで議論したトレードオフを記録する

4. **design-system.md を生成**: テンプレートの節構成に沿って記入する。トークンの命名と引き渡し形式は `references/system/tokens-handoff.md` に従う。
   - カラーはコントラスト比を数値で明記する（本文 4.5:1 以上は必須。`references/color.md` の計算式で確認し、推定値なら推定と書く）
   - スペーシング・タイプスケールは `references/spacing-layout.md` と `typography.md` の既定スケールをベースに、プロダクトに合わせて調整する。本文は 16px 以上、行高は `references/ja/typesetting.md` に従う（デジタル庁DS の基準）
   - 色は `references/visual/color-theory.md`（OKLCH）、基準値は `references/a11y/wcag.md`（テキスト 4.5:1、非テキスト 3:1）
   - 動きがあれば、各動きの時間・イージング・実装難度・`prefers-reduced-motion` の代替を表にする（`references/motion-interaction.md`）
   - ダーク/ライト両対応が必要なら両方のトークンを定義する
   - 冒頭に `<!-- generated-by: design-coach -->` を入れる

5. **自己点検**: Write 後に Read し、次を確認する。
   - TODO・空欄が残っていない
   - 本文コントラスト 4.5:1 以上
   - 色の役割（プライマリ・セマンティック・ニュートラル）に重複や欠落がない
   - `references/anti-generic.md` の項目に該当しない

6. **完了報告**: 生成したファイルのパス、主要な決定事項（3〜5行）、次の手順を伝える。
   - craft に進む場合: 「craft の designer は、これらのファイルを検出して実画面レビュー（フェーズ2c）から始められます」
   - craft を使わない場合: メインのClaudeに実装を依頼する際の渡し方を案内する

完了時に独立した1行で区切りを明示する。
例: `[design-coach] 仕様化フロー完了。以降は通常の会話として対応します`

## 禁止

- テンプレートの節構成を勝手に変更すること（変更が必要なら理由を示して確認）
- 未確認のまま `.craft/docs/` の既存ファイルを上書きすること

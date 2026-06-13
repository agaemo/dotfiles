# trade-roshi

投資道場スキル。老師と弟子たちが株式銘柄を分析し、裁定を下す。

## セットアップ

専用フォルダを1つ作り、そこを「道場」として使い続けるのが基本的な使い方。

```bash
mkdir ~/trade-roshi && cd ~/trade-roshi
```

以降はこのフォルダで Claude Code を起動するたびに、ウォッチリストや裁定履歴が引き継がれる。

## 使い方

```
/trade-roshi                   # ブリーフィング（ウォッチリスト確認・答え合わせ・雑談）
/trade-roshi AAPL              # 単一銘柄分析
/trade-roshi AAPL MSFT         # 複数銘柄比較・推薦
/trade-roshi preview AAPL      # 決算前シナリオ分析
/trade-roshi earnings AAPL     # 決算後レビュー・テーゼ確認
/trade-roshi sector 半導体      # セクター概観・注目銘柄
```

## フロー

```mermaid
flowchart TD
    Start([/trade-roshi]) --> Args{引数}

    Args -- なし --> B1[watchlist.json\nverdicts.json を読み込み]
    B1 --> B2[price-fetch + catalyst\n並列起動]
    B2 --> B3{答え合わせ対象?\n未チェック かつ 7日以上}
    B3 -- あり --> B4[損益を計算\nテーゼが崩れていないか確認\nverdicts.json を更新]
    B3 -- なし --> B5
    B4 --> B5[ブリーフィング表示\nウォッチリスト／次回決算／正解率]
    B5 --> B6{発話の種類 - 優先順位順}
    B6 -- 終わり --> B11([終了])
    B6 -- preview/earnings/sector --> NewModes
    B6 -- 銘柄追加・削除 --> B7[watchlist.json を更新]
    B6 -- 個別分析 --> S1
    B6 -- おすすめは? --> B9[ウォッチリストと前回裁定から\n老師が推薦]
    B6 -- 投資関連の質問 --> B10a[WebSearch で回答]
    B6 -- 雑談・その他 --> B10b[老師として応じる\n含蓄ある一言で返す]
    B7 --> B6
    S5 --> B6
    B9 --> B6
    B10a --> B6
    B10b --> B6

    Args -- 1つ --> S1[弟子4人を並列起動\nFund / Tech / Senti / Macro]
    S1 --> S2[強気・弱気リサーチャーを並列起動]
    S2 --> S3[リスク管理エージェント]
    S3 --> S4[老師の裁定\n買い / 売り / 様子見]
    S4 --> S5[現在値を取得\nverdicts.json に保存\nテーゼ・撤退条件を記録]

    Args -- 複数 --> M1[銘柄ごとに弟子4人×N を並列起動]
    M1 --> M2[各銘柄の強気・弱気を並列起動]
    M2 --> M3[各銘柄のリスク管理を並列起動]
    M3 --> M4[4軸比較表を出力]
    M4 --> M5[老師が推薦銘柄を選択]
    M5 --> M6[推薦→買い 非推薦→様子見\nverdicts.json に保存\nテーゼ・撤退条件を記録]

    Args -- preview ticker --> P1[earnings-preview エージェント]
    P1 --> P2[老師の決算前見立て]

    Args -- earnings ticker --> E1[earnings-review エージェント]
    E1 --> E2[テーゼが生きているか確認\n裁定見直し]

    Args -- sector 名前 --> Sec1[sector エージェント\nJP / US を判定]
    Sec1 --> Sec2[老師の見立てと\n注目銘柄の提案]

    NewModes --> P1
    NewModes --> E1
    NewModes --> Sec1
```

## データ

スキルを呼び出したディレクトリの `.trade-roshi/` 以下に保存される。

```
.trade-roshi/
  watchlist.json   # ウォッチリスト銘柄
  verdicts.json    # 裁定履歴（答え合わせ済みから90日で自動削除）
```

verdicts.json の各エントリ:

```json
{
  "ticker": "AAPL",
  "date": "2026-05-29",
  "price": 185.50,
  "verdict": "買い",
  "thesis": "AI向けハード需要でサイクル転換期",
  "exit_condition": "iPhone出荷が3四半期連続減少",
  "checked": false,
  "result_pct": null,
  "checked_date": null
}
```

## エージェント構成

```
agents/
  price-fetch.md       # 現在株価の一括取得
  catalyst.md          # 次回決算日・権利確定日の取得（ブリーフィングで並列起動）
  fundamental.md       # ファンダメンタル分析
  technical.md         # テクニカル分析
  sentiment.md         # センチメント分析
  macro.md             # マクロ・セクター分析
  bull-researcher.md   # 強気根拠の組み立て
  bear-researcher.md   # 弱気根拠の組み立て
  risk-mgmt.md         # リスク評価
  earnings-preview.md  # 決算前シナリオ分析
  earnings-review.md   # 決算後実績確認・テーゼ評価
  sector.md            # セクター概観・注目銘柄抽出
```

## 免責事項

このスキルはジョークコンテンツです。老師の裁定は投資判断の根拠にしないこと。老師は損失に責任を負わない。

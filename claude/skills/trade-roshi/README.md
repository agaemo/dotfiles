# trade-roshi

投資道場スキル。老師と弟子たちが株式銘柄を分析し、裁定を下す。

## 使い方

```
/trade-roshi              # ブリーフィング（ウォッチリスト確認・答え合わせ・雑談）
/trade-roshi AAPL         # 単一銘柄分析
/trade-roshi AAPL MSFT    # 複数銘柄比較・推薦
```

## フロー

```mermaid
flowchart TD
    Start([/trade-roshi]) --> Args{引数}

    Args -- なし --> B1[watchlist.json\nverdicts.json を読み込み]
    B1 --> B2[price-fetch エージェント\n現在値を一括取得]
    B2 --> B3{答え合わせ対象?\n未チェック かつ 7日以上}
    B3 -- あり --> B4[損益を計算\nverdicts.json を更新]
    B3 -- なし --> B5
    B4 --> B5[ブリーフィング表示\nウォッチリスト／正解率]
    B5 --> B6[対話ループ\n追加・削除・分析・推薦・雑談]

    Args -- 1つ --> S1[弟子4人を並列起動\nFund / Tech / Senti / Macro]
    S1 --> S2[老師が強気・弱気を整理]
    S2 --> S3[裁定を出力\n買い / 売り / 様子見]
    S3 --> S4[現在値を取得\nverdicts.json に保存]

    Args -- 複数 --> M1[銘柄ごとに弟子4人×N を並列起動]
    M1 --> M2[4軸比較表を出力]
    M2 --> M3[老師が推薦銘柄を選択]
    M3 --> M4[推薦→買い 非推薦→様子見\nverdicts.json に保存]
```

## データ

スキルを呼び出したディレクトリの `.trade-roshi/` 以下に保存される。

```
.trade-roshi/
  watchlist.json   # ウォッチリスト銘柄
  verdicts.json    # 裁定履歴（答え合わせ済みから90日で自動削除）
```

## 免責事項

このスキルはジョークコンテンツです。老師の裁定は投資判断の根拠にしないこと。老師は損失に責任を負わない。

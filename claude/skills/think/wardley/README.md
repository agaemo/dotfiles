# wardley

事業・製品・システムのコンポーネントをバリューチェーン × 進化軸でマッピングし、
内製・外注・差別化の戦略的判断を導く。Simon Wardley (2005〜) の手法。

## 使い方

```
/think wardley "SaaSスタートアップの開発体制"
/think wardley "ECサイトの決済・在庫・物流の構成"
/think wardley "IoTプラットフォーム事業"
```

## 出力例

```mermaid
quadrantChart
    title Wardley Map
    x-axis Genesis --> Commodity
    y-axis "可視性低" --> "可視性高"
    quadrant-1 "標準・必須（差別化なし）"
    quadrant-2 "差別化の源泉（投資優先）"
    quadrant-3 "外注検討候補"
    quadrant-4 "コスト最小化対象"
    "ユーザー体験": [0.15, 0.85]
    "独自レコメンド": [0.12, 0.55]
    "顧客管理": [0.45, 0.75]
    "決済API": [0.65, 0.4]
    "クラウド基盤": [0.85, 0.15]
```

## エージェント構成

chain-mapper → evolution-assessor → strategy-synthesizer の3段階逐次処理。

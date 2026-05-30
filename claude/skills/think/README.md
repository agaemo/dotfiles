# think

思考・分析・検討の相談を受け付けるオーケストレーター。入力の内容に応じて適切なスキルへ委譲する。

## フロー

```mermaid
flowchart TD
    Start(["/think [スキル名] 入力"]) --> Parse[引数を解析]

    Parse --> ExplicitSkill{スキル名を\n明示指定?}

    ExplicitSkill -- あり --> ValidSkill{スキルが\n存在する?}
    ValidSkill -- No --> Error["「スキル名XXは存在しません」\nSTOP"]
    ValidSkill -- Yes --> EmptyInput{入力が空?}
    EmptyInput -- Yes --> AskInput["「何を分析しますか?」"]
    AskInput --> Delegate
    EmptyInput -- No --> Delegate

    ExplicitSkill -- なし --> Auto[自動分類]
    Auto --> IsSixHats{six-hats\n向けか?}
    IsSixHats -- Yes --> Delegate
    IsSixHats -- No --> AskSkill["どのスキルを使うか\nユーザーに確認"]
    AskSkill --> UserChoice{選択}
    UserChoice -- six-hats --> Delegate
    UserChoice -- 直接回答 --> DirectAnswer[直接回答]

    Delegate["six-hats/SKILL.md を READ\n{input} を置換して実行"]
```

## 使い方

```
# スキルを自動判定
/think "新製品Xを日本市場に投入する計画（ターゲット：中小企業）"

# スキルを明示指定
/think six-hats "AWSかGCPか、バックエンドのクラウド選定"

# 対話形式
/think
```

## 委譲ルール

| 入力の性質 | 委譲先 |
|-----------|-------|
| 具体的な提案・計画・選択肢の検証 | six-hats |
| 上記以外 | ユーザーに確認 |

## スキルの追加方法

1. `SKILL.md` の「使えるスキル」テーブルにスキル名と得意な入力を追記する
2. ステップ2に判定基準を追加する
3. ステップ3に委譲処理を追加する
4. スキルのディレクトリを `think/` 配下に配置する

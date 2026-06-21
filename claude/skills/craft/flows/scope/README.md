# scope（種別確認・技術カテゴリ選定）フロー

種別（kind）の推定・確認・振り分けを一括で担当する。
会話から明確に推定できる場合は一言確認して new-static / new-project / new-app / consult へ
直接委譲し、不明確な場合（または確認が否定された場合）は要件・制約をヒアリングして振り分ける。
対応レシピがない技術（GAS等）はTODOとして報告し、consultへの相談・近いカテゴリでの妥協・終了を選んでもらう。

```mermaid
flowchart TD
    START([scope 起動]) --> S0INFER["STEP 0: 会話の文脈から\n種別を推定"]
    S0INFER --> S0CHECK{明確に\n推定できる?}
    S0CHECK -->|Yes| S0CONFIRM["「〇〇で進めますか？」と確認"]
    S0CONFIRM -->|承認| S0DIRECT{種別}
    S0DIRECT -->|1. 静的サイト| STATIC0[new-static]
    S0DIRECT -->|2. Webアプリ| DYNAMIC0[new-project]
    S0DIRECT -->|3. クロスプラットフォーム| APP0[new-app]
    S0DIRECT -->|4. 既存システムの相談| CONSULT0[consult]
    STATIC0 --> END_S0([完了])
    DYNAMIC0 --> END_D0([完了])
    APP0 --> END_A0([完了])
    CONSULT0 --> END_C0([完了])

    S0CONFIRM -->|否定| S1
    S0CHECK -->|No| S1

    S1["STEP 1: 相談の入口\n自由に話してもらう"]
    S1 --> EXIST{既存システムの\n相談?}
    EXIST -->|Yes| CONSULT[consult フローへ]
    EXIST -->|No| S2["STEP 2: 制約のヒアリング\nUI・DB認証・既存エコシステム依存・\n運用期間・技術知識レベル"]
    S2 --> S3["STEP 3: カテゴリ対応表と照合"]
    S3 --> MATCH{マッチする\nカテゴリ}
    MATCH -->|実装済み| GATE{ユーザー承認}
    MATCH -->|TODO\nGAS等| TODOR["未実装を報告"]
    TODOR --> TODO_CHOICE{どうする?}
    TODO_CHOICE -->|consultに相談\nSUMMARYを渡す| CONSULT
    TODO_CHOICE -->|近いカテゴリで妥協| GATE
    TODO_CHOICE -->|終了| END_T([終了])
    GATE -->|承認| S4["STEP 4: 委譲"]
    GATE -->|否定| S3B[対応表から\n直接選んでもらう]
    S3B --> S4
    S4 --> STATIC[new-static]
    S4 --> DYNAMIC[new-project]
    S4 --> APP[new-app]
    CONSULT --> END_C([完了])
    STATIC --> END_S([完了])
    DYNAMIC --> END_D([完了])
    APP --> END_A([完了])
```

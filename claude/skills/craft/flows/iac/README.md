# iac（Infrastructure as Code）フロー

Terraform/OpenTofu によるクラウドインフラのコード管理を導入・設計・運用する。
「設定を間違えると本番インフラが壊れる」領域のため、各ステップでユーザーの確認を挟みながら進める。

```mermaid
flowchart TD
    START([IaC相談を選択]) --> S0

    S0["ステップ0: ヒアリング\nクラウドプロバイダー・管理対象リソース・\n既存インフラの有無・環境数・State保存場所・利用規模"]
    S0 --> S05

    S05["ステップ0.5: 構成図の作成・確認\nplan.mdに既存図があればそれを使う。無ければ\nmermaidでシステム構成図を新規作成→承認"]
    S05 --> TOOL["ツール選定\n迷ったら Terraform / OpenTofu"]
    TOOL --> S15

    S15["ステップ1.5: researcher呼び出し（必須）\n対象provider（hashicorp/aws・hashicorp/google等）の\n最新バージョン・破壊的変更・認証方式の変更を調査\n→ .craft/docs/tech-research.md"]
    S15 --> DIFF{差分あり?}
    DIFF -->|Yes| PRESENT["差分をユーザーに提示"]
    PRESENT --> S1
    DIFF -->|No| S1

    S1["ステップ1: ディレクトリ構造の設計\nシンプル構成 / 環境分離構成"]
    S1 --> S2

    S2["ステップ2: State設定（リモートバックエンド）\nAWS: S3+DynamoDB / GCP: GCS"]
    S2 --> S3

    S3["ステップ3: Provider設定\nバージョンはtech-research.mdの推奨値を使用"]
    S3 --> S4

    S4["ステップ4: 変数・シークレット管理\nAWS: Secrets Manager/SSM / GCP: Secret Manager"]
    S4 --> S5

    subgraph APPLY["ステップ5: Plan/Apply"]
        PLAN["terraform plan"] --> GATE{ユーザー承認}
        GATE -->|承認| APPLY_RUN["terraform apply"]
    end

    S4 --> PLAN
    APPLY_RUN --> S6["ステップ6: 既存リソースのImport\n（必要な場合のみ）"]
    S6 --> END([完了])
```

## 呼び出し元

- `scope`: アプリ開発を伴わない、インフラのみのコード管理相談から直接委譲
- `consult`: 既存システムへのIaC導入相談から委譲
- `planner`（new-project等）: 本番クラウド公開を伴う新規プロジェクトで「インフラ構成」を決定した後、実装完了後にこのフローでTerraform/OpenTofu化する

## 設計上の注意点

- **破壊的変更（destroy/replace）は必ず赤字で警告し、plan結果の承認を得てからapplyする。**
- クラウドプロバイダーごとの具体例（State/Provider/シークレット管理）はAWS/GCPを用意している。Azure等それ以外は都度researcherで調査する。
- provider・認証方式は変化が速い領域のため、tech-research.md（researcher呼び出し結果）を必ず確認してから設定を確定する。recipeのように固定化した手順を鵜呑みにしない。

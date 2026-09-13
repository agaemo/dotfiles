---
name: iac
description: IaC（Infrastructure as Code）の導入・設計・運用手順。Terraform/OpenTofu を中心に、インフラをコード管理したいときに使う。
---

## このスキルの使い方

IaC は「設定を間違えると本番インフラが壊れる」リスクがある。
そのため、このスキルは **各ステップでユーザーの確認を取ってから次に進む** 設計になっている。
絶対に先回りしてリソースを作ったり `apply` を実行したりしないこと。

---

## ステップ0: ヒアリング（必ず最初に実施）

IaC 作業を始める前に、以下を確認してユーザーの回答を待つこと。

```
確認事項：
1. クラウドプロバイダーは何か？（AWS / GCP / Azure / その他）
2. 管理したいリソースは何か？（VPC・EC2・RDS・Lambda・Container など）
3. 既存インフラがある場合: Terraform 管理外のリソースはあるか？（import が必要）
4. 環境は何種類あるか？（dev / staging / prod など）
5. チームで使うか、個人利用か？（検証・PoC目的でクラウドに何も永続的に残したくない場合も
   ここで明示してもらう）
6. State の保存場所はどこにするか？
   （S3+DynamoDB / GCS / Terraform Cloud / ローカルstate）
   IMPORTANT: 質問5で「個人利用」かつ「検証・PoC目的」と回答された場合、ローカルstateを
   選択肢として明示的に提示すること（クラウド利用が前提の選択肢だけを出さない）。
   ただしローカルstateはチーム利用・実運用への移行を考えていない場合に限る旨を伝える
   （複数人での同時実行に弱く、マシン故障でState自体を失うリスクがあるため）。
```

すべての回答が揃うまで実装を始めないこと。

---

## ステップ0.5: 構成図の作成・確認

IF `.craft/docs/plan.md` の「インフラ構成」節に既にシステム構成図がある（`planner` 経由で
呼ばれた場合）:
  それをそのまま使う。作り直さない。
ELSE（iac単独で呼ばれた場合。構成図が無い）:
  ステップ0のヒアリング結果から、mermaid flowchart でシステム構成図を作成する。
  利用者→フロントエンド配信→認証→API/実行基盤→データストアのデータフローを矢印で表し、
  各ノードにサービス名と役割（1行）を添える。既存インフラがある場合は「既存」「新規」を
  色分けで区別する。
  PRESENT: 構成図をユーザーに提示する
  GATE: ユーザー承認
    IF 否定された: 該当箇所を修正して再提示する
  PROHIBITED: 承認前にステップ1へ進むこと
ENDIF

---

## ツール選定の目安

| ツール | 向いているケース |
|--------|----------------|
| **Terraform / OpenTofu** | マルチクラウド・チーム開発・OSS を優先したい |
| **Pulumi** | TypeScript/Python でインフラを書きたい・ロジックが複雑 |
| **AWS CDK** | AWS 専用・TypeScript/Python 既存チーム |
| **Ansible** | サーバー設定管理（プロビジョニング）に特化したい |

迷ったら **Terraform / OpenTofu** を選ぶ。エコシステムと情報量が最も豊富。
OpenTofu は Terraform の OSS fork で、ライセンス問題を避けたい場合に選択する。

---

## ステップ1: ディレクトリ構造の設計

ユーザーの環境数・規模に応じて提案する（変更可）。

### シンプル構成（環境1〜2、個人 or 小チーム）

```
infra/
├── main.tf          # メインのリソース定義
├── variables.tf     # 変数定義
├── outputs.tf       # 出力値
├── versions.tf      # provider バージョン固定
└── terraform.tfvars # 変数の値（.gitignore に入れること）
```

### 環境分離構成（環境3つ以上、チーム開発）

```
infra/
├── modules/
│   ├── network/     # 再利用可能なモジュール
│   ├── compute/
│   └── database/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
└── versions.tf
```

**どちらにするか確認してから作成すること。**

---

## ステップ1.5: 技術調査（researcher呼び出し、必須）

IMPORTANT: Terraform provider のバージョン・認証方式・推奨されるState管理方法は変化が速い。
IaCは「設定を間違えると本番インフラが壊れる」領域のため、古い情報のまま進めるリスクが特に高い。

Agent ツールで researcher エージェント（`{SKILL_DIR}/agents/researcher.md`。SKILL_DIR は
craftディレクトリの絶対パス）を起動する。
- 対象: ステップ0で確定したクラウドプロバイダーの Terraform provider（`hashicorp/aws` /
  `hashicorp/google` / `azurerm` 等）
- モード: フル調査（iacには専用recipeが無いため常にフル調査）
- 調査観点: providerの最新バージョン・直近の破壊的変更・認証方式の変更（IAM Role/
  Workload Identity連携等）・推奨されるState管理方法・既知の罠
WAIT_FOR: サブエージェントの完了報告（`.craft/docs/tech-research.md` への保存）を受け取ってから続きに進む
IF READ FAILED（researcher.mdが見つからない）:
  NOTE: 読めない場合でも省略せず、WebSearch/WebFetchで同等の調査をこの場で行うこと

IMPORTANT: researcherは客観的な事実（バージョンステータス変化・新たな認証方式等）を
  「懸念なし」の一言でまとめて省略しない。差分がある場合、その内容をユーザーに提示してから
  次のステップへ進むこと。
  WAIT_FOR: ユーザーの回答（差分がある場合のみ）

---

## ステップ2: State の設定

State はインフラの現状を記録するファイル。**絶対に git にコミットしない**（シークレットが含まれる）。

ステップ0で「ローカルstate」を選んだ場合は下記「ローカルstateの場合」に従う。
それ以外（リモートバックエンド）は、ステップ0で確定したクラウドプロバイダー、および
`.craft/docs/tech-research.md`（ステップ1.5の調査結果）に従い、以下の該当する例を
ベースに確定する。

### ローカルstateの場合（個人検証・PoC用途のみ）

`backend` ブロックを設定しない（Terraformのデフォルトでカレントディレクトリの
`terraform.tfstate` に保存される）。追加設定は不要。
`.gitignore` に `terraform.tfstate` `terraform.tfstate.backup` `.terraform/` を
必ず追加する（Stateにシークレットが平文で含まれるため）。

### AWS（S3 + DynamoDB）の場合

```hcl
# versions.tf
terraform {
  backend "s3" {
    bucket         = "<your-state-bucket>"
    key            = "infra/<env>/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "<your-lock-table>"  # State ロック用
  }
}
```

バックエンド用リソース（S3バケット・DynamoDBテーブル）はコンソールで手動作成するか、
bootstrap 用の別ディレクトリ（`infra/bootstrap/`）で先に作る。
**「バックエンドリソースをどうするか」を確認してから進むこと。**

### GCP（GCS）の場合

```hcl
# versions.tf
terraform {
  backend "gcs" {
    bucket = "<your-state-bucket>"
    prefix = "infra/<env>"
  }
}
```

GCSバックエンドはオブジェクトの世代管理でState変更履歴を保持し、Terraform自体が
ロック機構を持つため、AWSのDynamoDBに相当する別リソースは不要（GCSバケット1つで足りる）。
バックエンド用のGCSバケットはコンソールまたは `gcloud storage buckets create` で先に作る。
**「バックエンドバケットをどうするか」を確認してから進むこと。**

---

## ステップ3: Provider 設定

ステップ0で確定したクラウドプロバイダーに応じて選ぶ。バージョンは
`.craft/docs/tech-research.md`（ステップ1.5の調査結果）の推奨値を使う（下記は例）。

### AWS の場合

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # マイナーバージョンまで固定する
    }
  }
}

provider "aws" {
  region = var.aws_region
  # アクセスキーをここに書かない。環境変数 AWS_PROFILE か IAM Role を使う。
}
```

### GCP の場合

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"  # マイナーバージョンまで固定する
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  # サービスアカウントキーをここに書かない。ローカルは Application Default
  # Credentials（`gcloud auth application-default login`）、CI/CDは
  # Workload Identity連携を使う（長期キーの発行・保管を避ける）。
}
```

---

## ステップ4: 変数・シークレット管理のルール

- **シークレット（DBパスワード・APIキー）は `terraform.tfvars` に書かず、シークレット管理サービスから参照すること**
  - AWS: Secrets Manager / SSM Parameter Store
  - GCP: Secret Manager
- `terraform.tfvars` は `.gitignore` に必ず追加する
- `variables.tf` に `sensitive = true` をつけてログへの出力を防ぐ

```hcl
# variables.tf
variable "db_password" {
  type      = string
  sensitive = true  # plan/apply の出力に値が表示されなくなる
}
```

### AWS: Secrets Manager からの参照例

```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/myapp/db"
}
```

### GCP: Secret Manager からの参照例

```hcl
data "google_secret_manager_secret_version" "db" {
  secret = "prod-myapp-db-password"
}
```

---

## ステップ5: Plan / Apply の手順

```bash
# 初期化（初回・provider 追加時）
terraform init

# 変更内容の確認（apply の前に必ず実行）
terraform plan -out=tfplan

# plan 結果をユーザーに提示する（destroy / replace が含まれる場合は赤字で警告）
GATE: plan の内容をユーザーに提示し、承認を得ること
WAIT_FOR: ユーザーの承認
PROHIBITED: 承認前に terraform apply を実行すること

terraform apply tfplan

# 特定リソースだけ対象にする（影響範囲を絞りたいとき）
terraform apply -target=aws_instance.web tfplan
```

**`terraform apply` の前に必ずユーザーに plan の内容を提示して確認を取ること。**
特に `destroy` や `replace` が含まれる場合は赤字で警告すること。

---

## ステップ6: 既存リソースの Import

コンソールで手動作成済みのリソースを Terraform 管理下に入れる手順。

```bash
# リソースアドレスと実際のID を指定する
terraform import aws_instance.web i-0123456789abcdef0

# Terraform 1.5 以降: import ブロックでコードから宣言できる
import {
  to = aws_instance.web
  id = "i-0123456789abcdef0"
}
```

Import 後は必ず `terraform plan` で差分がないことを確認すること（差分があると次回 apply で上書きされる）。

---

## 破壊的変更の警告

`plan` 結果にこれらが含まれていたら、**実行前にユーザーへ明示的に警告すること**：

```
# 危険度: 高（データ消失・ダウンタイムのリスク）
- destroy     → リソース削除
- replace     → 削除 & 再作成（forces replacement）
- recreate    → 同上

# 危険度: 中（設定変更による影響）
- update      → 再起動が必要な場合あり（EC2 タイプ変更など）
```

---

## .gitignore のテンプレート

```gitignore
# State ファイル（シークレットを含む）
*.tfstate
*.tfstate.*
.terraform/

# ローカル変数値（シークレットを含む可能性）
terraform.tfvars
*.auto.tfvars

# Plan ファイル（バイナリ）
*.tfplan
tfplan
```

---

## チェックリスト

### 設計フェーズ
- [ ] ヒアリング（ステップ0）が完了している
- [ ] ディレクトリ構造を決定してユーザーの承認を得た
- [ ] State のリモートバックエンドを決定した

### 実装フェーズ
- [ ] `*.tfstate` / `terraform.tfvars` / `.terraform/` が `.gitignore` に入っている
- [ ] provider バージョンが `~>` で固定されている（メジャーバージョン固定）
- [ ] シークレットが `variables.tf` に `sensitive = true` で定義されている
- [ ] シークレットの値が `.tfvars` ではなく Secrets Manager / SSM から参照されている

### 実行フェーズ
- [ ] `terraform init` を実行した
- [ ] `terraform plan` の結果をユーザーに確認してもらった
- [ ] `destroy` / `replace` が含まれる場合はユーザーへ警告した
- [ ] `terraform apply` 後に `terraform plan` で差分がゼロになることを確認した

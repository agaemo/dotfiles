# Cloud Native ツールカタログ

## 適用場面

- Kubernetesを既に導入している、または `flows/iac` の「コンテナ実行基盤の選定の目安」で
  段階3（Kubernetes）を選んだ場合に、周辺ツールの選定リファレンスとして参照する
- Kubernetesを使っていない場合は参照不要（無理に導入を勧めるためのリストではない）

出典：CyberAgent「Cloud Native Technology Map 2025」の利用率データを参考にした整理。
利用率は同社事例における参考値であり、選定の絶対基準ではない。

---

## CNCF Graduated（成熟・実績豊富）

| ツール | 何をするもの |
|---|---|
| Kubernetes | コンテナのオーケストレーション基盤（デプロイ・スケーリング・自己修復） |
| Helm | Kubernetesマニフェストのパッケージマネージャ（テンプレート化して配布・バージョン管理） |
| Prometheus | メトリクス収集・時系列DB。K8sの標準的な監視基盤 |
| Istio | サービスメッシュ。マイクロサービス間の通信を可視化・制御・暗号化 |
| Argo | ArgoCD（GitOpsデプロイ）やArgo Workflows（ジョブ実行）等のK8sネイティブツール群 |
| KEDA | イベント駆動のオートスケーラー（キュー長やcron等、CPU/メモリ以外の指標でスケール） |
| Envoy | 高性能プロキシ。Istioなどのサービスメッシュの内部でも使われる |
| cert-manager | K8s上でTLS証明書を自動発行・更新するオペレーター |
| Fluentd / Fluent Bit | ログ収集・転送の統一レイヤー |
| Cilium | eBPFベースのCNI。ネットワーキング・ネットワークポリシーを高性能に制御 |
| Flux | GitOpsツール。Argo CDと並ぶ2大GitOpsツールの一つ |
| Falco | ランタイムセキュリティ監視。コンテナ内の不審な挙動を検知 |
| Backstage | 開発者ポータル。複数サービス・複数チームを横断したカタログ化 |

## CNCF Incubating

| ツール | 何をするもの |
|---|---|
| OpenTelemetry | メトリクス・トレース・ログの計装・収集の標準規格/SDK |
| gRPC | 高速なRPC通信フレームワーク |
| Knative | K8s上にサーバーレス層を構築する基盤（Cloud Runの内部実装もこれ） |

## CNCFプロジェクト外

| ツール | 何をするもの |
|---|---|
| Datadog | 商用の監視・セキュリティSaaS |
| Loki | ログ集約システム（Grafanaエコシステム） |
| External Secrets | クラウドのシークレット管理サービス（AWS Secrets Manager等）をK8s Secretへ同期するオペレーター |
| Grafana | メトリクス・ログの可視化ダッシュボード |
| k6 | 負荷試験ツール |
| VictoriaMetrics | Prometheus互換の時系列DB。Prometheus本体より省リソース |
| ExternalDNS | Service/IngressからDNSレコードを自動作成・更新する |
| Reloader | ConfigMap/Secretの変更を検知してPodを自動再起動する |
| NGINX | Ingress Controller（クラスタ外からのHTTPルーティング）として広く使われる |
| SOPS | Git管理下のファイルを暗号化するツール。GitOpsでのシークレット管理の定番 |

---

## iacスキルとの接続

`flows/iac` のステップ4（変数・シークレット管理）ではTerraformからSecrets Manager /
Secret Managerを直接参照する構成を案内している。Kubernetes環境ではそれに加えて、
以下のいずれかで橋渡しするのが定番：

- **External Secrets**：クラウド側のシークレットをK8s Secretへ同期するオペレーター
- **SOPS**：Gitリポジトリ上で暗号化したまま管理し、GitOpsのデプロイフローに乗せる

どちらを使うかは「Terraformで管理するリソース側で完結させるか」「K8s上のPodから見た
シークレット管理をK8sネイティブな方法に寄せるか」で選ぶ。

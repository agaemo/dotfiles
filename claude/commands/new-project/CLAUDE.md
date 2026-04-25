# CLAUDE.md

## プロジェクト概要

<!-- TODO: プロジェクトの概要を1〜3文で書いてください -->

**プロジェクト:** <!-- TODO: プロジェクト名 -->
**スタック:** <!-- TODO: 言語・フレームワーク（例: TypeScript / Hono / Cloudflare Workers） -->
**目標:** <!-- TODO: このプロジェクトで達成したいこと -->

---

## アーキテクチャ

<!-- TODO: アーキテクチャの概要を書いてください（例: routes → services → repositories の3層構造） -->

```
<!-- TODO: ディレクトリ構造のコメント付きツリーを書いてください -->
```

---

## 開発ワークフロー

```bash
# 起動: TODO
# テスト: TODO
# デプロイ: TODO
```

---

## 必ず守るルール

### コンテキスト管理
- エージェント引き継ぎ前に `/compact` を実行し、完了内容と次の指示をまとめること。

### ワークフロー
- 新規プロジェクト・新機能・曖昧な依頼: `intake` → `refiner` → `planner`（承認後に実装）
- フロントエンドUI含む場合: 実装前に `designer` でUI設計・デザインシステムを確定すること
- ビジネスロジック・API・DB操作の実装: `tester`（TDDモード）→ 実装 → `tester`（補完モード）
- 実装後: `planner` が宣言したトラックに従いレビューを実施すること
- 本番リリース前: `release-planner` でリリース計画・ロールバック手順を策定すること
- 新規プロジェクト時: `README.md` を作成すること（前提条件・セットアップ・実行・テスト）

### DB
- スキーマ設計は `templates/architecture/db-design.md` を参照すること
- INSERT/UPDATE/DELETE は `changes === 0` なら例外をthrowすること

### コードスタイル
- <!-- TODO: 言語・フレームワーク固有のスタイルルール -->
- TypeScript の型チェックは `bunx tsc --noEmit` を使うこと

---

## 制約事項

<!-- TODO: このプロジェクト固有の制約を書いてください -->
<!-- 例: Cloudflare Workers環境のためNode.js APIは使えない -->

# Onion Architecture（オニオンアーキテクチャ）

## 適用場面

- ビジネスルールが複雑で長期運用が見込まれるシステム
- テストカバレッジを高めたい（ドメイン層が外部依存ゼロ）
- DB・フレームワークを将来置き換える可能性がある

## 層の定義

```
src/
├── domain/          # 中心：エンティティ・値オブジェクト・ドメインサービス（依存ゼロ）
│   ├── entities/
│   ├── value-objects/
│   └── repositories/   ← インターフェースのみ（実装はinfraに）
├── application/     # ユースケース（domain のみ依存）
│   └── use-cases/
├── infrastructure/  # 外部：DB・外部API・メール（domainインターフェースの実装）
│   ├── repositories/
│   └── services/
└── presentation/    # HTTP・CLI・UIなど（applicationのみ依存）
    └── routes/
```

## 依存の向き

**外 → 内のみ。内は外を知らない。**

```
presentation → application → domain
infrastructure → domain（インターフェース実装のため）
```

## ルール

- `domain/` は Node.js / フレームワーク API を import しない
- リポジトリは `domain/repositories/` にインターフェースを置き、実装は `infrastructure/repositories/` に置く
- ユースケースはコンストラクタインジェクションでリポジトリを受け取る
- エンティティは `id` を持ち、同一性は `id` で判断する

## DB設計との関係

- エンティティ1つ = テーブル1つを基本とする（正規化を優先）
- 集約（Aggregate）単位でトランザクションを設計する
- 集約をまたぐ操作はドメインイベントまたはアプリケーション層でコーディネートする

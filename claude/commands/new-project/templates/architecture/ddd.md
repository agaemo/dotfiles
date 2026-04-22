# DDD（Domain-Driven Design）エッセンシャル

## 適用場面

- ドメインが複雑・専門用語が豊富
- 複数チームが同じシステムを開発
- 長期運用で仕様変更が多い

## 主要概念

| 概念 | 説明 | 実装例 |
|------|------|--------|
| Entity | IDで同一性を判断するオブジェクト | `User`, `Order` |
| Value Object | 値で同一性を判断・不変 | `Email`, `Money`, `Address` |
| Aggregate | 整合性の境界。ルートエンティティ経由でのみ操作 | `Order`（`OrderItem`を内包） |
| Repository | 集約の永続化インターフェース | `OrderRepository` |
| Domain Service | 複数の集約をまたぐロジック | `PricingService` |
| Domain Event | 集約内で起きた事実 | `OrderPlaced`, `PaymentFailed` |

## ディレクトリ構造（Onion と組み合わせる）

```
src/domain/
├── order/
│   ├── Order.ts           # Aggregate Root
│   ├── OrderItem.ts       # Entity（Order経由でのみ操作）
│   ├── OrderStatus.ts     # Value Object
│   ├── OrderRepository.ts # Interface
│   └── events/
│       └── OrderPlaced.ts
├── user/
│   ├── User.ts
│   ├── Email.ts           # Value Object
│   └── UserRepository.ts
```

## ルール

- Aggregate 外から子エンティティを直接操作しない
- Value Object はイミュータブルにする（`readonly` + `Object.freeze` or クラス）
- `new Email("invalid")` のようにコンストラクタでバリデーションを行う
- テーブル設計は Aggregate 単位を意識する（集約内は結合クエリOK、集約間は JOIN しすぎない）

## 軽量DDDの現実解

フルDDDは重い。以下の順で段階的に導入すること：

1. Value Object だけ導入（`Email`, `UserId` など型安全化）
2. Repository インターフェースを定義する
3. Aggregate の境界を意識する
4. Domain Event は本当に必要になってから

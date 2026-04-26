# モジュラーモノリス

## 適用場面

- レイヤードで始めたが、機能が増えてサービス間の依存が複雑になってきた
- 将来マイクロサービスへの分割を視野に入れているが、今は単一デプロイで十分
- チームが小〜中規模で、サービス間通信のオーバーヘッドを避けたい

## レイヤードとの違い

レイヤードは「横に切る（層で分ける）」。モジュラーモノリスは「縦に切る（機能で分ける）」。

```
# レイヤード（横切り）
src/
├── routes/        # 全機能のHTTPハンドラが混在
├── services/      # 全機能のビジネスロジックが混在
└── repositories/  # 全機能のDB操作が混在

# モジュラーモノリス（縦切り）
src/
├── order/         # 注文に関するすべてのコードが閉じている
├── user/          # ユーザーに関するすべてのコードが閉じている
└── payment/       # 決済に関するすべてのコードが閉じている
```

## 構造

```
src/
├── order/
│   ├── routes.ts              # HTTPハンドラ
│   ├── service.ts             # ビジネスロジック
│   ├── repository.interface.ts # リポジトリインターフェース
│   ├── repository.ts          # DB実装
│   └── index.ts               # モジュール外に公開するAPIのみをexport
├── user/
│   ├── routes.ts
│   ├── service.ts
│   ├── repository.interface.ts
│   ├── repository.ts
│   └── index.ts
└── shared/                    # モジュール間で共有する型・ユーティリティ
    └── types.ts
```

## リポジトリインターフェース

サービスは実装ではなくインターフェースに依存させる。DBエンジンの切り替え（SQLite → MySQL/PostgreSQL など）が実装ファイルの差し替えだけで完結する。

```ts
// order/repository.interface.ts
export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

// order/service.ts
export class OrderService {
  constructor(private readonly repo: OrderRepository) {}
}
```

## ルール

- モジュール内部のファイルを他モジュールから直接 import しない（`index.ts` 経由のみ）
- モジュール間の依存は `shared/` に置いた型・インターフェース経由にする
- サービスはコンストラクタインジェクションでリポジトリを受け取る（`new` で直接生成しない）
- DB トランザクションはモジュール内で完結させる（モジュールをまたぐトランザクションは設計を見直す）
- 循環依存を作らない（`order → user` は OK、`order ↔ user` は NG）

## マイクロサービスへの移行パス

モジュール境界が守られていれば、各モジュールを独立サービスに切り出せる。

1. モジュール間の同期呼び出しを非同期イベントに置き換える
2. DB をモジュールごとに分離する
3. 独立したデプロイ単位に切り出す

## スケールの限界サイン

- あるモジュールだけデプロイ頻度・チームが突出して多い
- モジュール間のデータ共有が増えて `shared/` が肥大化する

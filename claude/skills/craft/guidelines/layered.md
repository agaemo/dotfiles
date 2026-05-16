# Layered Architecture（レイヤードアーキテクチャ）

## 適用場面

- CRUD中心のシステム・中小規模API
- チームが薄い・スピード優先
- ビジネスルールがシンプルで変更頻度が低い

## 構造

```
src/
├── routes/       # HTTPハンドラ・バリデーション
├── services/     # ビジネスロジック
├── repositories/
│   ├── interfaces/   # リポジトリインターフェース定義
│   └── impl/         # DB実装（SQLite・MySQL・PostgreSQL など）
└── lib/          # 汎用ユーティリティ
```

## 依存の向き

```
routes → services → repositories/interfaces ← repositories/impl
```

## リポジトリインターフェース

サービスは実装ではなくインターフェースに依存させる。DBエンジンの切り替え（SQLite → MySQL/PostgreSQL など）が実装ファイルの差し替えだけで完結する。

```ts
// repositories/interfaces/UserRepository.ts
export interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

// repositories/impl/UserRepositorySQLite.ts
export class UserRepositorySQLite implements UserRepository { ... }

// repositories/impl/UserRepositoryPostgres.ts
export class UserRepositoryPostgres implements UserRepository { ... }
```

## ルール

- `routes/` にビジネスロジックを書かない（バリデーションと HTTP 変換のみ）
- `repositories/` は生の SQL またはクエリビルダのみ。ビジネス判断をしない
- サービスはコンストラクタインジェクションでリポジトリを受け取る（`new` で直接生成しない）
- サービスの戻り値は `Result<T>` 型を使い、例外を throw しない

## スケールの限界サイン

以下が増えてきたらオニオンアーキテクチャへの移行を検討すること：

- サービスが他サービスを大量 import する
- ビジネスルールが routes/repositories に漏れ始める
- テストでDBモックが複雑になる

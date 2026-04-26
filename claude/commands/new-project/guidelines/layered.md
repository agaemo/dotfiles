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
├── repositories/ # DB操作（SQL・ORMクエリ）
└── lib/          # 汎用ユーティリティ
```

## 依存の向き

```
routes → services → repositories
```

## ルール

- `routes/` にビジネスロジックを書かない（バリデーションと HTTP 変換のみ）
- `repositories/` は生の SQL またはクエリビルダのみ。ビジネス判断をしない
- サービスの戻り値は `Result<T>` 型を使い、例外を throw しない

## スケールの限界サイン

以下が増えてきたらオニオンアーキテクチャへの移行を検討すること：

- サービスが他サービスを大量 import する
- ビジネスルールが routes/repositories に漏れ始める
- テストでDBモックが複雑になる

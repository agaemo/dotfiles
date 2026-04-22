---
name: api-design
description: REST APIの設計規約（命名・HTTPメソッド・ステータスコード・エラーフォーマット・ページネーション）。API設計時・コードレビュー時の参照用。
---

## URL設計

### リソース命名

```
# 複数形・小文字・ハイフン区切り
GET    /users
GET    /users/:id
POST   /users
PUT    /users/:id       # リソース全体の置き換え
PATCH  /users/:id       # 部分更新
DELETE /users/:id

# ネストは2階層まで
GET    /users/:id/posts
GET    /users/:id/posts/:postId

# 3階層以上はフラットに切り出す
GET    /comments/:id    # /users/:id/posts/:postId/comments/:id ではなく
```

### 動詞を使わない

```
# NG
POST /createUser
GET  /getUserById
POST /users/delete

# OK
POST   /users
GET    /users/:id
DELETE /users/:id
```

### アクションが動詞にならない場合（例外）

```
# リソースに対する操作で名詞化できないもの
POST /users/:id/activate
POST /orders/:id/cancel
POST /payments/:id/refund
```

---

## HTTPメソッドの使い分け

| メソッド | 用途 | 冪等性 |
|---------|------|--------|
| GET | 取得（副作用なし） | ○ |
| POST | 新規作成・副作用あり操作 | ✕ |
| PUT | リソース全体の置き換え | ○ |
| PATCH | 部分更新 | △（実装による） |
| DELETE | 削除 | ○ |

---

## ステータスコード

```
200 OK              GET成功・PUT/PATCH成功
201 Created         POST成功（Location ヘッダにURLを含める）
204 No Content      DELETE成功（ボディなし）

400 Bad Request     バリデーションエラー・不正なリクエスト
401 Unauthorized    認証が必要（未ログイン）
403 Forbidden       認証済みだが権限なし
404 Not Found       リソースが存在しない
409 Conflict        状態の競合（重複登録など）
422 Unprocessable   意味的に不正（400より具体的なバリデーションエラーに使う）

500 Internal Server Error  サーバー側の予期しないエラー
```

---

## レスポンスフォーマット

### 成功レスポンス（単一リソース）

```json
{
  "id": "01HX...",
  "name": "山田太郎",
  "email": "yamada@example.com",
  "createdAt": "2024-01-20T09:00:00Z"
}
```

### 成功レスポンス（一覧）

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "hasNext": true
  }
}
```

### エラーレスポンス

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": [
      { "field": "email", "message": "有効なメールアドレスを入力してください" },
      { "field": "age", "message": "18以上の値を入力してください" }
    ]
  }
}
```

エラーコードは機械可読な定数文字列（SCREAMING_SNAKE_CASE）にする。
`message` はユーザーへの表示用。`code` はアプリ側の条件分岐に使う。

---

## ページネーション

### offset方式（シンプル・順序が安定している場合）

```
GET /posts?limit=20&offset=40
```

```json
{
  "data": [...],
  "pagination": { "total": 100, "limit": 20, "offset": 40, "hasNext": true }
}
```

### cursor方式（大量データ・リアルタイム更新がある場合）

```
GET /posts?limit=20&cursor=eyJpZCI6MTAwfQ==
```

```json
{
  "data": [...],
  "pagination": { "nextCursor": "eyJpZCI6ODB9", "hasNext": true }
}
```

offset方式は深いページで遅くなる（OFFSET 10000は10000行スキャンする）。
10万件を超えるデータにはcursor方式を使うこと。

---

## レートリミット

```
# レスポンスヘッダーで残量を通知する
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1706778000   # Unix timestamp

# 超過時は 429 Too Many Requests を返す
```

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "リクエスト上限に達しました。しばらく待ってから再試行してください",
    "retryAfter": 60
  }
}
```

レートリミットの単位はユーザーID・APIキー・IPアドレスのいずれかを選択する。
エンドポイント単位（書き込み系は厳しく）で設定するのが望ましい。

---

## 冪等性（Idempotency）

金融・注文など「二重実行が致命的な操作」には冪等性キーを必ず実装する。

```
# クライアントが生成したUUIDをヘッダーに含める
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

サーバー側の処理：
1. `Idempotency-Key` をキーにDBまたはキャッシュに結果を保存する
2. 同じキーで再リクエストが来たら保存済みの結果をそのまま返す（再処理しない）
3. キーの有効期限は24時間〜7日程度

冪等性キーが必要なエンドポイント：
- 決済・返金
- 注文作成
- メール送信・通知
- 外部サービスへの書き込み

---

## バージョニング

```
# URLパスにバージョンを含める（推奨）
/v1/users
/v2/users

# 後方互換性のない変更をするときに新バージョンを作る
# 旧バージョンは最低6ヶ月は維持する
```

---

## 日時・ID

```
# 日時: ISO 8601 / UTC
"createdAt": "2024-01-20T09:00:00Z"   # OK
"created_at": "2024/01/20 09:00:00"    # NG

# ID: UUIDv7（時刻順ソート可能）またはULID
# 整数連番をAPIレスポンスに露出しない（ユーザー数等が推測される）
"id": "01HX7QJ2K8B3V1AYMPPX6HKVR4"   # ULID
```

---

## チェックリスト

- [ ] URLはリソース名（複数形・名詞）になっている
- [ ] ネストは2階層以内
- [ ] HTTPメソッドが正しい（取得=GET, 作成=POST, 更新=PATCH/PUT, 削除=DELETE）
- [ ] ステータスコードが適切（201 Created, 204 No Content 等）
- [ ] エラーレスポンスに `code`（機械可読）と `message`（人間可読）がある
- [ ] 一覧取得にページネーションがある
- [ ] 日時はISO 8601 / UTC
- [ ] IDに整数連番を使っていない

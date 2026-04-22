---
name: observability
description: ログ・トレーシング・ヘルスチェックなど可観測性の設計と実装指針。問題が起きたときに原因を追えるシステムにするために使う。
---

## なぜ可観測性が必要か

スケールすると「何が起きているか分からない」ことが最大のリスクになる。
ログがないと障害の原因特定に数時間かかり、再発防止もできない。
小規模のうちから構造を整えておくコストは低く、後から直すコストは高い。

---

## 構造化ログ

### 原則

- ログは**JSON形式**で出力する（人間が読むより機械が集計できることを優先）
- すべてのログに**CorrelationID**（リクエストID）を含める
- ログレベルを使い分ける：`debug` / `info` / `warn` / `error`
- エラーを `catch` したら必ずログに出す。握り潰し禁止

### 必須フィールド

```json
{
  "timestamp": "2024-01-20T09:00:00.123Z",
  "level": "error",
  "correlationId": "req_01HX7QJ2K8B3V1AY",
  "userId": "usr_01HX...",
  "message": "注文作成に失敗しました",
  "error": {
    "name": "DatabaseError",
    "message": "Deadlock found when trying to get lock",
    "stack": "..."
  },
  "context": {
    "orderId": "ord_01HX...",
    "duration": 234
  }
}
```

### CorrelationIDの伝播

HTTPリクエストの入口でIDを生成し、全ての処理に引き継ぐ。

```typescript
// ミドルウェアで生成
app.use((req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] ?? generateId()
  res.setHeader('x-correlation-id', req.correlationId)
  next()
})

// サービス層に渡す
await orderService.create(data, { correlationId: req.correlationId })

// 外部APIコール時にヘッダーで引き継ぐ
headers['x-correlation-id'] = ctx.correlationId
```

### ログに含めてはいけないもの

- パスワード・トークン・APIキー
- クレジットカード番号・個人識別番号
- 大量のデータ（クエリ結果全件など）

---

## エラーハンドリングの原則

```typescript
// NG: エラーを握り潰す
try {
  await sendEmail(user)
} catch {
  // 何もしない
}

// NG: console.log だけ（構造化されていない）
} catch (e) {
  console.log('error', e)
}

// OK: 構造化ログ + 適切な伝播判断
} catch (e) {
  logger.error('メール送信失敗', {
    correlationId: ctx.correlationId,
    userId: user.id,
    error: e,
  })
  // 致命的でなければ処理を続行。致命的なら throw する。
}
```

---

## ヘルスチェックエンドポイント

ロードバランサー・Kubernetes・監視ツールが使う。必ず実装すること。

```
GET /health         → 簡易チェック（即時応答。DB接続確認なし）
GET /health/ready   → 依存サービス含む全体チェック（DBに接続できるか等）
```

```json
// /health のレスポンス例
{
  "status": "ok",
  "version": "1.2.3",
  "uptime": 3600
}

// /health/ready のレスポンス例（一部が落ちていても詳細を返す）
{
  "status": "degraded",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "externalApi": "timeout"
  }
}
```

ステータスコード：全チェック正常 → `200`、一部異常 → `503`

---

## Graceful Shutdown

プロセス終了シグナル（`SIGTERM`）を受けたとき、処理中のリクエストを完了してから終了する。
デプロイ時に「リクエストが途中で切れる」問題を防ぐ。

```typescript
process.on('SIGTERM', async () => {
  logger.info('Shutting down gracefully...')
  server.close(async () => {
    await db.close()
    logger.info('Shutdown complete')
    process.exit(0)
  })
  // タイムアウト：30秒以内に完了しなければ強制終了
  setTimeout(() => process.exit(1), 30_000)
})
```

---

## 外部依存のタイムアウト設定

外部APIやDBへの接続には必ずタイムアウトを設定する。
設定がないと1つの依存がハングしたとき、全リクエストが詰まる。

```typescript
// HTTP クライアント
const response = await fetch(url, {
  signal: AbortSignal.timeout(5_000),  // 5秒
})

// DB接続プール
const pool = new Pool({
  connectionTimeoutMillis: 3_000,
  idleTimeoutMillis: 30_000,
  max: 20,
})
```

---

## チェックリスト

- [ ] ログがJSON形式で出力されている
- [ ] 全ログにCorrelationIDが含まれている
- [ ] エラーが握り潰されていない（catchで必ずログ出力）
- [ ] ログにシークレット・個人情報が含まれていない
- [ ] `/health` エンドポイントが実装されている
- [ ] SIGTERMでGraceful Shutdownする
- [ ] 外部APIとDBにタイムアウトが設定されている

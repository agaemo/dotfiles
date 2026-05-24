# Socket.IO + Next.js カスタムサーバーパターン

WebSocketが必要な場合（チャット・リアルタイム通知等）は Next.js のカスタムサーバーを使う。

```
IMPORTANT: ts-node は Next.js の require-hook と干渉しTypeScriptファイルの解決に失敗することがある。
  カスタムサーバーは tsx で実行すること。
```

```bash
pnpm add -D tsx
```

```json
// package.json
{
  "scripts": {
    "dev": "tsx server.ts",
    "start": "NODE_ENV=production tsx server.ts"
  }
}
```

```ts
// server.ts（TypeScript で書く）
import { createServer } from 'http'
import { Server } from 'socket.io'
import next from 'next'

const app = next({ dev: process.env.NODE_ENV !== 'production' })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const httpServer = createServer((req, res) => handle(req, res))
  const io = new Server(httpServer, { path: '/api/socketio' })
  // Socket.IOハンドラを登録
  httpServer.listen(3000)
})
```

## httpOnly Cookie 認証

httpOnly Cookie はブラウザのJSから読めないため、ハンドシェイクでは
`withCredentials: true` でブラウザが自動送信したCookieをサーバー側でパースして検証する。

```ts
// サーバー側: socket.handshake.headers.cookie からトークンを抽出
io.use((socket, next) => {
  const cookie = socket.handshake.headers.cookie
  const token = cookie?.match(/(?:^|;\s*)token=([^;]+)/)?.[1]
  const user = token ? verifyToken(token) : null
  if (!user) return next(new Error('Unauthorized'))
  socket.data.user = user
  next()
})

// クライアント側: withCredentials: true でCookieを自動送信
const socket = io({ path: '/api/socketio', withCredentials: true })
```

## React StrictMode での二重接続対策

開発環境ではuseEffectが2回実行されるため、cancelledフラグでソケット二重生成を防ぐ。

```ts
useEffect(() => {
  let cancelled = false
  let socket: Socket | null = null

  async function init() {
    // ...fetch処理...
    if (cancelled) return
    socket = io({ path: '/api/socketio', withCredentials: true })
    socket.on('receive_message', (msg) => { ... })
  }

  init()
  return () => {
    cancelled = true
    socket?.disconnect()
  }
}, [roomId])
```

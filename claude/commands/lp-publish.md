---
name: lp-publish
description: LPを本番公開するための準備・手順をガイドする。ホスティング・ドメイン・SEOファイルの知識がなくてもWeb制作の相談相手として必要なものを揃えられるようにする。
---

# /lp-publish

LP を本番公開するための準備を、Web制作の知識がなくても進められるようガイドする。
**プロジェクトルートで実行すること。**

---

## 手順

### ステップ 1: 現状ヒアリング（メインClaude自身が実行）

> **注意:** サブエージェントはユーザーと対話できない。ヒアリングは必ずメインClaude自身が行うこと。

以下を **1つのメッセージ** でユーザーに質問する。
わからない・決めていない は「わからない」で構わない旨を必ず添える。

```
質問項目:

1. ドメイン（URL）について
   - 独自ドメイン（例: your-salon.com）を使いたいですか？
   - すでに取得済みですか？どこで取得しましたか？（例: お名前.com、Xサーバー、Squarespace など）

2. ホスティング（サーバー）について
   - どこにページを置くか決まっていますか？
   - 候補があれば教えてください（例: Vercel、Netlify、さくらのレンタルサーバー、Xサーバー など）

3. 予算・運用スキル感
   - 月あたり何円くらいまでかけられますか？（目安: 無料〜500円・500〜2000円・それ以上）
   - コマンド操作（ターミナル）に慣れていますか？

4. 公開後の更新頻度
   - 公開後に自分でページを更新する予定はありますか？

5. 今のプロジェクトの状態
   - `pnpm run build` は成功していますか？
   - Git リポジトリは初期化されていますか？（git init 済みかどうか）
```

WAIT_FOR: ユーザーの回答

---

### ステップ 2: 状況分析 & 推奨構成の提示

ヒアリング結果をもとに以下を判断し、ユーザーに **平易な言葉で** 説明する。

```
ANALYZE:

  [ホスティング推奨ロジック]
  - コマンド操作に不慣れ AND 予算が無料〜500円
      → Netlify（GUI でドラッグ&ドロップ公開が可能）を第一推奨
  - コマンド操作に慣れている OR 予算に余裕がある
      → Vercel（GitHub 連携で自動デプロイ）を第一推奨
  - すでにレンタルサーバー（さくら・Xサーバー等）を契約済み
      → FTP/SSH アップロードを案内
  - それ以外
      → Netlify を第一推奨（無料・GUI・独自ドメイン対応）

  [ドメインロジック]
  - 独自ドメイン希望 AND 未取得
      → 取得サービスを案内（お名前.com / Xserver Domain 等）
      → DNS 設定が必要になることを説明
  - 独自ドメイン希望 AND 取得済み
      → ホスティング側で DNS 設定が必要なことを説明
  - 独自ドメイン不要
      → ホスティングの無料サブドメイン（xxx.netlify.app 等）で可

SHOW USER:
  推奨構成（ホスティング + ドメイン）とその理由を平易な日本語で説明する。
  専門用語を使う場合は必ずカッコ内に一言で説明を添える。

  例:
  「Netlify（ネットリファイ）という無料サービスをおすすめします。
   ファイルをドラッグ&ドロップするだけで公開でき、独自ドメインも無料で設定できます。」

WAIT_FOR: ユーザーが推奨構成に同意する
IF NOT CONFIRMED: 別の構成を提案するか、要望を再ヒアリングする
```

---

### ステップ 3: 公開に必要なファイルの準備

ユーザーが承認した構成をもとに、以下を実施する。

#### 3-1. astro.config.mjs に site URL を設定

```
READ: astro.config.mjs

IF site プロパティが未設定 OR "https://example.com" のまま:
  ASK USER: 公開する URL を確認する
    - 独自ドメイン未取得の場合は「決まったら後で設定します」で進める
    - 仮で設定する場合は "https://your-site.netlify.app" などを使う
  EDIT astro.config.mjs:
    site: "https://ユーザーが指定したURL"
ENDIF
```

#### 3-2. @astrojs/sitemap の追加

```
RUN:
  mise exec -- pnpm add @astrojs/sitemap

EDIT astro.config.mjs:
  import sitemap from '@astrojs/sitemap' を追加
  integrations: [sitemap()] を追加

NOTE: site プロパティが設定されていないと sitemap は生成されない
```

#### 3-3. robots.txt の作成

```
WRITE public/robots.txt:

  [Netlify / Vercel / 静的ホスティングの場合]
  ---
  User-agent: *
  Allow: /

  Sitemap: https://<ユーザーのURL>/sitemap-index.xml
  ---

NOTE: Sitemap 行の URL は astro.config.mjs の site と一致させること
```

#### 3-4. ビルド確認

```
RUN:
  mise exec -- pnpm run build

ASSERT EXISTS(dist/sitemap-index.xml)
ASSERT EXISTS(dist/robots.txt)

IF FAILED:
  REPORT: エラー内容を説明し、原因と対処を案内する
  STOP
ENDIF
```

---

### ステップ 4: ホスティング別デプロイ手順の案内

推奨されたホスティングに応じて、手順を **平易な言葉で** 案内する。

```
BRANCH ON hosting:

  [Netlify - GUI の場合]
    GUIDE:
      1. https://app.netlify.com にアクセスしてアカウント作成（GitHub / Google でログイン可）
      2. "Add new site" → "Deploy manually" を選択
      3. dist/ フォルダをブラウザにドラッグ&ドロップ
      4. 数秒で公開完了。表示された URL でアクセスできることを確認
      5. 独自ドメインを使う場合は "Domain settings" から設定

  [Netlify - CLI の場合]
    RUN:
      mise exec -- pnpm add -D netlify-cli
      mise exec -- pnpm exec netlify login
      mise exec -- pnpm exec netlify deploy --prod --dir dist

  [Vercel の場合]
    RUN:
      mise exec -- pnpm add -D vercel
      mise exec -- pnpm exec vercel login
      mise exec -- pnpm exec vercel --prod
    NOTE: 初回は対話形式でプロジェクト設定が入る

  [さくら / Xサーバー / FTP の場合]
    GUIDE:
      1. ホスティング管理画面から FTP 情報（ホスト・ユーザー・パスワード）を確認
      2. FTP ソフト（例: Cyberduck、FileZilla）をインストール
      3. dist/ フォルダの中身をサーバーの public_html（または www）フォルダへアップロード
      4. ドメインの DNS 設定はホスティング会社のマニュアルを参照
    NOTE: さくら・Xサーバーは管理画面に詳細なマニュアルがあることを伝える

  [未決定の場合]
    GUIDE: Netlify の GUI 手順を案内する（最も敷居が低いため）
```

---

### ステップ 5: 独自ドメインの DNS 設定案内（該当する場合のみ）

```
IF 独自ドメインを使う:

  [ドメイン未取得の場合]
    GUIDE:
      - お名前.com / Xserver Domain / Squarespace Domains などで取得できる
      - 年間1,000〜2,000円が目安
      - 取得後にここに戻って DNS 設定を続ける

  [ドメイン取得済みの場合]
    GUIDE ホスティングに応じたネームサーバー or CNAME 設定:

      Netlify:
        - Netlify の "Domain settings" に表示される CNAME 値をコピー
        - ドメイン取得サービスの DNS 設定画面で CNAME レコードを追加
        - 反映に数分〜数時間かかる（最大 48 時間）

      Vercel:
        - vercel --prod 後に表示される DNS 設定値を使う
        - 手順は Netlify と同様

      レンタルサーバー:
        - ホスティング会社のマニュアルに従う
        - 「ネームサーバー変更」または「CNAME 設定」で検索するよう案内

  NOTE: DNS の反映待ちは避けられない。反映中は旧URLや「接続できない」状態になることがある旨を伝える
```

---

### ステップ 6: 公開確認チェックリスト

```
SHOW USER（チェックリスト形式で）:

  公開後に確認してほしいこと:

  [ ] サイトのURLにアクセスしてページが表示される
  [ ] スマートフォンでも正しく表示される
  [ ] /sitemap-index.xml にアクセスして sitemap が表示される
  [ ] /robots.txt にアクセスして内容が表示される
  [ ] Google Search Console（グーグルサーチコンソール）に URL を登録する（検索に表示されるようにするため）

  Google Search Console の登録は任意だが、検索エンジンに早く認識してもらうために推奨する。
  必要であれば登録手順も案内できる旨を伝える。
```

---

## 注意事項

- 専門用語は使うたびに平易な説明を添えること
- ユーザーが「わからない」と言ったら、責めずに最もシンプルな選択肢を提案する
- 完璧な構成より「まず公開できる状態」を優先する
- 設定ファイルを変更した場合は必ず `pnpm run build` で確認してから案内する

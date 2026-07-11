# output-brief

アウトプットを伴うタスクで、**形式・保存先・スタイルをユーザーと確認してから出力まで担当する**スキル。

---

## 概要

「一覧化して」「HTMLで出力して」「〜について調べて出力して」などの指示を受けたとき、作り始める前にブリーフィング（方針確認）を行い、承認を得てから出力する。
データ・素材が無い、または不十分・曖昧な場合は `WebSearch` / `WebFetch` で調べてから方針確認に進む。
形式・保存先・内容が**全て明示済みの場合は使わず直接出力する**。

### 使う状況

| 状況 | 使う / 使わない |
|------|----------------|
| 保存先（ファイル / チャット表示）が未指定 | 使う |
| 出力形式（HTML / Markdown / CSV…）が未指定 | 使う |
| HTMLでレイアウト・カラーが未指定 | 使う |
| コンテンツ内容・構成が不明 | 使う |
| データ・素材が無い、または不十分・曖昧 | 使う（調査してから出力） |
| 形式・保存先・内容が全て明示されている | **使わない（直接出力）** |

---

## フロー

```
データ確認（ステップ1）
  ↓ 不明点があれば1回で質問
  ↓ 素材が無い・不十分な場合は WebSearch/WebFetch で調査
ブリーフィング（ステップ2）
  ↓ 調査した場合は要約を提示して内容を確認
  ↓ テキストの番号リストで選択肢を提示
承認（ステップ3）
  ↓ WAIT_FOR: ユーザーの承認を受けてから
出力（ステップ4）
  ↓ Write ツール / コードブロック
完了報告
```

発動判断で全て指定済みと判断した場合は、ステップ1〜3をスキップしてステップ4へ直行する。

---

## 調査（リサーチ）

データ・素材が無い、または不十分・曖昧な場合にステップ1で行う。

| ケース | 対応 |
|--------|------|
| 素材が指定されていない（「〜について調べて出力して」等） | `WebSearch` / `WebFetch` で調べる |
| 素材はあるが情報が不足・曖昧 | 不足分を `WebSearch` / `WebFetch` で補う |
| 調査範囲が広い・情報源が乏しい | 調査前に番号リストで対象・観点を確認 |

調査結果はステップ2のブリーフィングで要約（出典・主要な事実）を提示し、内容が正しいか確認してから後続のフォーマット確認に進む。

---

## 対応フォーマット

### HTML

レイアウトとカラーテーマをテキストの番号リストで選択し、サンプルを確認してから生成する。

#### レイアウト

| カテゴリ | レイアウト | 説明 | 向いているコンテンツ |
|---------|-----------|------|-------------------|
| 一覧 | `simple-list` | 行ごとに縦一覧 | テキスト中心・情報量が多い |
| 一覧 | `panel` | カードグリッド | 同程度の重要度の項目 |
| 文書 | `article` | 本文・見出し・コード・引用 | Markdown 的な構造のドキュメント |
| 表 | `table` | データ比較表 | 複数項目を列ごとに比較するコンテンツ |
| プレゼン | `slide` | 1セクション1枚の枠付きカードを横スクロールで送るスライド（全画面表示トグル付き） | 提案・報告・ピッチ資料 |

#### カラーテーマ

| テーマ | 配色 | 印象 |
|--------|------|------|
| `warm`  | オレンジ・ベージュ | 温かみ |
| `cool`  | パープル・ラベンダー | 落ち着き |
| `blue`  | 青系 | 清潔感・信頼 |
| `green` | 緑系 | 自然・安心 |
| `dark`  | 暗い背景 | モダン・集中 |
| `light` | 白ベース | シンプル・クリーン |

#### サンプル

##### simple-list

| warm | cool | blue |
|------|------|------|
| [![](assets/previews/simple-list-warm.png)](assets/previews/simple-list-warm.png) | [![](assets/previews/simple-list-cool.png)](assets/previews/simple-list-cool.png) | [![](assets/previews/simple-list-blue.png)](assets/previews/simple-list-blue.png) |

| green | dark | light |
|-------|------|-------|
| [![](assets/previews/simple-list-green.png)](assets/previews/simple-list-green.png) | [![](assets/previews/simple-list-dark.png)](assets/previews/simple-list-dark.png) | [![](assets/previews/simple-list-light.png)](assets/previews/simple-list-light.png) |

##### panel

| warm | cool | blue |
|------|------|------|
| [![](assets/previews/panel-warm.png)](assets/previews/panel-warm.png) | [![](assets/previews/panel-cool.png)](assets/previews/panel-cool.png) | [![](assets/previews/panel-blue.png)](assets/previews/panel-blue.png) |

| green | dark | light |
|-------|------|-------|
| [![](assets/previews/panel-green.png)](assets/previews/panel-green.png) | [![](assets/previews/panel-dark.png)](assets/previews/panel-dark.png) | [![](assets/previews/panel-light.png)](assets/previews/panel-light.png) |

##### article

| warm | cool | blue |
|------|------|------|
| [![](assets/previews/article-warm.png)](assets/previews/article-warm.png) | [![](assets/previews/article-cool.png)](assets/previews/article-cool.png) | [![](assets/previews/article-blue.png)](assets/previews/article-blue.png) |

| green | dark | light |
|-------|------|-------|
| [![](assets/previews/article-green.png)](assets/previews/article-green.png) | [![](assets/previews/article-dark.png)](assets/previews/article-dark.png) | [![](assets/previews/article-light.png)](assets/previews/article-light.png) |

##### table

| warm | cool | blue |
|------|------|------|
| [![](assets/previews/table-warm.png)](assets/previews/table-warm.png) | [![](assets/previews/table-cool.png)](assets/previews/table-cool.png) | [![](assets/previews/table-blue.png)](assets/previews/table-blue.png) |

| green | dark | light |
|-------|------|-------|
| [![](assets/previews/table-green.png)](assets/previews/table-green.png) | [![](assets/previews/table-dark.png)](assets/previews/table-dark.png) | [![](assets/previews/table-light.png)](assets/previews/table-light.png) |

##### slide

| warm | cool | blue |
|------|------|------|
| [![](assets/previews/slide-warm.png)](assets/previews/slide-warm.png) | [![](assets/previews/slide-cool.png)](assets/previews/slide-cool.png) | [![](assets/previews/slide-blue.png)](assets/previews/slide-blue.png) |

| green | dark | light |
|-------|------|-------|
| [![](assets/previews/slide-green.png)](assets/previews/slide-green.png) | [![](assets/previews/slide-dark.png)](assets/previews/slide-dark.png) | [![](assets/previews/slide-light.png)](assets/previews/slide-light.png) |

---

### Markdown

番号リストで以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 見出し構造 | フラット（H2 のみ）/ 階層あり（H2 + H3） |
| テーブル | あり / なし |
| コードブロック | あり / なし |

保存先はステップ1（データ確認）で確定済みのため再確認しない。

---

### CSV

番号リストで以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 区切り文字 | カンマ / タブ |
| ヘッダ行 | あり / なし |
| 文字コード | UTF-8 / Shift-JIS |

---

### JSON

番号リストで以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 構造 | 配列 / オブジェクト（キーあり） |
| インデント | あり（2スペース）/ なし（minified） |

---

### その他のフォーマット

形式・主要構成（セクション・項目）を列挙して確認する。不明点は1回でまとめて質問する。

---

## 設計メモ

- **ブリーフィングは必ずテキストの番号リストで行う** — `AskUserQuestion` は使わない（選択肢数の上限がなく、6色のカラーテーマも一度に提示できる）
- **承認なしに出力しない** — `WAIT_FOR` → 承認 → `Write` の順序を守る
- **修正は最大3ラウンド** — 収束しない場合は中断してユーザーに方向性を確認する
- **出力後は存在確認** — ファイル保存後にパスの存在を確認してから報告する
- **調査結果も出力前に要約確認する** — 調べた内容を出力に直結させず、ステップ2で正しさを確認してから先に進む

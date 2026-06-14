# output-brief

アウトプットを伴うタスクで、**形式・保存先・スタイルをユーザーと確認してから出力まで担当する**スキル。

---

## 概要

「一覧化して」「HTMLで出力して」などの指示を受けたとき、作り始める前にブリーフィング（方針確認）を行い、承認を得てから出力する。  
形式・保存先・内容が**全て明示済みの場合は使わず直接出力する**。

### 使う状況

| 状況 | 使う / 使わない |
|------|----------------|
| 保存先（ファイル / チャット表示）が未指定 | 使う |
| 出力形式（HTML / Markdown / CSV…）が未指定 | 使う |
| HTMLでレイアウト・カラーが未指定 | 使う |
| コンテンツ内容・構成が不明 | 使う |
| 形式・保存先・内容が全て明示されている | **使わない（直接出力）** |

---

## フロー

```
データ確認（ステップ1）
  ↓ 不明点があれば1回で質問
ブリーフィング（ステップ2）
  ↓ AskUserQuestion で選択肢を提示
承認（ステップ3）
  ↓ WAIT_FOR: ユーザーの承認を受けてから
出力（ステップ4）
  ↓ Write ツール / コードブロック
完了報告
```

発動判断で全て指定済みと判断した場合は、ステップ1〜3をスキップしてステップ4へ直行する。

---

## 対応フォーマット

### HTML

レイアウトとカラーテーマを `AskUserQuestion` で1回選択し、サンプルを確認してから生成する。

#### レイアウト

| レイアウト | 説明 | 向いているコンテンツ |
|-----------|------|-------------------|
| `simple-list` | 行ごとに縦一覧 | テキスト中心・情報量が多い |
| `panel` | カードグリッド | 同程度の重要度の項目 |

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

---

### Markdown

`AskUserQuestion` で以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 見出し構造 | フラット（H2 のみ）/ 階層あり（H2 + H3） |
| テーブル | あり / なし |
| コードブロック | あり / なし |

保存先はステップ1（データ確認）で確定済みのため再確認しない。

---

### CSV

`AskUserQuestion` で以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 区切り文字 | カンマ / タブ |
| ヘッダ行 | あり / なし |
| 文字コード | UTF-8 / Shift-JIS |

---

### JSON

`AskUserQuestion` で以下を確認する。

| 項目 | 選択肢 |
|------|--------|
| 構造 | 配列 / オブジェクト（キーあり） |
| インデント | あり（2スペース）/ なし（minified） |

---

### その他のフォーマット

形式・主要構成（セクション・項目）を列挙して確認する。不明点は1回でまとめて質問する。

---

## 設計メモ

- **ブリーフィングは必ず `AskUserQuestion` で行う** — テキスト羅列は使わない
- **承認なしに出力しない** — `WAIT_FOR` → 承認 → `Write` の順序を守る
- **修正は最大3ラウンド** — 収束しない場合は中断してユーザーに方向性を確認する
- **出力後は存在確認** — ファイル保存後にパスの存在を確認してから報告する

# ideate — アイデア・提案生成

**使用条件:** 「〇〇のアイデアを出してほしい」「〇〇をどう改善できるか」など、新しいアイデア・解決策の生成が目的のときに使う。既存案の検証・矛盾解消・変形には向かない（後述参照）。

Jobs-to-be-Done（Christensen et al., 2016）で問題を定式化し、
Design Thinking の発想フェーズ（Brown, 2008; Stanford d.school）でアイデアを生成する。

job-mapper（JTBD定式化）→ synectics-analogist（類推）→ dt-ideator（発想）の3段階逐次処理で、
「誰の何の困りごとを解決するか」を軸に具体的な提案を返す。

```
SKILL_DIR = このSKILL.mdが置かれているディレクトリ（= .../think/ideate/）
think から委譲された場合も SKILL_DIR は ideate/ を指す。
agents/ の参照は常に {SKILL_DIR}/agents/<name>.md とする。
```

## このスキルでできること・できないこと

**向いている入力:**
- 「〇〇のアイデアを出してほしい」という新規発想
- 「〇〇をどう改善できるか」という課題起点の提案生成
- ターゲットや背景が多少曖昧でも受け付ける

**向いていない入力（受け付けない）:**
- 既存の提案を検証・評価したい（→ six-hats）
- 矛盾・トレードオフを解消したい（→ triz）
- 常識を疑いゼロから再構築したい（→ first-principles）
- 変形元の対象が明確で改良・発展させたい（→ scamper）

---

## 引数の処理

- **`{input}` あり**: NG判定を行う（下記参照）
- **`{input}` なし**: 「どんな課題や状況についてアイデアを出しますか?」と一言聞く
- **`{verbosity}`**: think から渡される。渡されていない場合は 標準 とする

### NG判定（1つでも該当したら代替を1文で提案してSTOP）

1. 具体的な提案・計画の検証が目的 → six-hats を提案
2. 矛盾・トレードオフの解消が目的 → triz を提案
3. 常識を疑うゼロベース再構築が目的 → first-principles を提案
4. 変形する既存の対象が明確に含まれている → scamper を提案

NG時: 「〇〇が目的であれば `<スキル名>` が向いています。」と1文で伝えてSTOP。
OK判定の場合のみ以降に進む。

---

## ブリーフィング（補足情報収集）

分析精度を高めるために補足情報を収集する。以下の質問を出力してから WAIT_FOR: ユーザーの回答。
「スキップ」「省略」と返答された場合は `{context}` = "" としてステップ1に進む。

1. **すでに試したこと**: 検討・却下済みのアプローチがあれば（なければ「なし」）
2. **対象ユーザー・ステークホルダー**: 誰が使うか・影響を受けるか（組織・役割・状況を含めて）
3. **優先したい制約**: コスト・期間・技術・組織など、アイデアの実現を制限する条件があれば

ユーザーの回答を `{context}` として保持し、変数 `{enriched_input}` を定義する:
- `{context}` が空でない場合: `{enriched_input}` = `{input}` の末尾に `\n\n## 補足情報\n{context}` を追加したもの
- `{context}` が空の場合: `{enriched_input}` = `{input}`

IMPORTANT: 以降のすべてのエージェント起動では `{input}` の代わりに `{enriched_input}` を使うこと。対話フェーズのagent再起動でも同様。

---

## ステップ1: 3エージェントを逐次起動

IMPORTANT: エージェント実行中・結果待ちの間、会話上にテキストを出力しないこと。

1. `{SKILL_DIR}/agents/job-mapper.md` を READ し、`{enriched_input}` を置換したプロンプトで Agent 起動する（同期実行）。完了したら出力全文を `{jtbd_analysis}` として保持する。
   - 失敗した場合: `{jtbd_analysis}` = "（取得失敗）" として次に進む。
2. `{SKILL_DIR}/agents/synectics-analogist.md` を READ し、`{enriched_input}` と `{jtbd_analysis}` を置換したプロンプトで Agent 起動する（同期実行）。完了したら出力全文を `{analogy_result}` として保持する。
   - 失敗した場合: `{analogy_result}` = "" として次に進む。
3. `{SKILL_DIR}/agents/dt-ideator.md` を READ し、`{enriched_input}` と `{jtbd_analysis}` と `{analogy_result}` を置換したプロンプトで Agent 起動する（同期実行）。完了したら出力全文を `{ideation_result}` として保持する。
   - 失敗した場合: 「アイデア生成を完了できませんでした。再度お試しください。」と伝えてSTOP。

---

## ステップ2: 統合・出力

`{ideation_result}` の全アイデアを対象に、最も有望な案を verbosity に応じた数・形式で出力する。

有望度の判断基準:
- `{jtbd_analysis}` の「望ましい成果」に近いか
- 異なる視点軸から選ばれているか（偏りを防ぐ）
- 実行可能性があるか

### verbosity に応じた出力

デフォルト保存先: `{SKILL_DIR}/../`（= think/ 直下）

| verbosity | 会話上の出力 | ファイル保存 |
|---|---|---|
| 簡潔 | マインドマップ + 案リスト | なし |
| 標準 | マインドマップ + 案リスト（詳細） | 保存先を聞く（省略時はデフォルト先） |
| 詳細 | マインドマップ + JTBD + HMW + 案リスト（詳細） | 保存先を聞く（省略時はデフォルト先） |

verbosity = 簡潔 の場合: ファイル保存は行わない。会話上に以下の形式で出力し、ステップ3（対話）に進む。

````markdown
```mermaid
mindmap
  root((**{inputの冒頭15字}**))
    コアジョブ
      {コアジョブの要約10字以内}
    ユーザー視点
      {該当案タイトル}
    技術・手段視点
      {該当案タイトル}
    ビジネス・運用視点
      {該当案タイトル}
    逆張り視点
      {該当案タイトル}
    類推視点
      {該当案タイトル（analogy_resultが空の場合はこのノードを省略）}
```

案1: <タイトル15字以内> — <一文説明>
案2: ...
案3: ...
（3〜5案）
````

verbosity = 標準 の場合: まず会話上にマインドマップ + 案リスト（詳細）を出力する。
mindmap は簡潔と同じ形式で出力する。案リストは以下の形式:

**案1: <タイトル15字以内>**（[視点軸] / HMW[番号]）
<2文の説明。ジョブとの対応を含む>

**案2: ...**（3〜5案）

verbosity = 詳細 の場合: まず会話上に以下を出力する。フォーマットはファイル保存フォーマット（後述）と同一とする。
- mindmap（簡潔と同じ形式）
- JTBD 定式化サマリー（{jtbd_analysis} の要点 3〜4行）
- How Might We 質問一覧
- アイデア（上位3〜5案）：視点軸・HMW番号・2〜3文説明・実行ステップ

会話上の出力が完了したら、「保存先のパスを教えてください（デフォルト: {SKILL_DIR}/../）」と一言聞く。
WAIT_FOR: ユーザーの回答
「保存しない」「スキップ」と言われた場合はファイル保存をスキップしてステップ3に進む。
ユーザーが答えたパスに対し:

1. Bash で `date +%Y%m%d-%H%M` を実行してファイル名用タイムスタンプを、`date +%Y-%m-%d` を実行してレポートタイトル用日付をそれぞれ取得する。ファイル名は `ideate-<YYYYMMdd-HHmm>.md`（例: ideate-20260530-1430.md）とする
2. 指定パスが存在しない場合は Bash で `mkdir -p <path>` を実行してから保存する
3. Write ツールで保存する

パスが省略されたり「ここ」「カレント」と言われた場合はデフォルト先に保存する。

---

Write 直前に `{SKILL_DIR}/templates/report.md` を READ し、`{input}` `{jtbd_analysis}` `{analogy_result}` `{ideation_result}` `{YYYY-MM-DD}` を置換したものを保存内容とする。

ファイル保存後、会話上には「`{実際の保存フルパス}` に保存しました」と一言だけ伝える（verbosity = 簡潔 の場合は案リストの後に添える）。

---

## ステップ3: 対話

- 「案Nを深掘りして」→ その案の詳細・実行ステップを会話上のみ展開
- 「別の角度から出して」→ `{ideation_result}` から使用済み視点軸を確認する。未使用の軸がある場合は明示してから `{SKILL_DIR}/agents/dt-ideator.md` を READ して `{enriched_input}` と `{jtbd_analysis}` と `{analogy_result}` で Agent 起動し、出力を `{ideation_result}` に追記して新しいアイデアを出力する。全視点軸が使用済みの場合は「すべての視点軸を網羅しました。」と伝える。
- 「このアイデアのリスクは?」→ six-hats での検証を提案
- 「JTBDを見直したい」→ `{SKILL_DIR}/agents/job-mapper.md` を READ して `{enriched_input}` で Agent 起動し（同期実行）、出力で `{jtbd_analysis}` を更新する。続けて `{SKILL_DIR}/agents/synectics-analogist.md` を READ して `{enriched_input}` と `{jtbd_analysis}` で Agent 起動し（同期実行）、出力で `{analogy_result}` を更新する。続けて `{SKILL_DIR}/agents/dt-ideator.md` を READ して `{enriched_input}` と `{jtbd_analysis}` と `{analogy_result}` で Agent 起動し（同期実行）、出力で `{ideation_result}` を更新する。ステップ2を再実行する。
- 「終わり」→ 簡潔に締める
- その他 → 生成したアイデアと JTBD 定式化を踏まえて回答する

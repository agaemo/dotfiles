# Wardley Mapping — 戦略的ポジション分析

Simon Wardley が開発した戦略マッピング手法（2005〜）。
バリューチェーン（ユーザーニーズ → コンポーネント）と進化軸（Genesis → Custom → Product → Commodity）で
コンポーネントを可視化し、内製・外注・廃止・差別化の戦略的判断を導く。

```
WARDLEY_DIR = スキル起動時に提供される "Base directory for this skill:" のパス
```

## このスキルでできること・できないこと

**向いている入力:**
- 事業・製品・システムの構造を戦略的に可視化したい
- 何を内製/外注/廃止すべきかを判断したい
- 競合との差別化ポイントを見極めたい
- 組織・投資の優先度を整理したい

**向いていない入力（受け付けない）:**
- まだ対象が何もない新規発想（→ ideate）
- 矛盾・トレードオフの解消（→ triz）
- 具体的な提案・計画の多角的検証（→ six-hats）
- 前提を疑いゼロから再構築したい（→ first-principles）

---

## 引数の処理

- **引数あり**: 入力の適切性を判定する（下記参照）
- **引数なし**: 「何の戦略マップを作りますか? 例：「ECサイト事業」「IoTプラットフォームの開発体制」」と一言聞く
- **`{verbosity}`**: think から渡される。渡されていない場合は 標準 とする

### 入力の適切性判定

**NG判定の条件（1つでも該当したら断る）:**
1. 分析対象（事業・製品・システム・業務）が何も含まれていない
2. アイデアを出してほしいという新規発想が目的 → ideate を提案
3. 矛盾・トレードオフの解消が目的 → triz を提案

NGの場合:
```
Wardley Mapping は「既存の事業・製品・システムの戦略的構造」を可視化する手法です。
今の入力「{input}」は[NG理由]のため、Wardley Mapping には向いていません。
[代替スキルの提案]
```

OK判定の場合のみ以降に進む。以降、分析対象を `{input}` と呼ぶ。

---

## ブリーフィング（補足情報収集）

分析精度を高めるために補足情報を収集する。以下の質問を出力してから WAIT_FOR: ユーザーの回答。
「スキップ」「省略」と返答された場合は `{context}` = "" としてステップ1に進む。

1. **ユーザー・顧客**: 最終的な価値を受け取るのは誰か（エンドユーザー・社内利用者・取引先など）
2. **分析の目的**: 今回マッピングすることで何を決めたいか（内製/外注判断・投資優先度・競合比較など）
3. **既知の課題やモヤモヤ**: すでに「ここをどうすべきか」と迷っている箇所があれば

ユーザーの回答を `{context}` として保持し、変数 `{enriched_input}` を定義する:
- `{context}` が空でない場合: `{enriched_input}` = `{input}` の末尾に `\n\n## 補足情報\n{context}` を追加したもの
- `{context}` が空の場合: `{enriched_input}` = `{input}`

IMPORTANT: 以降のすべてのエージェント起動では `{input}` の代わりに `{enriched_input}` を使うこと。対話フェーズのagent再起動でも同様。

---

## ステップ1: バリューチェーンの抽出

`{WARDLEY_DIR}/agents/chain-mapper.md` を READ し、`{enriched_input}` を置換して Agent 起動する（同期実行）。
完了したら出力全文を `{chain_result}` として保持し、ステップ2に進む。
エージェントが失敗した場合は「バリューチェーンの抽出を完了できませんでした。再度お試しください。」と伝えてSTOP。

---

## ステップ2: 進化段階の評価

`{WARDLEY_DIR}/agents/evolution-assessor.md` を READ し、`{enriched_input}` と `{chain_result}` を置換して Agent 起動する（同期実行）。
完了したら出力全文を `{evolution_result}` として保持し、ステップ3に進む。
エージェントが失敗した場合は「進化段階の評価を完了できませんでした。再度お試しください。」と伝えてSTOP。

---

## ステップ3: 戦略的インサイトの導出

`{WARDLEY_DIR}/agents/strategy-synthesizer.md` を READ し、`{enriched_input}` と `{chain_result}` と `{evolution_result}` を置換して Agent 起動する（同期実行）。
完了したら出力全文を `{strategy_result}` として保持し、ステップ4に進む。
エージェントが失敗した場合は「戦略的インサイトの導出を完了できませんでした。再度お試しください。」と伝えてSTOP。

---

## ステップ4: 統合・出力

3フェーズの結果を受け取り、以下の内容を組み立てる。

### verbosity に応じた出力

| verbosity | 会話上の出力 | ファイル保存 |
|---|---|---|
| 簡潔 | Wardley Map + 戦略的アクション TOP 3 | なし |
| 標準 | Wardley Map + コンポーネント表 + 戦略的推奨 | 保存先を聞く |
| 詳細 | Wardley Map + コンポーネント表 + 全フェーズ詳細 + 戦略的推奨 | 保存先を聞く |

PROHIBITED: ユーザーの保存先確認なしにファイルを書くこと

verbosity = 簡潔 の場合: ファイル保存は行わない。`{evolution_result}` の「Wardley Map（テキスト表現）」セクションと `{strategy_result}` の「優先度の高いアクション（TOP 3）」セクションを会話上に出力し、ステップ5（対話）に進む。
verbosity = 標準 / 詳細 の場合: 「保存先のパスを教えてください（例: ~/Desktop）」と一言聞く。ユーザーが答えたパスに対し:

1. Bash で `date +%Y%m%d-%H%M` を実行してタイムスタンプを、`date +%Y-%m-%d` を実行して日付をそれぞれ取得する。ファイル名は `wardley-<YYYYMMdd-HHmm>.md` とする
2. 指定パスが存在しない場合は Bash で `mkdir -p <path>` を実行してから保存する
3. Write ツールで保存する
4. Bash で `test -f <保存フルパス> && echo OK` を実行しファイルの存在を確認する。失敗した場合は Write を再試行する（最大1回）。

パスが省略されたり「ここ」「カレント」と言われた場合は `{WARDLEY_DIR}/../`（= think/ 直下）に保存する。

---

Write 直前に `{WARDLEY_DIR}/templates/report.md` を READ し、`{enriched_input}` `{chain_result}` `{evolution_result}` `{strategy_result}` `{YYYY-MM-DD}` を置換したものを保存内容とする。

---

ファイル保存後、会話上には「`{実際の保存フルパス}` に保存しました」と一言伝える。
verbosity = 詳細 の場合は `{chain_result}` `{evolution_result}` `{strategy_result}` の全内容を会話上に出力する。それ以外は詳細フェーズを会話上には出力しない。

---

## ステップ5: 対話

- 「このコンポーネントをもっと詳しく」→ ユーザーの発話からコンポーネント名を `{target_component}` として抽出する。特定できない場合は「どのコンポーネントについて詳しく評価しますか？」と聞き、返答を `{target_component}` とする。`{WARDLEY_DIR}/agents/evolution-assessor.md` を READ し、`{enriched_input}` `{chain_result}` を置換し、プロンプト末尾に「特に `{target_component}` を詳細に評価してください」を追記して Agent 起動する（同期実行）。失敗した場合は「詳細取得に失敗しました。再度お試しください。」と伝えて対話を継続する。結果を会話上のみ出力
- 「進化方向を予測して」→ `{WARDLEY_DIR}/agents/strategy-synthesizer.md` を READ し、`{enriched_input}` `{chain_result}` `{evolution_result}` を置換し、プロンプト末尾に「3〜5年後の進化段階の変化と戦略的影響を予測してください」を追記して Agent 起動する（同期実行）。失敗した場合は「詳細取得に失敗しました。再度お試しください。」と伝えて対話を継続する。結果を会話上のみ出力
- 「外注候補を整理して」→ `{evolution_result}` の進化段階テーブルから Product / Commodity のコンポーネントを抽出し、以下の形式で会話上のみ出力する:
  | コンポーネント | 進化段階 | 推奨アクション候補 |
  |---|---|---|
  | [名前] | Product/Commodity | [SaaS/OSS/クラウド移行等] |
- 「この計画のリスクは?」→ six-hats での検証を提案
- 「終わり」→ 簡潔に締める
- その他 → 生成したマップと戦略的インサイトを踏まえて回答する

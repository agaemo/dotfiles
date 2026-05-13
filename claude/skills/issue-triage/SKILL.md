---
name: issue-triage
description: GitHub issue番号を渡すと対応方針を検討し、承認を得てから修正・PR作成まで行う。forager:humanラベルのissueや通常のバグ・改善issueに使う。
---

## 入力

```
/issue-triage                                    # issue一覧を表示して選択
/issue-triage {issue番号}                        # 直接トリアージ
/issue-triage {issue番号} {owner/repo}           # リポジトリ指定

フィルターオプション（issue番号なしのときに使用）：
  --label, -l {label}       ラベルでフィルター（複数指定可）
  --assignee, -a {user}     アサインでフィルター
  --state {open|closed}     状態でフィルター（デフォルト: open）
  --milestone {name}        マイルストーンでフィルター
  --limit, -L {n}           表示件数（デフォルト: 20）
```

例：
```
/issue-triage --label bug
/issue-triage --label forager:human --state open
/issue-triage --assignee @me
/issue-triage 42 owner/repo
```

## プロセス

### ステップ 0：入力を解釈する

1. 引数を解析する：
   - 最初のトークンが数字なら `{issue番号}` として扱い、**ステップ 1** へ進む
   - それ以外はフィルターオプションとして扱い、**ステップ 0-A** へ進む
2. `{owner/repo}` を確定させる：
   - 引数で指定された場合はそれを使う
   - 省略された場合は `gh repo view --json nameWithOwner -q .nameWithOwner` で取得する

### ステップ 0-A：issue 一覧を表示して選ばせる（issue番号が省略された場合）

オプションを組み立てて `gh issue list` を実行する：

```bash
gh issue list --repo {owner/repo} \
  [--label {label} ...] \
  [--assignee {user}] \
  [--state {state}] \
  [--milestone {name}] \
  --limit {n} \
  --json number,title,labels,assignees,createdAt \
  --jq '.[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(", "))]"'
```

結果を表示したあと、ユーザーに番号を入力させる：

```
{n}件のissueが見つかりました：

#42 タイトル [bug, forager:human]
#38 タイトル [enhancement]
...

トリアージするissue番号を入力してください（q で中断）：
```

- `q` または空白の場合は中断して終了する
- 番号が入力されたら `{issue番号}` を確定し、**ステップ 1** へ進む
- 該当 issue が 0 件の場合はその旨を伝えて終了する

### ステップ 1：issue を読む

```bash
gh issue view {issue番号} --repo {owner/repo} --json number,title,body,labels,comments
```

### ステップ 2：内容を分析する

1. issue body に記載されているファイルパスがあれば、そのファイルを**全体**読む。
   - importの削除・変更を伴う修正の場合は、削除するシンボルがファイル内の他の箇所でも使われていないことを grep で確認する：
     ```bash
     grep -n "シンボル名" path/to/file.ts
     ```
2. 以下の観点で評価する：

| 観点 | 確認内容 |
|------|----------|
| **カテゴリ** | バグ / コードスメル / 型・ドキュメント不足 / デッドコード / 機能追加 |
| **影響範囲** | 変更が必要なファイル数・モジュール数 |
| **リスク** | 動作変更を伴うか / テストが必要か / ビジネスロジックの理解が必要か |
| **複雑度** | 自己完結しているか / 他の変更との依存があるか |

### ステップ 3：対応方針を提示してユーザーに確認する

分析結果をもとに、以下のいずれかを推奨する：

#### A. 直接修正（シンプル・安全）

条件：1〜3ファイル以内、動作変更なし、リバート容易

```
【推奨】直接修正

対象：{ファイルパス:行番号}
修正内容：{before → after のコードを明示する}
リスク：低（{理由}）

修正してPRを作成しますか？ (y/N/wontfix)
- y → ステップ4-A へ
- wontfix → ステップ4-C へ
```

修正内容の提示では、変更前・変更後のコードをコードブロックで明示すること（テキスト説明のみ不可）。

承認後、実際の diff を提示してもう一度確認を取る（2段階承認）。

#### B. 計画が必要

条件：複数ファイル連動 / ロジック変更 / アーキテクチャ判断が必要

```
【要検討】計画が必要

理由：{なぜシンプルに直せないか}
検討事項：
  - {論点1}
  - {論点2}

実装ステップ（案）：
  1. {ステップ1 — 対象ファイル・変更内容}
  2. {ステップ2 — 対象ファイル・変更内容}

この方針で進めますか？ (y/N/wontfix)
```

#### C. wontfix

条件：意図的な設計 / コスト対効果が低い / フレームワーク制約による回避策

```
【wontfix推奨】

理由：{なぜ修正不要か}

issueをcloseしますか？ (y/N)
```

### ステップ 4：承認されたら実行する

**A（直接修正）が承認された場合：**

1. 修正対象ファイルを変更するオープンPRがないか確認する：
   ```bash
   gh pr list --state open --json number,title,files \
     --jq '.[] | select(.files[].path == "対象ファイルパス") | "#\(.number) \(.title)"'
   ```
   該当するPRがある場合はその旨をユーザーに伝え、マージ後に再実行するか確認する。
2. mainに戻ってからブランチを切る：
   - slug: issueタイトルから英数字トークンを最大3つ選びケバブケースに（`[UNSAFE]` 等の角括弧プレフィックスは除外。日本語のみのタイトルは英数字部分のみ抽出し、なければ issue番号のみ使う）
   - 命名規則：`fix/{issue番号}-{slug}`
   - 例：`fix/47-incidentform-error-ignored`
   ```bash
   git switch main
   git checkout -b fix/{issue番号}-{slug}
   ```
3. 修正を適用する
4. 修正内容（変更ファイルと diff）をユーザーに提示し確認を取る：
   ```
   以下の変更をコミット・リモートにpushします：
   {diff の概要}

   この内容をコミット・pushしますか？ (y/N)
   ```
   - N を選択した場合: `git switch main && git branch -D {branch}` を実行して報告し、停止する
   PROHIBITED: 上記の diff 確認（y/N）を得ずにコミット・pushすること
5. 承認されたらビルド・テストを実行する：
   - `.forager/config.json` が存在すれば `picker.validateCommand` を読んで使う
   - なければ `package.json` の `scripts.build` を試み、それもなければ `tsc --noEmit` を実行する
   - ビルド失敗時: `git switch main && git branch -D {branch}` を実行してその旨を報告し、停止する
6. 問題なければコミット・pushしてPR作成、その後mainに戻る：
   ```bash
   git push -u origin {branch}
   gh pr create \
     --title "fix: {issueタイトルをそのまま使う。[UNSAFE]/[SMELL]等の角括弧プレフィックスは除外。70字超の場合は要約}" \
     --body "$(cat <<'EOF'
   ## Summary
   
   {修正内容を1文で}
   
   Closes #{issue番号}
   EOF
   )"
   git switch main
   ```

**B（計画が必要）が承認された場合：**

1. 各ステップを1PR単位で順番に実装する：
   - ブランチ命名規則: `fix/{issue番号}-step{n}-{slug}`
   - 各ステップ開始前に `git switch main` してから新ブランチを切る
   - ブランチ切る → 修正 → diff 確認 → ビルド → PR作成 → `git switch main` → 次のステップへ
2. 全ステップ完了後に「完了した PR 一覧」を報告する

**C（wontfix）が承認された場合：**

```bash
gh issue close {issue番号} --reason "not planned"
gh issue comment {issue番号} --body "意図的な設計のためcloseします。{理由}"
```

## ルール

- 修正前に必ずユーザーの承認を取ること。サイレントに変更しない
- 承認なしに `wontfix` でcloseしない
- 修正内容は最小限にとどめる。issueのスコープを超えた変更はしない
- ビルドが通らない場合は変更を戻してその旨を報告する

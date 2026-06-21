---
name: scope
description: 種別（kind）の推定・確認・振り分けを一括で担当する。会話から明確に推定できる場合は一言確認して new-static / new-project / new-app / consult へ直接委譲し、不明確な場合（または確認が否定された場合）は要件・制約をヒアリングして振り分ける。/craft のステップ0から常に呼び出される。
---

# scope（種別確認・技術カテゴリ選定フロー）

```
SKILL_DIR = このSKILL.md（craft/flows/scope/SKILL.md）のパスから2階層上の絶対パス
  # このファイルを /Users/alice/.claude/skills/craft/flows/scope/SKILL.md で読んだ場合
  #      → SKILL_DIR = /Users/alice/.claude/skills/craft
```

---

## 手順

### ステップ 0: 種別の推定・確認（ショートカット）

```
# 会話の文脈から種別を推定する（ユーザーに聞き直さない）
INFER kind FROM 直前の会話内容:
  キーワード例:
    1（静的サイト）  → LP・ランディングページ・PoC・画面モック・静的
    2（Webアプリ）   → API・DB・認証・バックエンド・Next.js・サーバー・チャット・管理画面
    3（アプリ）      → Flutter・React Native・Expo・iOS・Android・スマホアプリ
    4（既存相談）    → 移行・改善・リファクタ・相談・課題・既存

IF kind が明確に推定できる:
  CONFIRM: 「〇〇（種別名）で進めますか？」と一言確認する
  IF ユーザーが承認した:
    委譲先 = (kind に応じて以下のいずれか)
      1 → {SKILL_DIR}/flows/new-static/SKILL.md
      2 → {SKILL_DIR}/flows/new-project/SKILL.md
      3 → {SKILL_DIR}/flows/new-app/SKILL.md
      4 → {SKILL_DIR}/flows/consult/SKILL.md
    READ 委譲先
    IF READ FAILED:
      REPORT: "フローファイルが見つかりません: {委譲先}。SKILL_DIR の導出を確認してください。"
      STOP
    FOLLOW: そこに記述されたすべての手順を実行する
    STOP
  ELSE:
    # 推定が外れた → ステップ1（自由ヒアリング）へ
ENDIF
# kind が推定できない場合も、そのままステップ1へ
```

### ステップ 1: 相談の入口

```
ASK USER:
  何を作りたいか、または困っていることを自由に話してください。

WAIT_FOR: ユーザーの話

IF 話の内容が既存システムへの課題・移行・リファクタ等（既存システムの相談）:
  READ {SKILL_DIR}/flows/consult/SKILL.md
  FOLLOW: そこに記述されたすべての手順を実行する
  STOP

# 新規構築と判断した場合のみ、ステップ2へ進む
```

### ステップ 2: 制約のヒアリング

```
ASK USER: 以下を1つのメッセージで教えてください
  1. フロントエンドUI（画面）は必要ですか？（あり / なし）
  2. データの保存（DB）や認証は必要ですか？（あり / なし）
  3. 既存のエコシステムへの依存はありますか？
     （例: Google Workspace・Slack・既存のAWS/Firebase等。なければ「なし」）
  4. PoC・お試しですか、それとも継続的に運用しますか？
  5. 技術的な知識レベルはどの程度ですか？（自分でコードを書く / Claudeに任せたい）

WAIT_FOR: ユーザーの回答
```

### ステップ 3: カテゴリ対応表との照合

```
| 条件                                      | カテゴリ                | 状態     | 委譲先フロー  |
|--------------------------------------------|--------------------------|----------|---------------|
| UI・API・DB不要、画面モックのみ            | 静的サイト                | 実装済み | new-static    |
| API・DB・認証など動的機能（Node.js系）     | Webアプリ                 | 実装済み | new-project   |
| Flutter・React Native・Expo等スマホアプリ  | クロスプラットフォーム    | 実装済み | new-app       |
| Google Sheets・Workspace連携が中心         | Google Apps Script        | TODO     | （未実装）     |
| ネイティブSwift・Kotlin単体実装            | ネイティブアプリ          | TODO     | （未実装）     |

ANALYZE: ヒアリング結果を対応表と照合し、最も適合するカテゴリを1つ選ぶ
  IF 複数の候補で判断がつかない:
    ASK USER: 判断に必要な点（例:「フロントエンドは必要ですか？」）を確認する
    WAIT_FOR: ユーザーの回答

PRESENT: 候補カテゴリと選定理由を1〜2文で提示
  例: 「APIとDBが必要そうなので、Webアプリ（new-project）が適しています」

GATE: ユーザー承認
  IF 否定された:
    ASK USER: 対応表から直接選んでもらう
    WAIT_FOR: ユーザーの選択

IF 選定カテゴリ.状態 == TODO:
  REPORT:
    "{カテゴリ名}はまだ対応レシピがありません（TODO）。"
  ASK USER: どう進めますか？
    1. consultに相談して、調査ベースで進め方を考える
    2. 近い既存カテゴリで妥協して進める
    3. ここで終了する
  WAIT_FOR: ユーザーの回答

  IF 1（consultに相談）:
    SUMMARY = ここまでのヒアリング内容（要望・制約・選定カテゴリ名・TODOである理由）
    READ {SKILL_DIR}/flows/consult/SKILL.md
    FOLLOW: そこに記述されたすべての手順を実行する。SUMMARY を前提として渡し、再ヒアリングしない。
    STOP
  ELIF 2（妥協する）:
    SET 選定カテゴリ = ユーザーが選んだ近い既存カテゴリ
  ELSE:
    STOP
```

### ステップ 4: 委譲

```
READ {SKILL_DIR}/flows/<選定カテゴリの委譲先フロー>/SKILL.md
IF READ FAILED:
  REPORT: "フローファイルが見つかりません。SKILL_DIR の導出を確認してください。"
  STOP
FOLLOW: そこに記述されたすべての手順を実行する

NOTE: ステップ2のヒアリングで判明済みの情報（フロントエンド要否・フレームワーク等）は、
      委譲先フロー内で同じ内容を再度質問しないこと。既知の回答として扱う。
```

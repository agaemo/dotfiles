---
name: new-static
description: Astro + Node.js で静的サイト（LP・PoC・画面モック）をセットアップする手順。/craft から静的サイトを選択したときに実行される。
---

# new-static（静的サイトセットアップ）

Astro + Node.js で静的サイト（LP・PoC・管理画面モック等）プロジェクトをセットアップする。
**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 手順

### ステップ 1: ヒアリング & デザインブリーフ作成（メインClaude自身が実行）

> **注意:** サブエージェントはユーザーと対話できない。ヒアリングは必ずメインClaude自身が行うこと。

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの絶対パス
  # 例: /Users/alice/.claude/skills/craft/flows/new-static
  # このファイルを Read ツールで読んだパスから導出すること
  # 注: 他フローファイル（new-project/new-app/consult）の SKILL_DIR は craft/ を指すが、
  #     このファイルの SKILL_DIR は craft/flows/new-static/ を指す

REQUIRE: カレントディレクトリがプロジェクトルートであること

IF NOT EXISTS(.craft/):
  MKDIR .craft/
ENDIF

IF NOT EXISTS(.craft/design-brief.md):
  READ {SKILL_DIR}/design-brief-template.md
  WRITE .craft/design-brief.md（内容: 上記テンプレートをそのまま。REQUIRE でカレントディレクトリ = プロジェクトルートが保証されているため相対パスで書く）
ENDIF

ASSERT EXISTS(.craft/design-brief.md)

--- ヒアリング（SELF = メインClaudeがユーザーに直接質問する） ---

SELF: 以下を 1つのメッセージ でユーザーに質問する
  1. 業種・サービス内容とターゲットユーザー（誰に届けたいか）
  2. ページ構成（単一ページ / 複数ページ。複数の場合は画面名を列挙してもらう）
  3. 画面の明暗（ダーク系 / ライト系 / どちらでも）
  4. 色の方向性（使いたい色・避けたい色・ブランドカラーの有無）
  5. 文字の印象（A. 丸みがあって親しみやすい / B. きっちり直線的 / C. どちらでもない）
  6. 参考にしたいデザイン（サービス名 + 好きな部分を1〜3つ、なければ「なし」でOK）
  7. 感じてほしい印象（FEEL 3語）・感じてほしくない印象（ANTI-FEEL 3語）

WAIT_FOR: ユーザーの回答

--- デザインブリーフ作成（SELF = メインClaudeが記入する） ---

SELF: ヒアリング回答をもとに .craft/design-brief.md の全TODOを埋める
  - ブランドアーキタイプはヒアリング結果から推定して選択する
  - 仮定で埋めた項目がある場合は、その旨をユーザーに明示すること

--- プロジェクト名・サービス名の決定 ---

ユーザーからサービス名・プロジェクト名の指定がない場合:
  RECOMMENDED: 「SAMPLE IMS」「DEMO SHOP」など、サンプルであることが一目でわかる名前を使う
  ALTERNATIVE: ユーザーに希望を確認する
  PROHIBITED: 実在するブランド・サービスの名前を流用すること
  理由: 後から名前変更が必要になると、レイアウト崩れ・文言の意味的不整合が連鎖して発生する

--- サンプルデータのルール ---

ユーザーから実際のデータの指定がない場合、プロジェクト種別に応じた架空データを使うこと:

  共通ルール:
    REQUIRED: サンプルであることが一目でわかる値にする
    PROHIBITED: 実在する個人名・会社名・住所・電話番号・URLを組み合わせること

  BtoC向けLP（住所・電話番号・SNSが必要な場合）:
    住所: 郵便番号「〒000-0000」、都市名・区・町名はすべて架空（例: 架空都サンプル区見本町）
    電話番号: 市外局番「000」（例: 000-0000-0000）
    SNS・URL: href は「#」か「javascript:void(0)」。実在サービスのルートURLをリンク先に使わないこと
    アクセス案内: 架空の路線名・駅名（例: 架空線「サンプル駅」北口より徒歩5分）

  業務ツール・PoC（人名・組織名・インシデントデータ等が必要な場合）:
    人名: 架空の日本人名（例: 田中 健、鈴木 理恵）
    組織名: 「サンプル株式会社」「架空チーム」など
    IDや数値: 実運用を想定した形式だが実在しない値（例: INC-001、#00000）

SELF: 埋めたデザインブリーフの内容をユーザーに簡潔に見せる
```

---

### ステップ 2: 理解度チェック（Early Stop）& ユーザー確認

ステップ1のヒアリング後でも、AI が仮定で埋めた部分が残っている可能性がある。
セットアップ前にここで潰す。

```
REPEAT:
  SELF_EVALUATE: 以下の5項目を 1〜5 で採点する
    スケール: 1=全く不明 / 2=断片的 / 3=概ね把握 / 4=ほぼ確信 / 5=完全に理解

    | # | 評価項目                                          | スコア |
    |---|---------------------------------------------------|--------|
    | 1 | 目的・ターゲット（誰に・何を伝えるLPか）            |        |
    | 2 | コンテンツ・訴求ポイント（何を見せるか・伝えるか）  |        |
    | 3 | デザイン方針（ビジュアルトーン・ブランド制約）      |        |
    | 4 | 技術的制約（アニメーション・フォーム・外部連携）    |        |
    | 5 | 完了条件（何をもって完成とするか・公開先・締め切り）|        |

  IF ANY(score < 4):
    ASK USER: スコアが4未満の項目について不明点を質問する
  ENDIF
UNTIL ALL(score >= 4)

GATE: ユーザー承認
  SHOW USER:
    "デザインブリーフが完成しました。この方針で実装を進めますか？"
  WAIT_FOR: ユーザーが明示的に承認する
  PROHIBITED: 承認を受け取る前にステップ3へ進むこと
  IF NOT CONFIRMED: STOP
```

---

### ステップ 3: セットアップ（サブエージェントで実行）

Agent ツールでサブエージェントを起動し、以下のプロンプトを渡す。
WAIT_FOR: サブエージェントの完了報告（"完了しました"）を受け取ってから続きに進む。

IMPORTANT: プロンプト内のプレースホルダーを渡す前に実際の絶対パスへ展開すること。
  <CWD>      = カレントディレクトリの絶対パス（Bash で `pwd` を実行して取得）
  <TEMPLATE> = このSKILL.mdから2階層上の絶対パス（craft/ ディレクトリ）
               例: /Users/alice/.claude/skills/craft

READ {SKILL_DIR}/setup-prompt.md ← サブエージェントへのプロンプト本文（ここで初めて読む）
IF READ FAILED:
  REPORT: "setup-prompt.md が見つかりません。セットアップを開始できません。"
  STOP
（テンプレート内の `<CWD>`・`<TEMPLATE>` を実際の値に展開してから渡すこと）

---

### ステップ 3.5: 初期 .craft/plan.md 生成

セットアップ完了後、デザインブリーフのページ・セクション構成から実装計画を作る。

```
IF NOT EXISTS(.craft/plan.md):
  ANALYZE: .craft/design-brief.md のページ構成・セクション構成を読み取る
  WRITE .craft/plan.md
    INCLUDE:
      - プロジェクト名・目的（1〜2文）
      - セクション構成（ID・内容・実装状態の表）。各セクションは「未着手」で初期化する
      - ファイル構成の概要（.astro コンポーネントの配置方針）
    NOTE: フィーチャートラック設計セクションは不要
          （static は build フロー内で常にシンプルループとして実装される）
  ASSERT EXISTS(.craft/plan.md)
```

---

### ステップ 4: build フローへ委譲

```
READ {SKILL_DIR}/../build/SKILL.md
  # SKILL_DIR はこのファイル（craft/flows/new-static）を指すため、
  # craft/flows/build/SKILL.md へは1階層上がってアクセスする
FOLLOW: そこに記述されたすべての手順を実行する
  STACK = "static"
  HAS_REVIEW_CHAIN = false
  HAS_FRONTEND = true

NOTE: セクション単位の実装・モバイルファースト対応・Puppeteer での最終確認・
      CLAUDE.md / README.md 生成・.craft/plan.md の更新は build フロー側で行われる。
```

---

## 注意事項

- `intake` / `planner` / `security-reviewer` / `qa` は不要
- 単一 HTML ファイルで実装しない（メンテナンス性が著しく低下するため）
- フレームワークのインストール手順は必ず公式ドキュメントを確認すること

---

## 名前変更が発生した場合

`rename-checklist.md`（このSKILL.mdと同じディレクトリ）を参照すること。

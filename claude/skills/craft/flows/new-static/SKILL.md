---
name: new-static
description: Astro + Node.js で、コンテンツ訴求が主目的の静的LP（ランディングページ・PoCの画面モック）をセットアップする手順。/craft から静的サイトを選択したときに実行される。ツールのサンプル集・ドキュメントサイト・言語/ランタイム環境の紹介など「実行環境が前提にある」依頼には使わない（consultへ誘導する）。
---

# new-static（静的サイトセットアップ）

Astro + Node.js で、コンテンツ訴求が主目的の静的LP（ランディングページ・PoCの画面モック）
プロジェクトをセットアップする。**純粋なLP専用。** 実行環境・ツール・サンプルコードなど
「動かして確かめるもの」が本質のプロジェクト（例: プログラミング言語の学習用サンプル集）は、
画面（HTML）が欲しいように見えてもここには該当しない。scopeフローの対応表で
判断がつかない場合はconsultへ倒すこと。

**プロジェクトディレクトリを作成して `cd` で移動した後に実行すること。**

## 手順

### ステップ 1: ヒアリング & デザインブリーフ作成（メインClaude自身が実行）

> **注意:** サブエージェントはユーザーと対話できない。ヒアリングは必ずメインClaude自身が行うこと。

```
SKILL_DIR = このSKILL.mdが存在するディレクトリの絶対パス
  # 例: /Users/alice/.claude/skills/craft/flows/new-static
  # このファイルを Read ツールで読んだパスから導出すること

REQUIRE: カレントディレクトリがプロジェクトルートであること

IF NOT EXISTS(.craft/docs/):
  MKDIR .craft/docs/
ENDIF

# design-coach などで、デザインが先に固まっているか（この判定は、下のテンプレート書き出しより前に行う）
SET DESIGN_READY = EXISTS(.craft/docs/design-brief.md) AND EXISTS(.craft/docs/design-system.md)

IF NOT EXISTS(.craft/docs/design-brief.md):
  READ {SKILL_DIR}/design-brief-template.md
  WRITE .craft/docs/design-brief.md（内容: 上記テンプレートをそのまま。REQUIRE でカレントディレクトリ = プロジェクトルートが保証されているため相対パスで書く）
ENDIF

ASSERT EXISTS(.craft/docs/design-brief.md)

--- コンセプトの取り込み（/craft を呼ぶ前の会話に企画内容が含まれる場合） ---

IF ここまでの会話の中で、何を作るか・核となる仕組み・名称など
   デザイン（見た目）以前の企画がすでに固まっている:
  SELF: .craft/docs/design-brief.md の「0. コンセプト」に、その内容をそのまま記録する
  NOTE: 以下のヒアリングでは、ここに書いた内容を再度質問しないこと

--- デザインが既に固まっている場合（DESIGN_READY） ---

IF DESIGN_READY:
  # 既存の design-brief.md・design-system.md の内容を再度質問しない。
  # 以降の「ヒアリング」と「デザインブリーフ作成」は実行しない（「プロジェクト名・サービス名の決定」と
  # 「サンプルデータのルール」は引き続き参照する）
  CHECK: design-brief.md に「0. コンセプト」「9. 機能要件・完成条件」があるか。無い節は、既存の brief と
    これまでの会話から補って追記する（節の見出し順は design-brief-template.md に合わせる。
    「完成条件の実現可能性」欄は空欄でよい）
  CHECK: 「9. 画面構成・核となる操作」「完成条件」が埋まっていなければ、不足分だけをユーザーに質問する
  SELF: 補った内容を1〜2行でユーザーに伝え、ステップ2へ進む

--- ヒアリング（DESIGN_READY でない場合のみ。SELF = メインClaudeがユーザーに直接質問する） ---

SELF: 以下を 1つのメッセージ でユーザーに質問する
  （「0. コンセプト」に既に記録済みの項目があれば省略する）
  1. 業種・サービス内容とターゲットユーザー（誰に届けたいか）
  2. ページ構成（単一ページ / 複数ページ。複数の場合は画面名を列挙してもらう）
  3. 画面の明暗（ダーク系 / ライト系 / どちらでも）
  4. 色の方向性（使いたい色・避けたい色・ブランドカラーの有無）
  5. 文字の印象（A. 丸みがあって親しみやすい / B. きっちり直線的 / C. どちらでもない）
  6. 参考にしたいデザイン（サービス名 + 好きな部分を1〜3つ、なければ「なし」でOK）
  7. 感じてほしい印象（FEEL 3語）・感じてほしくない印象（ANTI-FEEL 3語）
  8. 画面構成・核となる操作（何ができれば良いか、主要な操作フロー）
  9. 完成条件（何をもって完成とみなすか。具体的な目標動作・成果物があれば明記）

WAIT_FOR: ユーザーの回答

--- デザインブリーフ作成（SELF = メインClaudeが記入する） ---

SELF: ヒアリング回答をもとに .craft/docs/design-brief.md の全TODOを埋める
  - ブランドアーキタイプはヒアリング結果から推定して選択する
  - 「9. 機能要件・完成条件」の「画面構成・核となる操作」「完成条件」には質問8・9の回答を
    そのまま記入する（「完成条件の実現可能性」欄は空欄のままでよい。build フローの
    ステップ0.5で検証後に記入される）
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
    | 2 | コンテンツ・訴求ポイント / 核となる操作（何を見せる・何ができれば良いか） |        |
    | 3 | デザイン方針（ビジュアルトーン・ブランド制約）      |        |
    | 4 | 技術的制約（アニメーション・フォーム・外部連携）    |        |
    | 5 | 完了条件（何をもって完成とするか・公開先・締め切り）|        |

  IF ANY(score < 4):
    ASK USER: スコアが4未満の項目について不明点を質問する
  ENDIF
UNTIL ALL(score >= 4)

プレビュー生成（GATEの前に必ず実施）:
  READ {SKILL_DIR}/../new-project/preview-generation.md（このプレビュー生成チェーン中に
  未読の場合のみ。セッションが変わった場合は再度READする。共通ルール・CDN方針・
  ASSERT/失敗時の代替導線が定義されている）
  .craft/docs/design-brief.md の内容から、カラーパレット（実際のスウォッチ）・
  タイポグラフィの印象・ブランドアーキタイプ・FEEL/ANTI-FEELワード・ページ構成を
  1枚にまとめる。{SKILL_DIR}/../new-project/templates/review/design-system.html を
  .craft/review/gates/04-design.html にコピーして置き換える（節の構成と並びは固定。ページ構成などの補足は「7 補足」に書く）（保存後、preview-generation.md の「index.html の生成と更新」に従って
  `review_index.py` で `.craft/review/index.html` を作り、`set` で 04 をページありにする。
  あわせて、次の確認用ページも出す（材料があるものだけ。無ければ作らない）:
    - 03 画面モック（`gates/03-mock.html`）: design-brief.md の「9. 画面構成」の順に、全セクションを縦に並べた
      ワイヤー（HTML/CSS。色・書体・余白は design-system.md の実トークン。文言は brief の仮文言かダミー。
      ページ冒頭に「表示している内容はサンプル」と書く）。画面UIの骨組み（mock-skeleton-web.html）は合わないため、
      戻りリンク・テーマ切替の型だけを借りる。`set` で登録する
    - 補助 `brief`（`extras/brief.html`）: `md2html.py` で design-brief.md と design-system.md を1枚にし、`extra` で登録する
    - 補助 `explore`（design-coach の探索モックがあるとき）: `.craft/docs/explore/mock-*.html` を
      `extras/explore-<名前>.html` にコピーし、`extra` で登録する（採用理由は brief の「8.」）
    - 01 要件定義・02 ユーザーストーリー（承認の前に出す。作り方は、下の「01・02 の作成」）。
      05 は未作成のままにし、ステップ3.5で作る。06 もステップ3.5で作る
  保存後に index.html を開いて提示する）
    - 明暗の方針で分岐する。両テーマ対応の案件は、artifact-design skill の既定方針（ライト/ダーク両テーマ対応）を
      維持したまま、明暗の方針を初期表示（:root のデフォルト値）に反映する。
      **ライトのみの案件（LP など。brief の「対応範囲」がライトのみ）は、右上の切替ボタンを「通常面 / 暗い面
      （常に暗いヒーロー等）」の見え方の確認用に読み替え、テーマ切替は実装に含めない旨を「7 補足」に書く**
  出力先: .craft/review/gates/04-design.html

01・02 の作成（GATE の前。メインClaude自身が直接作る。intake・refiner エージェントは呼ばない）:
  .craft/docs/design-brief.md の「0. コンセプト」「9. 機能要件・完成条件」から、次の2つを書く。
    - .craft/docs/requirements.md（{SKILL_DIR}/../../agents/intake.md の「出力」の形式）
    - .craft/docs/stories.md（{SKILL_DIR}/../../agents/refiner.md の「出力」の形式。US は画面・セクション単位）
  ヒアリングはしない。brief に無い項目は、仮定で埋めず、requirements.md の「未確定事項」と、
  stories.md の「未解決の疑問」に残す。
  md2html.py で、gates/01-requirements.html と gates/02-stories.html に変換し、
  `review_index.py set` で登録する（変換の手順は preview-generation.md）。

GATE: ユーザー承認
  SHOW USER:
    "デザインブリーフが完成しました（プレビュー: .craft/review/gates/04-design.html）。この方針で実装を進めますか？"
  WAIT_FOR: ユーザーが明示的に承認する
  PROHIBITED: 承認を受け取る前にステップ3へ進むこと
  IF NOT CONFIRMED: STOP
```

---

### ステップ 2.5: 技術調査（researcher呼び出し）

```
IMPORTANT: setup-prompt.md に書かれたAstroの既知の罠（v6のContent Collections等）は
  記載時点のスナップショットであり、Astro自体は更新が速いフレームワークのため、
  そのまま実行前提にしない。

Agent ツールで researcher エージェント（{SKILL_DIR}/../../agents/researcher.md）を起動する。
  対象: Astro（+ Node.js）
  モード: 差分確認（{SKILL_DIR}/setup-prompt.md の内容、特にSTEP2のNOTE群を前提として渡す）
WAIT_FOR: サブエージェントの完了報告（`.craft/docs/tech-research.md` への保存）を受け取ってから続きに進む
IF READ FAILED（researcher.mdが見つからない）:
  NOTE: 読めない場合でも省略せず、WebSearch/WebFetchで同等の調査（Astro最新版の
  破壊的変更・既知の罠）をこの場で行うこと

IMPORTANT: researcherは「懸念なし」であっても客観的な差分（バージョンステータスの変化・
  新たなセキュリティリリース・破壊的変更・新たな既知の罠等）を報告に含めてくる。差分がある
  場合、その内容をそのままユーザーに提示してから次に進むこと（提示せず進めることを禁止する）。
  WAIT_FOR: ユーザーの回答（差分がある場合のみ）

保存後（承認ゲートではない補助資料）:
  `md2html.py` で `.craft/docs/tech-research.md` を `.craft/review/extras/tech.html` に変換し、
  `review_index.py extra` で `tech`（技術調査）として登録する（手順は preview-generation.md の「index.html の生成と更新」）
```

---

### ステップ 3: セットアップ（サブエージェントで実行）

```
IMPORTANT: プロンプト内のプレースホルダーを渡す前に実際の絶対パスへ展開すること。
  <CWD>      = カレントディレクトリの絶対パス（Bash で `pwd` を実行して取得）
  <TEMPLATE> = {SKILL_DIR}/../.. の絶対パス（craft/ ディレクトリ）
               例: /Users/alice/.claude/skills/craft

READ {SKILL_DIR}/setup-prompt.md ← サブエージェントへのプロンプト本文（ここで初めて読む）
IMPORTANT: .craft/docs/tech-research.md の内容と setup-prompt.md の記載が食い違う場合、
  tech-research.md（＝現時点の調査結果）を優先し、サブエージェントへの指示にその差分を
  明記してから渡すこと（setup-prompt.md 自体は書き換えない）。
IF READ FAILED:
  REPORT: "setup-prompt.md が見つかりません。セットアップを開始できません。"
  STOP
（テンプレート内の `<CWD>`・`<TEMPLATE>` を実際の値に展開してから渡すこと）

Agent ツールでサブエージェントを起動し、上記で読み込んだプロンプトを渡す。
WAIT_FOR: サブエージェントの完了報告（"完了しました"）を受け取ってから続きに進む。
IF サブエージェントが "完了しました" を報告しない（エラー・中断）:
  REPORT: 失敗したステップと理由をユーザーに伝え、再試行するか確認すること
  STOP
```

---

### ステップ 3.4: hooks・settings.json の書き出し（メインClaude自身が実行）

IMPORTANT: このステップはサブエージェントに委譲せず、メインClaude自身が直接 Read/Write すること。
  `.claude/settings.json`・`.claude/hooks/*.sh` の書き出しをサブエージェントに含めると、
  ハーネスの権限システムに「自己変更（Self-Modification）」と判定され Agent 呼び出し自体が
  拒否される（実際に発生・再現済み）。ステップ3のAstroプロジェクト生成が完了した後（＝
  ディレクトリが非空になった後）に行うことで、STEP2の「非空ディレクトリ」誤判定問題も回避する。

```
TEMPLATE = {SKILL_DIR}/../..  # craftディレクトリの絶対パス

READ  TEMPLATE/hooks/on-session-start.sh → WRITE CWD/.claude/hooks/on-session-start.sh
READ  TEMPLATE/hooks/pre-bash.sh         → WRITE CWD/.claude/hooks/pre-bash.sh

READ TEMPLATE/settings.json
REPLACE ALL: ".claude/hooks/" → "${CLAUDE_PROJECT_DIR}/.claude/hooks/"
WRITE CWD/.claude/settings.json

ASSERT EXISTS(CWD/.claude/settings.json)
ASSERT EXISTS(CWD/.claude/hooks/on-session-start.sh)
ASSERT EXISTS(CWD/.claude/hooks/pre-bash.sh)
ASSERT: 書き出した CWD/.claude/settings.json に CWD の実際の絶対パス文字列が含まれていないこと
IF いずれかの ASSERT が FAILED:
  REPORT: エラー内容を報告してユーザーに確認を求める
  STOP
```

---

### ステップ 3.5: 初期 .craft/docs/plan.md 生成

セットアップ完了後、デザインブリーフのページ・セクション構成から実装計画を作る。

```
IF NOT EXISTS(.craft/docs/plan.md):
  ANALYZE: .craft/docs/design-brief.md のページ構成・セクション構成を読み取る
  WRITE .craft/docs/plan.md
    INCLUDE:
      - プロジェクト名・目的（1〜2文。「0. コンセプト」があれば参照する）
      - 完成条件（「9. 機能要件・完成条件」の内容をそのまま転記する）
      - セクション構成（ID・内容・実装状態の表）。各セクションは「未着手」で初期化する
      - ファイル構成の概要（.astro コンポーネントの配置方針）
      - 「開発ランタイム」（STACK識別子・環境管理ツール・検証コマンド）と「開発コマンド」の表
        （dev / build / test / fmt / lint。static で test・fmt が無いターゲットは `@echo '<名前>: 対象なし'`）。
        build フローのステップ0.7 が、この表から Makefile を生成する
    NOTE: フィーチャートラック設計セクションは不要
          （static は build フロー内で常にシンプルループとして実装される）
    NOTE: 完成条件の達成が新規のロジック・アルゴリズム・独自フォーマット等（設計しながら
          決める核となる仕組み）に依存する場合は、それを担うセクションを最優先（先頭）に
          配置する。build フロー側で実装前に実現可能性を検証するため
  ASSERT EXISTS(.craft/docs/plan.md)

保存後（承認は求めない）:
  `md2html.py` で plan.md を `.craft/review/gates/05-plan.html` に変換し、`review_index.py set` で 05 をページありにする。

06 統合設計書の作成（承認は求めない。メインClaude自身が直接作る）:
  READ {SKILL_DIR}/../new-project/templates.md
  次の3つを、そのテンプレートで書く（入力: requirements.md・stories.md・design-brief.md・plan.md・design-system.md）。
    - .craft/docs/01_requirements_doc.md
    - .craft/docs/02_specifications_doc.md
    - .craft/docs/03_basic_design_doc.md（入力は plan.md と design-system.md）
  該当しない章（認証・DB・API・セキュリティなど）は、省略せず「対象外（理由）」と書く（章立ては変えない）。
  `md2html.py` で、3つを連結して `.craft/review/gates/06-spec.html` に変換し、`review_index.py set` で 06 を登録する。
```

---

### ステップ 4: build フローへ委譲

```
READ {SKILL_DIR}/../build/SKILL.md
  # SKILL_DIR はこのファイル（craft/flows/new-static）を指すため、
  # craft/flows/build/SKILL.md へは1階層上がってアクセスする
IF READ FAILED:
  REPORT: "フローファイルが見つかりません: {SKILL_DIR}/../build/SKILL.md。SKILL_DIR の導出を確認してください。"
  STOP
FOLLOW: そこに記述されたすべての手順を実行する
  STACK = "static"
  HAS_REVIEW_CHAIN = false
  HAS_FRONTEND = true

NOTE: セクション単位の実装・モバイルファースト対応・Puppeteer での最終確認・
      CLAUDE.md / README.md 生成・.craft/docs/plan.md の更新は build フロー側で行われる。
```

---

## 注意事項

- `intake` / `planner` / `security-reviewer` / `qa` は不要（エージェントとしては呼ばない）。
  ただし 01 要件定義・02 ユーザーストーリー・06 統合設計書は、brief と plan.md から、メインClaudeが直接作る
- 単一 HTML ファイルで実装しない（メンテナンス性が著しく低下するため）
- フレームワークのインストール手順は必ず公式ドキュメントを確認すること

---

## 名前変更が発生した場合

`rename-checklist.md`（このSKILL.mdと同じディレクトリ）を参照すること。

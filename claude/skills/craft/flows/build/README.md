# build（実装フェーズ）フロー

`.craft/plan.md` に基づいて実装を進める共通エンジン。`SKILL.md` に定義。
new-project・new-static・new-app の設計フェーズ完了後、または別セッションでの再開時に、
同じこのフローが呼ばれる（実装ロジックの二重管理をなくすため）。

```mermaid
flowchart TD
    START([build 起動\n初回 or 再開]) --> DETECT{STACK等の変数を\n受け取った?}
    DETECT -->|No・再開時| AUTO["自動判定\npubspec.yaml存在→flutter\ndesign-brief.mdのみ存在→static\nそれ以外→node"]
    AUTO --> S0
    DETECT -->|Yes・初回| S0

    S0["STEP 0: plan.md / design-system.md を読み\n完了状況を提示"]
    S0 --> S1{STACK != static?}
    S1 -->|Yes| S1A["STEP 1: テスト戦略決定\ntesterエージェントでTDD環境セットアップ"]
    S1A --> S2
    S1 -->|No| S2

    S2{plan.md に\nフィーチャートラック設計がある?}
    S2 -->|Yes| PH1["フェーズ1: クリティカルパス\n（シリアル実装）"]
    PH1 --> PH2["フェーズ2: 並列トラック\n（worktree分離）"]
    PH2 --> PH3["フェーズ3: 統合確認\n（Bug-fix TDD含む）"]
    PH3 --> S3
    S2 -->|No| LOOP["シンプルループ:\n未着手ステップを1件実装\n→ビルド確認→完了マーク\n（staticはセクション単位+モバイルファースト）"]
    LOOP --> S3

    S3{HAS_FRONTEND?}
    S3 -->|Yes・static| S3B["Puppeteerで最終確認"]
    S3 -->|Yes・node/flutter| S3A["designerエージェントで\n実画面レビュー"]
    S3 -->|No| S4
    S3A --> S4
    S3B --> S4

    S4{HAS_REVIEW_CHAIN?}
    S4 -->|Yes| S4A["/ultrareview（オプション）"]
    S4A --> S5["verify→security-reviewer\n→qa→code-reviewer"]
    S5 --> S6
    S4 -->|No| S6

    S6["STEP 6: CLAUDE.md・README.md 生成\nplan.md の完了マーク更新"]
    S6 --> END([完了])
```

---

## 各フィーチャートラックの処理

フェーズ2で並列起動される各トラックエージェントの内部フロー。

```mermaid
flowchart LR
    subgraph Track["track-[name]（worktree 分離済み）"]
        direction TB
        R["docs/working/stories.md の\n担当 US を読む"]
        R --> I["所有ファイルを実装\n（依存ファイルは読み取り専用）"]
        I --> B{"pnpm build\n成功？"}
        B -->|失敗| I
        B -->|成功| V["受け入れ条件を\n1件ずつ確認"]
        V --> REP["完了レポート\n・実装ファイル一覧\n・受け入れ条件充足状況\n・未解決問題"]
    end
```

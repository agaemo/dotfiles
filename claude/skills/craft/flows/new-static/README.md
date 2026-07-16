# new-static（静的サイトセットアップ）フロー

Astro + Node.js で静的サイト（LP・PoC・画面モック等）プロジェクトをセットアップする。
ヒアリング・デザインブリーフ・初期 `.craft/plan.md` 生成までを担当し、実装フェーズは `build` フローに委譲する。

```mermaid
flowchart TD
    START([静的サイトを選択]) --> S1

    subgraph DESIGN["設計フェーズ（メインClaude が対話）"]
        S1["STEP 1: ヒアリング\n業種・ページ構成・色・フォント・\n参考デザイン・FEEL/ANTI-FEEL を\n1メッセージで質問"]
        S1 --> S1B["デザインブリーフ生成\n→ .craft/design-brief.md"]
        S1B --> S2["STEP 2: 理解度チェック\n5項目すべて ≥4 になるまでループ"]
        S2 --> S2P["プレビュー生成\n→ .craft/design-preview.html（ローカル）"]
        S2P --> GATE{承認}
    end

    GATE -->|承認| S3

    subgraph SETUP["セットアップ（サブエージェント）"]
        S3["STEP 3:\nmise → Astro プロジェクト作成\n→ ファイル書き出し\n→ settings.json\n→ git init\n→ pnpm build 確認"]
    end

    S3 --> S35["STEP 3.5:\nデザインブリーフのセクション構成から\n.craft/plan.md を未着手状態で生成"]
    S35 --> S4["STEP 4: build フローへ委譲\nSTACK=static, HAS_REVIEW_CHAIN=false"]
    S4 --> END([完了])
```

実装フェーズの詳細は [flows/build/README.md](../build/README.md) を参照。

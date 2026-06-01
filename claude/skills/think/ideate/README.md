# ideate

Design Thinking（Brown, 2008; Stanford d.school）の発想フェーズと
Jobs-to-be-Done（Christensen et al., 2016）を組み合わせたアイデア生成スキル。
Synectics の Direct Analogy（Gordon, 1961）を用いた他領域類推を発想に組み込む。

課題・問いを受け取り、3フェーズのエージェント処理で具体的な提案を返す。

1. **job-mapper**（JTBD）: ジョブ実行者・コアジョブ・感情的/社会的ジョブ・望ましい成果・制約を定式化
2. **synectics-analogist**（Synectics）: コアジョブと同型の問題を他領域（近・中・遠）で探し、転用可能な原則を抽出
3. **dt-ideator**（Design Thinking）: JTBD と類推結果を元に HMW 質問を生成し、最大5視点軸でアイデアを発散

## できること・できないこと

| できること | できないこと |
|-----------|------------|
| 課題・問いから複数の提案を生成する | 既存の提案の検証・評価（→ six-hats） |
| ターゲットや背景が曖昧でも受け付ける | 矛盾・トレードオフの解消（→ triz） |
| 異なる視点軸（ユーザー/技術/ビジネス/逆張り/類推）から多角的に発想する | 常識を疑うゼロベース再構築（→ first-principles） |
| verbosity に応じて箇条書き〜実行ステップ付きで出力する | 変形元が明確な既存サービスの改良（→ scamper） |

## 使い方

`/think` 経由で呼び出す。

```
# 自動判定（ideate に振られる）
/think "新しい社内ツールのアイデアを出したい"
/think "チームの生産性を上げる方法が知りたい"

# 明示指定
/think ideate "社員のオンボーディングを改善したい"
/think ideate "新規顧客獲得の施策を詳しく出して"
/think ideate "BtoB 営業の効率化アイデアを簡潔に"
/think ideate    # 入力を対話形式で聞く
```

## 視点軸

各アイデアは以下のいずれかの軸から出発する。なるべく異なる軸から生成し、視点の偏りを防ぐ。

| 軸 | 出発点 | 論拠 |
|----|-------|------|
| ユーザー視点 | ターゲットの体験・感情・行動から逆算 | Brown (2008) |
| 技術・手段視点 | 既存の技術・仕組みの組み合わせや転用 | Brown (2008) |
| ビジネス・運用視点 | コスト・収益・オペレーションの変え方 | Brown (2008) |
| 逆張り視点 | 常識と逆の方向を試みる | Brown (2008) |
| 類推視点 | 他領域の転用可能な原則を起点にする（`analogy_result` が空の場合はスキップ） | Gordon (1961); Chan et al. (2011) |

## verbosity による出力の違い

| verbosity | 出力内容 | ファイル保存 |
|-----------|---------|------------|
| 簡潔 | 案タイトル + 一文説明（3〜5案） | なし |
| 標準 | 案タイトル + 2〜3文の理由つき説明（3〜5案） | なし |
| 詳細 | 案タイトル + 説明 + 実行ステップ（3〜5案） | 保存先を聞く |

## フロー

```mermaid
flowchart TD
    Start([/think ideate input]) --> NG{NG判定}
    NG -- NG --> Stop[代替スキルを提案してSTOP]
    NG -- OK --> F1[job-mapper: JTBD定式化\nジョブ実行者 / コアジョブ / 成果 / 制約]
    F1 --> F2[synectics-analogist: 他領域類推\n近・中・遠の転用可能な原則を抽出]
    F2 --> F3[dt-ideator: Design Thinking発想\nHMW生成 → 最大5視点軸でアイデア発散]
    F3 --> Synth[統合: 有望案を選出]
    Synth --> Out{verbosity?}
    Out -- 簡潔 --> Brief[タイトル + 一文\nファイル保存なし]
    Out -- 標準 --> Normal[タイトル + 理由 + 視点軸\n保存先を確認]
    Out -- 詳細 --> Detail[JTBD要約 + HMW + 実行ステップ\n保存先を確認]
    Brief & Normal & Detail --> Dialog[対話・深掘り]
```

## 参考文献

Brown, T. (2008). Design Thinking. *Harvard Business Review*, 86(6), 84–92.
Christensen, C. M., Hall, T., Dillon, K., & Duncan, D. S. (2016). *Competing Against Luck: The Story of Innovation and Customer Choice*. HarperBusiness.
Gordon, W. J. J. (1961). *Synectics: The Development of Creative Capacity*. Harper & Row.
Gick, M. L., & Holyoak, K. J. (1980). Analogical problem solving. *Cognitive Psychology*, 12(3), 306–355.
Gick, M. L., & Holyoak, K. J. (1983). Schema induction and analogical transfer. *Cognitive Psychology*, 15(1), 1–38.
Chan, J., Fu, K., Schunn, C., Cagan, J., Wood, K., & Kotovsky, K. (2011). On the benefits and pitfalls of analogies for innovative design: Ideation performance based on analogical distance, commonness, and modality of examples. *Journal of Mechanical Design*, 133(8).

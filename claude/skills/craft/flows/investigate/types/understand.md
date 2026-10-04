---
name: investigate-understand
description: investigate フローの種別B（コード・仕様の理解、影響範囲の把握）の調査手順。flows/investigate/SKILL.md のステップ2から、種別Bと判定された場合のみ読み込まれる。
---

# 種別B: コード・仕様の理解

共通ルール（編集禁止・根拠と確度・サブエージェントの扱い）は `flows/investigate/SKILL.md` に従う。
SKILL_DIR は呼び出し元で定義済みの値をそのまま使う。

```
1. 関連ファイルを Read / Grep で追い、処理の流れと影響範囲（呼び出し元・依存先）を把握する

2. IF モジュール境界・依存方向など構造レベルの評価が必要:
     IF .craft/docs/arch-review.md が既に存在する:
       ASK USER: 既存のアーキテクチャ評価を上書きしてよいか
       WAIT_FOR: ユーザーの回答
       IF 上書きしない: 既存ファイルを根拠として使い、architect は起動しない
     architect（{SKILL_DIR}/agents/architect.md）を起動する
       - 渡すもの: 調査したい構造上の論点、対象プロジェクトの絶対パス
   ELSE:
     architect は起動しない（局所的な調査は 1 のみで完結させる）
```

---
name: investigate-tech
description: investigate フローの種別C（技術の実現可能性・選定材料の調査）の手順。flows/investigate/SKILL.md のステップ2から、種別Cと判定された場合のみ読み込まれる。
---

# 種別C: 技術調査

共通ルール（編集禁止・根拠と確度・サブエージェントの扱い）は `flows/investigate/SKILL.md` に従う。
SKILL_DIR は呼び出し元で定義済みの値をそのまま使う。

```
1. IF .craft/docs/tech-research.md が既に存在する:
     ASK USER: researcher の保存先（tech-research.md 固定）を上書きしてよいか
     WAIT_FOR: ユーザーの回答
     IF 上書きしない: 既存ファイルを調査結果として使い、researcher は起動しない（2 をスキップ）

2. researcher（{SKILL_DIR}/agents/researcher.md）をフル調査モードで起動する
   - 渡すもの: 調査対象の技術、知りたいこと、対象プロジェクトの絶対パス

3. 調査結果を、このプロジェクトの構成・制約と突き合わせ、適用可否を自分で評価する

4. ステップ3の報告には、tech-research.md への参照と要点のみを載せる（内容を二重に転記しない）
```

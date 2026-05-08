---
name: git-workflow
description: git/gh操作（状態確認・ブランチ作成・ステージング・コミット・PR作成・マージ）を安全な手順で行う。
---

## git ルール

- ユーザーが明示的に依頼しない限り、コミットしないこと。
- ユーザーが明示的に依頼しない限り、プッシュしないこと。
- `--no-verify`・main/masterへの `--force`・公開済みコミットへの `--amend` は使わないこと。
- コミット前に必ず `git diff --staged` を表示してユーザーが確認できるようにすること。

## 手順

### ブランチ作成
```bash
git checkout -b <type>/<description>
# type: feat / fix / refactor / chore / docs
```

### ステージングとコミット
```bash
git add <specific-files>       # 禁止: git add -A や git add .
git diff --staged              # コミット前にレビュー
git commit -m "$(cat <<'EOF'
<message>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### プッシュとPR作成
```bash
git push -u origin <branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## 概要
- <変更点>

## テスト方法
- [ ] <確認手順>

🤖 Generated with Claude Code
EOF
)"
```

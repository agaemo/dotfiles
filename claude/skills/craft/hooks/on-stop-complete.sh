#!/bin/sh
# Stop hook: build フローの完了報告の前に、必須ファイルが揃っているかを確認する
# exit 0 → 停止を許可 / exit 2 → 停止をブロック（stderr の内容が Claude に返る）
#
# build フロー ステップ6 の開始時に .craft/docs/.completing が作られ、完了報告のあとで削除される。
# マーカーが無い間（設計・実装の途中、通常の会話）は何もしない。
# 連続でブロックした場合は、Claude Code 側の上限（既定8回）で打ち切られる。
cat > /dev/null

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

[ -f .craft/docs/.completing ] || exit 0

missing=""
for f in CLAUDE.md README.md .craft/docs/plan.md; do
  [ -f "$f" ] || missing="$missing $f"
done

[ -z "$missing" ] && exit 0

printf '完了報告の前に、次のファイルが不足しています:%s\n' "$missing" >&2
printf 'build フロー ステップ6 に戻って生成してから、完了を報告してください。\n' >&2
exit 2

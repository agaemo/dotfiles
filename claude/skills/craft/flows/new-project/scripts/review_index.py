"""確認用ページの入口(.craft/review/index.html)のメニューを更新する。標準ライブラリだけで動く。

使い方:
  python3 -I review_index.py init   <index.html> <プロジェクト名>
  python3 -I review_index.py set    <index.html> <id> <file> <gate|extra> <タイトル> [補足]
  python3 -I review_index.py remove <index.html> <id>
  python3 -I review_index.py list   <index.html>

init   雛形(templates/review/index.html)をコピーし、PROJECT を置き換える(PAGES は空)。
       <index.html> が既にあれば何もしない(上書きしない)。
set    ページを追加する。同じ id があれば置き換える。
remove ページを消す。
list   現在のメニューを表示する。

<file> は index.html からの相対パス(例: gates/03-mock.html)。ファイルが実在しないと set は失敗する。
メニューの並びは、承認ゲート(gate)をファイル名の順、補助資料(extra)をファイル名の順にそろえる。
"""

import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "review" / "index.html"
BLOCK = re.compile(r"(var PAGES = \[\n)(.*?)(    \];)", re.S)
ENTRY = re.compile(r"\{\s*id:\s*(\".*?\"),\s*file:\s*(\".*?\"),\s*group:\s*(\".*?\"),\s*title:\s*(\".*?\"),\s*note:\s*(\".*?\")\s*\}")


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise SystemExit("PAGES の配列が見つかりません。雛形から作った index.html を指定してください")
    pages = [dict(zip(("id", "file", "group", "title", "note"), (json.loads(g) for g in e.groups()))) for e in ENTRY.finditer(m.group(2))]
    return text, m, pages


def save(path: Path, text: str, m: re.Match, pages: list) -> None:
    pages.sort(key=lambda p: (p["group"] != "gate", p["file"]))
    body = "".join(
        "      { id: %s, file: %s, group: %s, title: %s, note: %s },\n"
        % tuple(json.dumps(p[k], ensure_ascii=False).replace("</", "<\\/") for k in ("id", "file", "group", "title", "note"))
        for p in pages
    )
    path.write_text(text[: m.start(2)] + body + text[m.end(2) :], encoding="utf-8")


def main(argv: list) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd, path = argv[1], Path(argv[2])
    if cmd == "init":
        if len(argv) != 4:
            print(__doc__)
            return 1
        if path.exists():
            print(f"既にあります(変更しません): {path}")
            return 0
        text = TEMPLATE.read_text(encoding="utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace("{{PROJECT_NAME}}", html.escape(argv[3], quote=False).replace("\\", "\\\\").replace('"', '\\"')), encoding="utf-8")
        print(f"作成しました: {path}")
        return 0

    text, m, pages = load(path)
    if cmd == "list":
        for p in pages:
            print(f"{p['group']:5} {p['id']:14} {p['file']}  {p['title']}")
        return 0
    if cmd == "set":
        if len(argv) not in (7, 8):
            print(__doc__)
            return 1
        pid, file, group, title = argv[3:7]
        note = argv[7] if len(argv) == 8 else ""
        if group not in ("gate", "extra"):
            raise SystemExit("group は gate か extra です")
        if not (path.parent / file).is_file():
            raise SystemExit(f"ファイルがありません: {path.parent / file}")
        pages = [p for p in pages if p["id"] != pid] + [dict(id=pid, file=file, group=group, title=title, note=note)]
    elif cmd == "remove":
        if len(argv) != 4:
            print(__doc__)
            return 1
        pages = [p for p in pages if p["id"] != argv[3]]
    else:
        print(__doc__)
        return 1
    save(path, text, m, pages)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

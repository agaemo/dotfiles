"""確認用ページの入口(.craft/review/index.html)のメニューを更新する。標準ライブラリだけで動く。

承認ゲートは6つの固定スロット(番号・ファイル名・タイトルが決まっている)で、補足(extra)は自由に追加・削除できる。

  01 requirements  gates/01-requirements.html  要件定義
  02 stories       gates/02-stories.html       ユーザーストーリー
  03 mock          gates/03-mock.html          画面モック(UI なしの案件は対象外)
  04 design        gates/04-design.html        デザインシステム
  05 plan          gates/05-plan.html          実装計画
  06 spec          gates/06-spec.html          統合設計書(承認は求めない)

スロットの状態は、ready(ページあり)/ skip(対象外。理由つき)/ pending(未作成)の3つ。

使い方:
  python3 -I review_index.py init   <index.html> <プロジェクト名> [--force]
  python3 -I review_index.py set    <index.html> <スロットid> [補足 [タイトル]]
  python3 -I review_index.py skip   <index.html> <スロットid> <理由>
  python3 -I review_index.py extra  <index.html> <id> <file> <タイトル> [補足]
  python3 -I review_index.py remove <index.html> <extra の id>
  python3 -I review_index.py list   <index.html>

init   雛形をコピーし、6つのスロットを pending で作る。既にあれば何もしない(--force で作り直す)。
set    スロットを ready にする。ページのファイルが実在しないと失敗する。タイトルは、固定スロットの
       タイトルを変えないため、通常は指定しない。
skip   スロットを対象外にする(例: skip index.html design "UI なし")。
extra  補足のページを追加する(同じ id は置き換え)。<file> は extras/ 配下の、実在するファイル。
remove 補足のページを消す。
"""

import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "review" / "index.html"
BLOCK = re.compile(r"(var PAGES = \[\n)(.*?)(    \];)", re.S)
LEGACY = re.compile(r"\{\s*id:\s*(\".*?\"),\s*file:\s*(\".*?\"),\s*group:\s*(\".*?\"),\s*title:\s*(\".*?\"),\s*note:\s*(\".*?\")\s*\}")

SLOTS = [
    ("requirements", "gates/01-requirements.html", "要件定義"),
    ("stories", "gates/02-stories.html", "ユーザーストーリー"),
    ("mock", "gates/03-mock.html", "画面モック"),
    ("design", "gates/04-design.html", "デザインシステム"),
    ("plan", "gates/05-plan.html", "実装計画"),
    ("spec", "gates/06-spec.html", "統合設計書"),
]
SLOT = {s[0]: s for s in SLOTS}
KEYS = ("id", "file", "group", "title", "note", "status")


def slot_entry(sid: str, status: str = "pending", note: str = "", title: str = "") -> dict:
    _, file, default_title = SLOT[sid]
    return dict(id=sid, file=file, group="gate", title=title or default_title, note=note, status=status)


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise SystemExit("PAGES の配列が見つかりません。雛形から作った index.html を指定してください")
    pages = []
    for line in m.group(2).splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            lm = LEGACY.fullmatch(line)
            if not lm:
                raise SystemExit(f"PAGES の行を読めません: {line}")
            e = dict(zip(KEYS, (json.loads(g) for g in lm.groups())))
        e.setdefault("status", "ready")
        pages.append(e)
    return text, m, pages


def save(path: Path, text: str, m: re.Match, pages: list) -> None:
    order = {s[0]: i for i, s in enumerate(SLOTS)}
    pages.sort(key=lambda p: (p["group"] != "gate", order.get(p["id"], 99), p["file"]))
    body = "".join(
        "      " + json.dumps({k: p[k] for k in KEYS}, ensure_ascii=False).replace("</", "<\\/") + ",\n" for p in pages
    )
    path.write_text(text[: m.start(2)] + body + text[m.end(2) :], encoding="utf-8")


def need(argv: list, lo: int, hi: int) -> None:
    if not lo <= len(argv) <= hi:
        print(__doc__)
        raise SystemExit(1)


def main(argv: list) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd, path = argv[1], Path(argv[2])

    if cmd == "init":
        force = "--force" in argv
        args = [a for a in argv if a != "--force"]
        need(args, 4, 4)
        if path.exists() and not force:
            print(f"既にあります(変更しません): {path}")
            return 0
        name = html.escape(args[3], quote=False).replace("\\", "\\\\").replace('"', '\\"')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", name), encoding="utf-8")
        text, m, _ = load(path)
        save(path, text, m, [slot_entry(s[0]) for s in SLOTS])
        print(f"作成しました: {path}")
        return 0

    text, m, pages = load(path)
    by_id = {p["id"]: p for p in pages}

    if cmd == "list":
        for p in pages:
            print(f"{p['group']:5} {p['status']:7} {p['id']:14} {p['file']}  {p['title']}  {p['note']}")
        return 0

    if cmd in ("set", "skip"):
        need(argv, 4, 6)
        sid = argv[3]
        if sid not in SLOT:
            raise SystemExit(f"承認ゲートの id は {', '.join(SLOT)} のどれかです")
        if cmd == "skip":
            need(argv, 5, 5)
            by_id[sid] = slot_entry(sid, "skip", argv[4])
        else:
            file = path.parent / SLOT[sid][1]
            if not file.is_file():
                raise SystemExit(f"ファイルがありません: {file}")
            by_id[sid] = slot_entry(sid, "ready", argv[4] if len(argv) > 4 else "", argv[5] if len(argv) > 5 else "")
    elif cmd == "extra":
        need(argv, 6, 7)
        eid, file, title = argv[3:6]
        if eid in SLOT:
            raise SystemExit("補足の id に、承認ゲートの id は使えません")
        if not file.startswith("extras/") or not (path.parent / file).is_file():
            raise SystemExit(f"extras/ 配下の実在するファイルを指定してください: {file}")
        by_id[eid] = dict(id=eid, file=file, group="extra", title=title, note=argv[6] if len(argv) > 6 else "", status="ready")
    elif cmd == "remove":
        need(argv, 4, 4)
        if argv[3] in SLOT:
            raise SystemExit("承認ゲートは消せません。対象外にするには skip を使ってください")
        by_id.pop(argv[3], None)
    else:
        print(__doc__)
        return 1
    save(path, text, m, list(by_id.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

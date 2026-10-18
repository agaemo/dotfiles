#!/usr/bin/env python3
"""Markdown を、確認用の1枚のHTML（左にセクションナビ）に変換する。標準ライブラリのみ。

使い方: python3 -I md2html.py <出力パス> <タイトル> <Markdown...>

対応する記法: 見出し(# 〜 ####)・段落・箇条書き(入れ子・継続行つき)・番号付きリスト・チェックボックス(- [ ] / - [x])・
表・コードブロック(``` と ~~~)・引用(>)・水平線(---)・強調・コード・リンク。HTML コメントは出さない。
ユーザーストーリー(`## US-001: タイトル` の見出しを持つ文書)は、自動でカード表示にする
(誰が・何をしたい・なぜ・受け入れ条件・サイズ・依存)。「未解決の疑問」は、回答済み/未回答を色と文言で区別する。
"""
import html
import re
import sys
from pathlib import Path


def inline(text: str) -> str:
    """行内の記法（コード・強調・リンク）をHTMLに変換する。"""
    text = html.escape(text, quote=False)
    codes = []  # コードの中身は、強調やリンクの変換から守るため、先に退避する
    text = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", text)


FENCE = re.compile(r"^(```|~~~)")
LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.) (.*)$")
TASK = re.compile(r"^\[([ xX])\] (.*)$")


def task_li(text: str) -> str:
    """リスト項目の本文を <li> の中身にする。チェックボックス記法なら、済/未の印と class を付ける。"""
    m = TASK.match(text)
    if not m:
        return "<li>" + inline(text)
    done = m.group(1) in "xX"
    mark = "&#10003;" if done else "&#9633;"
    return f'<li class="task {"done" if done else "open"}"><span class="box" aria-label="{"済" if done else "未"}">{mark}</span> ' + inline(m.group(2))


def convert(md: str, prefix: str, nav: list, base_level: int = 0) -> str:
    """1つのMarkdown本文をHTML断片に変換する。見出しは nav に (id, レベル, 文字列) を追加する。"""
    out, lines, i, n = [], md.splitlines(), 0, 0
    stack = []  # (インデント幅, "ul"/"ol")。各項目は </li> を後で閉じる

    def close_lists(to_indent: int = -1):
        while stack and stack[-1][0] > to_indent:
            out.append("</li>")
            out.append(f"</{stack.pop()[1]}>")

    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("<!--"):  # HTML コメントは出さない(複数行も)
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
        elif FENCE.match(line):
            close_lists()
            fence = line[:3]
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].startswith(fence):
                buf.append(lines[i])
                i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
        elif re.match(r"^#{1,4} ", line):
            close_lists()
            level = len(line) - len(line.lstrip("#")) + base_level
            title = line.lstrip("#").strip()
            n += 1
            hid = f"{prefix}-{n}"
            nav.append((hid, level, title))
            out.append(f'<h{level} id="{hid}">{inline(title)}</h{level}>')
        elif line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?$", lines[i + 1]):
            close_lists()
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            out.append("<div class='wrap'><table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("</table></div>")
        elif LIST_ITEM.match(line):
            m = LIST_ITEM.match(line)
            indent, kind = len(m.group(1)), ("ol" if m.group(2)[0].isdigit() else "ul")
            if stack and indent == stack[-1][0] and kind == stack[-1][1]:
                out.append("</li>")  # 同じ階層の次の項目
            else:
                if stack and indent == stack[-1][0] and kind != stack[-1][1]:
                    close_lists(indent - 1)  # 同じ階層で、箇条書きと番号付きリストが切り替わる
                if stack and indent < stack[-1][0]:
                    close_lists(indent)
                    out.append("</li>") if stack and stack[-1][0] == indent else None
                if not stack or indent > stack[-1][0] or kind != stack[-1][1]:
                    out.append(f"<{kind}>")
                    stack.append((indent, kind))
            out.append(task_li(m.group(3)))
        elif line.strip() == "":
            close_lists()
        elif stack and line.startswith(" "):
            out.append("<br>" + inline(line.strip()))  # 箇条書きの継続行
        elif line.startswith(">"):
            close_lists()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(inline(lines[i].lstrip(">").strip()))
                i += 1
            i -= 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
        elif re.match(r"^(---+|\*\*\*+)$", line.strip()):
            close_lists()
            out.append("<hr>")
        else:
            close_lists()
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    close_lists()
    return "\n".join(out)


US_HEAD = re.compile(r"^## (US-\d+)[:：]\s*(.*)$")
FIELD = re.compile(r"^\*\*(誰が|何をしたい|なぜ|サイズ|依存|受け入れ条件):\*\*\s*(.*)$")


def stories(md: str, prefix: str, nav: list) -> str:
    """ユーザーストーリーの文書を、カード表示のHTML断片にする。US 以外の節は通常の変換に任せる。"""
    lines = md.splitlines()
    parts, buf, card, k = [], [], None, 0

    def flush_plain():
        nonlocal buf
        if buf:
            parts.append(convert("\n".join(buf), f"{prefix}p{len(parts)}", nav))
            buf = []

    def flush_card():
        nonlocal card
        if not card:
            return
        f, ac, rest = card["fields"], card["ac"], card["rest"]
        h = [f'<section class="card us" id="{card["id"]}"><header><span class="usid">{html.escape(card["us"])}</span>'
             f'<h3>{inline(card["title"])}</h3>']
        if "サイズ" in f:
            h.append(f'<span class="chip size">サイズ {inline(f["サイズ"])}</span>')
        h.append("</header><dl>")
        for key in ("誰が", "何をしたい", "なぜ"):
            if key in f:
                h.append(f"<dt>{key}</dt><dd>{inline(f[key])}</dd>")
        h.append("</dl>")
        if ac:
            h.append("<h4>受け入れ条件</h4>" + convert("\n".join(ac), f"{card['id']}-ac", []))
        if "依存" in f:
            h.append(f'<p class="dep"><strong>依存:</strong> {inline(f["依存"])}</p>')
        if rest:
            h.append(convert("\n".join(rest), f"{card['id']}-r", []))
        h.append("</section>")
        parts.append("".join(h))
        card = None

    mode = None  # カード内で、直前の「受け入れ条件:」の続きを読んでいるか
    for line in lines:
        m = US_HEAD.match(line)
        if m:
            flush_plain()
            flush_card()
            k += 1
            hid = f"{prefix}-us{k}"
            nav.append((hid, 2, f"{m.group(1)}: {m.group(2)}"))
            card = dict(us=m.group(1), title=m.group(2), id=hid, fields={}, ac=[], rest=[])
            mode = None
        elif line.startswith("## ") and card is not None:
            flush_card()
            buf.append(line)
            mode = None
        elif card is not None:
            if line.strip() == "---":
                flush_card()
                continue
            fm = FIELD.match(line)
            if fm:
                if fm.group(1) == "受け入れ条件":
                    mode = "ac"
                else:
                    card["fields"][fm.group(1)] = fm.group(2)
                    mode = None
            elif mode == "ac" and (line.strip() == "" or LIST_ITEM.match(line) or line.startswith(" ")):
                if line.strip():
                    card["ac"].append(line)
            elif line.strip():
                mode = None
                card["rest"].append(line)
        else:
            buf.append(line)
    flush_plain()
    flush_card()
    return "\n".join(parts)


CSS = """
:root{--bg:#fafaf8;--fg:#1d1d1b;--mut:#6b6b66;--line:#dcdcd4;--card:#fff;--code:#f1f1ec;--ok:#1f7a4a;--open:#8a5a12}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecece6;--mut:#a3a39b;--line:#34342f;--card:#1f1f1c;--code:#262622;--ok:#6fcf97;--open:#e5b65c}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.8 -apple-system,"Hiragino Sans",sans-serif;display:flex}
nav{width:260px;flex:none;position:sticky;top:0;height:100vh;overflow-y:auto;padding:16px;border-right:1px solid var(--line);font-size:.85rem}
nav a{display:block;color:var(--mut);text-decoration:none;padding:2px 0}
[hidden]{display:none!important}
nav a:hover{color:var(--fg)}
nav .l2{padding-left:12px}nav .l3{padding-left:24px}nav .l4{padding-left:36px}
main{flex:1;max-width:820px;padding:24px 24px 64px;min-width:0}
h1,h2,h3,h4{line-height:1.4}h1{border-bottom:1px solid var(--line);padding-bottom:6px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);font-size:.9rem}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--code)}
.wrap{overflow-x:auto}
code{background:var(--code);padding:1px 4px;border-radius:3px;font-size:.9em}
pre{background:var(--code);padding:12px;border-radius:6px;overflow-x:auto}pre code{background:none;padding:0}
blockquote{margin:12px 0;padding:4px 14px;border-left:3px solid var(--line);color:var(--mut)}
hr{border:0;border-top:1px solid var(--line);margin:20px 0}
li.task{list-style:none;margin-left:-1.2em}li.task .box{display:inline-block;width:1.2em;font-weight:700}
li.task.done .box{color:var(--ok)}li.task.open .box{color:var(--open)}
li.task.done{color:var(--mut)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 18px;margin:16px 0}
.card header{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.card h3{margin:0;flex:1;min-width:12em}
.usid{font:600 .8rem ui-monospace,Menlo,monospace;color:var(--mut)}
.chip{font-size:.75rem;border:1px solid var(--line);border-radius:999px;padding:0 10px;color:var(--mut)}
.card dl{display:grid;grid-template-columns:7em 1fr;gap:2px 12px;margin:8px 0}.card dt{color:var(--mut)}.card dd{margin:0}
.card h4{margin:10px 0 2px;font-size:.85rem;color:var(--mut)}.card ul{margin:0;padding-left:1.4em}.card .dep{margin:8px 0 0;font-size:.9rem;color:var(--mut)}
@media (max-width:720px){body{display:block}nav{position:static;width:auto;height:auto;border-right:0;border-bottom:1px solid var(--line)}.card dl{grid-template-columns:1fr}}
"""


def main(argv: list) -> int:
    if len(argv) < 4:
        print(__doc__)
        return 1
    out_path, title, sources = Path(argv[1]), argv[2], argv[3:]
    nav, body = [], []
    for idx, src in enumerate(sources, 1):
        text = Path(src).read_text(encoding="utf-8")
        is_stories = any(US_HEAD.match(line) for line in text.splitlines())
        body.append((stories if is_stories else convert)(text, f"s{idx}", nav))
    nav_html = "".join(f'<a class="l{lv}" href="#{hid}">{html.escape(t)}</a>' for hid, lv, t in nav)
    doc = (
        '<!doctype html><html lang="ja"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
        f'<nav><a id="back-nav" href="../index.html">&larr; 一覧へ</a>{nav_html}</nav>'
        f"<main>{'<hr>'.join(body)}</main>"
        '<script>if(window.top!==window){var b=document.getElementById("back-nav");if(b)b.hidden=true;}</script>'
        "</body></html>"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    print(f"出力しました: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

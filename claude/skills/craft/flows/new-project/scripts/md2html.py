#!/usr/bin/env python3
"""Markdown を、確認用の1枚のHTML（左にセクションナビ）に変換する。標準ライブラリのみ。

使い方: python3 -I md2html.py <出力パス> <タイトル> <Markdown...>
"""
import html
import re
import sys
from pathlib import Path


def inline(text: str) -> str:
    """行内の記法（コード・強調・リンク）をHTMLに変換する。"""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def convert(md: str, prefix: str, nav: list) -> str:
    """1つのMarkdown本文をHTML断片に変換する。見出しは nav に (id, レベル, 文字列) を追加する。"""
    out, lines, i, n = [], md.splitlines(), 0, 0
    list_stack = []  # "ul" / "ol"

    def close_lists():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            close_lists()
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
        elif re.match(r"^#{1,4} ", line):
            close_lists()
            level = len(line) - len(line.lstrip("#"))
            title = line[level:].strip()
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
        elif re.match(r"^\s*([-*]|\d+\.) ", line):
            kind = "ol" if re.match(r"^\s*\d+\. ", line) else "ul"
            if not list_stack or list_stack[-1] != kind:
                close_lists()
                out.append(f"<{kind}>")
                list_stack.append(kind)
            out.append("<li>" + inline(re.sub(r"^\s*([-*]|\d+\.) ", "", line)) + "</li>")
        elif line.strip() == "":
            close_lists()
        else:
            close_lists()
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    close_lists()
    return "\n".join(out)


CSS = """
:root{--bg:#fafaf8;--fg:#1d1d1b;--mut:#6b6b66;--line:#dcdcd4;--card:#fff;--code:#f1f1ec}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecece6;--mut:#a3a39b;--line:#34342f;--card:#1f1f1c;--code:#262622}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.8 -apple-system,"Hiragino Sans",sans-serif;display:flex}
nav{width:260px;flex:none;position:sticky;top:0;height:100vh;overflow-y:auto;padding:16px;border-right:1px solid var(--line);font-size:.85rem}
nav a{display:block;color:var(--mut);text-decoration:none;padding:2px 0}
nav a:hover{color:var(--fg)}
nav .l2{padding-left:12px}nav .l3{padding-left:24px}nav .l4{padding-left:36px}
main{flex:1;max-width:820px;padding:24px 24px 64px;min-width:0}
h1,h2,h3,h4{line-height:1.4}h1{border-bottom:1px solid var(--line);padding-bottom:6px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);font-size:.9rem}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--code)}
.wrap{overflow-x:auto}
code{background:var(--code);padding:1px 4px;border-radius:3px;font-size:.9em}
pre{background:var(--code);padding:12px;border-radius:6px;overflow-x:auto}pre code{background:none;padding:0}
@media (max-width:720px){body{display:block}nav{position:static;width:auto;height:auto;border-right:0;border-bottom:1px solid var(--line)}}
"""


def main(argv: list) -> int:
    if len(argv) < 4:
        print(__doc__)
        return 1
    out_path, title, sources = Path(argv[1]), argv[2], argv[3:]
    nav, body = [], []
    for idx, src in enumerate(sources, 1):
        body.append(convert(Path(src).read_text(encoding="utf-8"), f"s{idx}", nav))
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

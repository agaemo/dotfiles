// 画面の実測スクリプト（ブラウザの JS 実行ツールに貼り付けて使う。process/measure.md から参照）
// 使い方: ページを開いて 2〜3 秒待ち、全体を貼り付けて実行する。最後の式の値が返る。
// 出力が長いと切れるため、件数と一覧（先頭の数十件）だけを返す。

const parse = (c) => {
  const m = c.match(/[\d.]+/g).map(Number);
  return { r: m[0], g: m[1], b: m[2], a: m[3] === undefined ? 1 : m[3] };
};
const lum = ({ r, g, b }) => {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const blend = (t, b) => ({
  r: t.r * t.a + b.r * (1 - t.a),
  g: t.g * t.a + b.g * (1 - t.a),
  b: t.b * t.a + b.b * (1 - t.a),
  a: 1,
});
// 背景色は祖先を不透明な色までたどって重ねる（画像・グラデーションは考慮しない）
const bgOf = (el) => {
  const st = [];
  for (let e = el; e; e = e.parentElement) {
    const c = parse(getComputedStyle(e).backgroundColor);
    if (c.a > 0) st.push(c);
    if (c.a === 1) break;
  }
  let bg = { r: 255, g: 255, b: 255, a: 1 };
  for (const c of st.reverse()) bg = blend(c, bg);
  return bg;
};

// 装飾（欧文ラベル・番号・プレースホルダー）とみなすクラス名の接頭辞。プロジェクトに合わせて直す
const DECORATIVE = /^(hero__location|hero__scroll-text|label|lp-concept__feat-num|img-ph|lp-reservation__btn-en)/;

const low = [];
const small = [];
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
const seen = new Set();
while (walker.nextNode()) {
  const n = walker.currentNode;
  if (!n.textContent.trim()) continue;
  const el = n.parentElement;
  if (seen.has(el)) continue;
  seen.add(el);
  const cs = getComputedStyle(el);
  if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('script,style')) continue;
  if (!el.getBoundingClientRect().width) continue;
  const bg = bgOf(el);
  const fg = blend(parse(cs.color), bg); // 半透明の文字色も背景に重ねて評価する
  const L1 = lum(fg), L2 = lum(bg);
  const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
  const size = parseFloat(cs.fontSize);
  const large = size >= 24 || (size >= 18.66 && parseInt(cs.fontWeight) >= 700);
  const label = (el.className || el.tagName) + ':' + n.textContent.trim().slice(0, 14);
  if (ratio < (large ? 3 : 4.5)) low.push(`${label} ${ratio.toFixed(2)} ${size.toFixed(1)}`);
  if (size < 14) small.push(`${label} ${size.toFixed(1)}`);
}

// 孤立行: 行頭または行末に 1〜2 文字だけ残る要素
const orphans = [];
document.querySelectorAll('p,h1,h2,h3,li,span,a,td').forEach((el) => {
  const tn = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
  if (!tn.length) return;
  const lines = [];
  let lastTop = null;
  tn.forEach((n) => {
    for (let i = 0; i < n.length; i++) {
      const r = document.createRange();
      r.setStart(n, i);
      r.setEnd(n, i + 1);
      const rc = r.getClientRects()[0];
      if (!rc || !n.data[i].trim()) continue;
      if (lastTop === null || Math.abs(rc.top - lastTop) > rc.height * 0.6) { lines.push(''); lastTop = rc.top; }
      lines[lines.length - 1] += n.data[i];
    }
  });
  if (lines.length > 1 && (lines[0].length <= 2 || lines[lines.length - 1].length <= 2)) {
    orphans.push((el.className || el.tagName) + ' | ' + lines.join(' / '));
  }
});

({
  width: innerWidth,
  title: document.title,
  lowContrast: low.length,
  lowContrastList: low.slice(0, 40),
  smallTotal: small.length,
  smallInformational: small.filter((s) => !DECORATIVE.test(s)), // 情報を持つ文字（0件が基準）
  smallDecorativeMin: Math.min(...small.filter((s) => DECORATIVE.test(s)).map((s) => parseFloat(s.split(' ').pop()))),
  orphans,
  hrefHash: document.querySelectorAll('a[href="#"]').length,
});

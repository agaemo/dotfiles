#!/usr/bin/env node
/**
 * PreToolUse hook: Bash
 * 危険なコマンドをブロックする。
 * exit 0 → 許可 / exit 2 → ブロック
 */

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let data;
  try {
    data = JSON.parse(input);
  } catch {
    process.exit(0);
  }

  const command = data?.tool_input?.command ?? '';

  // TODO: プロジェクト固有のブロックルールを追加する
  const BLOCKED_PATTERNS = [
    /rm\s+-rf\s+\//,
    /git\s+push\s+--force/,
    /git\s+reset\s+--hard/,
    /DROP\s+TABLE/i,
    />\s*\.env/,
  ];

  for (const pattern of BLOCKED_PATTERNS) {
    if (pattern.test(command)) {
      console.log(`pre-bash フックによりブロックされました: コマンドがブロックパターン ${pattern} に一致します`);
      process.exit(2);
    }
  }

  process.exit(0);
});

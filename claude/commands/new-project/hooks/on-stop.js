#!/usr/bin/env node
/**
 * Stop hook: Claudeの応答終了後に実行される
 * 型チェック・テスト実行など、ターン終わりにまとめて行う処理に使う。
 */

const { execSync } = require('child_process');

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let data;
  try { data = JSON.parse(input); } catch { process.exit(0); }
  if (data?.stop_reason !== 'end_turn') process.exit(0);

  let changed = '';
  try {
    changed = execSync('git diff --name-only HEAD', { stdio: 'pipe' }).toString().trim();
  } catch {
    changed = 'unknown';
  }
  if (!changed) process.exit(0);

  // TODO: プロジェクト固有のチェックをここに追加する
  //
  // 【TypeScript プロジェクト】
  //   if (!require('fs').existsSync('package.json')) process.exit(0);
  //   try {
  //     execSync('npx tsc --noEmit', { stdio: 'pipe' });
  //   } catch (e) {
  //     console.log(JSON.stringify({ type: 'result', content: `型チェック失敗:\n${e.stdout?.toString()}` }));
  //     process.exit(2);
  //   }
  //
  // 【Go プロジェクト】
  //   if (!require('fs').existsSync('go.mod')) process.exit(0);
  //   try {
  //     execSync('mise exec -- go build ./...', { stdio: 'pipe' });
  //   } catch (e) {
  //     console.log(JSON.stringify({ type: 'result', content: `go build 失敗:\n${e.stderr?.toString()}` }));
  //     process.exit(2);
  //   }

  process.exit(0);
});

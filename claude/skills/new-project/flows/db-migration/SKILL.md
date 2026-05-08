---
name: db-migration
description: DBマイグレーション（スキーマ変更）を安全に実行する手順。テーブル追加・カラム変更・インデックス追加・本番反映時に使う。
---

## ルール

- マイグレーションファイルは一度適用したら編集しない。修正は新しいファイルで行う。
- 本番実行前に必ずステージング環境で検証すること。
- 大量データへの `ALTER TABLE` は実行時間を事前に見積もること（行数 × 変換コストで数分〜数時間になりうる）。
- 破壊的変更（カラム削除・型変更）は2段階で行うこと（下記参照）。
- ロールバック手順を先に書いてから実行すること。

## 手順

### ステップ1: マイグレーションファイルを作成する

```bash
# ファイル名はタイムスタンプ + 内容を含める
# 例: 20240120_001_add_users_email_index.sql
touch migrations/$(date +%Y%m%d)_001_<description>.sql
```

内容の構成：

```sql
-- Up
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_phone ON users(phone);

-- Down（ロールバック手順を必ず書く）
DROP INDEX idx_users_phone;
ALTER TABLE users DROP COLUMN phone;
```

### ステップ2: ローカルで検証する

NOTE: `<migration-tool>`、`<db-client>`、`<backup-tool>` はプロジェクトの CLAUDE.md または README を確認して実際のコマンドに置き換えること

```bash
# 適用
<migration-tool> up

# 動作確認（スキーマ確認）
<db-client> "DESCRIBE users;"
<db-client> "SHOW INDEXES FROM users;"

# ロールバック確認（必ず試す）
<migration-tool> down
<migration-tool> up
```

### ステップ3: 実行時間を見積もる（本番前）

```sql
-- 対象テーブルの行数確認
SELECT COUNT(*) FROM target_table;
-- 1万行以下: 即時
-- 10万行: 数秒〜数十秒
-- 100万行以上: 事前にオンラインDDLツール（pt-online-schema-change等）を検討
```

### ステップ4: 本番反映

```bash
# 直前にバックアップ確認
<backup-tool> verify

# メンテナンス時間帯に実行（トラフィックが少ない時間）
<migration-tool> up

# 適用後の確認
<db-client> "SHOW CREATE TABLE target_table;"
```

## 破壊的変更の2段階手順

カラム削除・型変更は1度のリリースで行わない。

### カラム削除の場合

**フェーズ1（今回のリリース）:**
1. アプリコードでそのカラムへの参照を削除する
2. デプロイして動作確認
3. このフェーズではDDLを変更しない

**フェーズ2（次回以降のリリース）:**
1. `ALTER TABLE ... DROP COLUMN ...` を実行する
2. 参照が完全になくなっていることを確認してから実行

### カラムの型変更の場合

```sql
-- フェーズ1: 新カラムを追加
ALTER TABLE users ADD COLUMN age_new INTEGER;

-- フェーズ2: アプリで新カラムに書き込む（両カラムに二重書き）

-- フェーズ3: 既存データをバックフィル
UPDATE users SET age_new = CAST(age_old AS INTEGER);

-- フェーズ4: アプリで新カラムのみ使う

-- フェーズ5: 旧カラムを削除
ALTER TABLE users DROP COLUMN age_old;
```

## NOT NULL 追加の手順

```sql
-- NG: 既存データがある場合にこれをやると失敗する
ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL;

-- OK: デフォルト値と同時に追加
ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- または: NULLableで追加 → バックフィル → NOT NULL制約を追加
ALTER TABLE orders ADD COLUMN status VARCHAR(20);
UPDATE orders SET status = 'pending' WHERE status IS NULL;
ALTER TABLE orders MODIFY COLUMN status VARCHAR(20) NOT NULL;
```

## チェックリスト

- [ ] マイグレーションファイルに Up と Down（ロールバック）の両方を書いた
- [ ] ローカルで Up → Down → Up を確認した
- [ ] 対象テーブルの行数を確認し、実行時間を見積もった
- [ ] 破壊的変更（削除・型変更）の場合は2段階リリース計画を立てた
- [ ] NOT NULL 追加の場合はデフォルト値またはバックフィルを用意した
- [ ] ステージング環境で検証した
- [ ] 本番反映後のスキーマ確認クエリを準備した

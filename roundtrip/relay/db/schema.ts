import { sql } from 'drizzle-orm';
import { sqliteTable, text, integer, uniqueIndex } from 'drizzle-orm/sqlite-core';
export const studio = sqliteTable('studio', {
  id: integer('id').primaryKey(), photoId: text('photo_id').notNull(),
  revision: text('revision').notNull(), label: text('label').notNull(),
  title: text('title').notNull(), heartbeat: integer('heartbeat').notNull(),
  accepting: integer('accepting').notNull(),
});
export const requests = sqliteTable('requests', {
  id: text('id').primaryKey(), baseRevision: text('base_revision').notNull(),
  baseLabel: text('base_label').notNull(), feedback: text('feedback').notNull(),
  status: text('status').notNull(), message: text('message').notNull(),
  resultLabel: text('result_label'), created: integer('created').notNull(), updated: integer('updated').notNull(),
}, t => [uniqueIndex('one_active_request').on(sql`(1)`).where(sql`${t.status} IN ('requested','running','verifying')`)]);

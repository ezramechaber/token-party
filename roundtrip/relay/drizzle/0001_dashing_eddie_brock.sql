CREATE TABLE `comments` (
	`id` text PRIMARY KEY NOT NULL,
	`photo_id` text NOT NULL,
	`revision_id` text NOT NULL,
	`text` text NOT NULL,
	`created` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `gallery_revisions` (
	`id` text PRIMARY KEY NOT NULL,
	`photo_id` text NOT NULL,
	`label` text NOT NULL,
	`summary` text NOT NULL,
	`object_key` text NOT NULL,
	`created` integer NOT NULL
);

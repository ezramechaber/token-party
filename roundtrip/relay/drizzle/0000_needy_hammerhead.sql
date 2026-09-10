CREATE TABLE `requests` (
	`id` text PRIMARY KEY NOT NULL,
	`base_revision` text NOT NULL,
	`base_label` text NOT NULL,
	`feedback` text NOT NULL,
	`status` text NOT NULL,
	`message` text NOT NULL,
	`result_label` text,
	`created` integer NOT NULL,
	`updated` integer NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `one_active_request` ON `requests` ((1)) WHERE "requests"."status" IN ('requested','running','verifying');--> statement-breakpoint
CREATE TABLE `studio` (
	`id` integer PRIMARY KEY NOT NULL,
	`photo_id` text NOT NULL,
	`revision` text NOT NULL,
	`label` text NOT NULL,
	`title` text NOT NULL,
	`heartbeat` integer NOT NULL,
	`accepting` integer NOT NULL
);

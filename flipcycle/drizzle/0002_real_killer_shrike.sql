ALTER TABLE `collaborators` ADD `createdById` int NOT NULL;--> statement-breakpoint
ALTER TABLE `collaborators` ADD `userId` int;--> statement-breakpoint
ALTER TABLE `comps` ADD `createdById` int NOT NULL;--> statement-breakpoint
ALTER TABLE `documents` ADD `createdById` int NOT NULL;--> statement-breakpoint
ALTER TABLE `expenses` ADD `createdById` int NOT NULL;
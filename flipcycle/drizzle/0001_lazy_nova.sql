CREATE TABLE `collaborators` (
	`id` int AUTO_INCREMENT NOT NULL,
	`projectId` int NOT NULL,
	`email` varchar(320) NOT NULL,
	`name` varchar(160),
	`collaboratorRole` enum('owner','editor','viewer') NOT NULL DEFAULT 'viewer',
	`collaboratorStatus` enum('invited','active') NOT NULL DEFAULT 'invited',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `collaborators_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `comps` (
	`id` int AUTO_INCREMENT NOT NULL,
	`projectId` int NOT NULL,
	`address` varchar(255) NOT NULL,
	`salePrice` int NOT NULL DEFAULT 0,
	`sqft` int NOT NULL DEFAULT 0,
	`beds` int NOT NULL DEFAULT 0,
	`baths` int NOT NULL DEFAULT 0,
	`soldAt` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `comps_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `documents` (
	`id` int AUTO_INCREMENT NOT NULL,
	`projectId` int NOT NULL,
	`name` varchar(255) NOT NULL,
	`docType` enum('contracts','photos','inspection_reports','other') NOT NULL DEFAULT 'other',
	`fileKey` varchar(512) NOT NULL,
	`url` varchar(1024) NOT NULL,
	`mimeType` varchar(128),
	`size` int NOT NULL DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `documents_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `expenses` (
	`id` int AUTO_INCREMENT NOT NULL,
	`projectId` int NOT NULL,
	`category` enum('labor','materials','permits') NOT NULL,
	`description` varchar(255) NOT NULL,
	`estimate` int NOT NULL DEFAULT 0,
	`actual` int NOT NULL DEFAULT 0,
	`vendor` varchar(160),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `expenses_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `projects` (
	`id` int AUTO_INCREMENT NOT NULL,
	`ownerId` int NOT NULL,
	`name` varchar(160) NOT NULL,
	`address` varchar(255) NOT NULL,
	`stage` enum('Acquisition','Rehab','Listed','Sold') NOT NULL DEFAULT 'Acquisition',
	`purchasePrice` int NOT NULL DEFAULT 0,
	`repairCosts` int NOT NULL DEFAULT 0,
	`arv` int NOT NULL DEFAULT 0,
	`downPayment` int NOT NULL DEFAULT 0,
	`loanAmount` int NOT NULL DEFAULT 0,
	`interestRate` int NOT NULL DEFAULT 0,
	`holdingMonths` int NOT NULL DEFAULT 6,
	`closingCosts` int NOT NULL DEFAULT 0,
	`sellingCosts` int NOT NULL DEFAULT 0,
	`sqft` int NOT NULL DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `projects_id` PRIMARY KEY(`id`)
);

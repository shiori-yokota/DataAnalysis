CREATE TABLE `mixing_task` (
	`recipe_id` varchar(100) NOT NULL,
	`task_id` int(11) NOT NULL,
    `step` int(2) NOT NULL,
    `sentence` text NOT NULL,
    `materials` text NOT NULL,
    PRIMARY KEY (`recipe_id`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
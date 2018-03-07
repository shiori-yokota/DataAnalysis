CREATE TABLE `user_state` (
	`user_id` int(11) NOT NULL,
	`task_id` int(11) NOT NULL,
    PRIMARY KEY (`user_id`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
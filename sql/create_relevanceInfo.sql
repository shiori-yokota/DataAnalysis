CREATE TABLE `relevance_data` (
	`user_id` int(11) NOT NULL,
    `task_id` int(11) NOT NULL,
    `tool_name` varchar(100) NOT NULL,
    `recording_id` int(11) NOT NULL,
    PRIMARY KEY (`user_id`, `task_id`, `tool_name`, `recording_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
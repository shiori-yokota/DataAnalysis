CREATE TABLE `user_data` (
	`user_id` int(11) NOT NULL,
    `user_name` varchar(100) NOT NULL,
    `user_password` varchar(100) NOT NULL,
    `user_age` int(2) NOT NULL,
    PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
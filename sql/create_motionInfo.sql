CREATE TABLE `motion_data` (
  `recording_id` int(11) NOT NULL,
  `elapsed_time` int(11) NOT NULL,
  `data_type` int(11) NOT NULL,
  `motion_data` text NOT NULL,
  PRIMARY KEY (`elapsed_time`,`data_type`,`recording_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
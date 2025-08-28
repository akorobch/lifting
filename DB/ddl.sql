use `lifting-replica`;

DROP TABLE IF EXISTS `set`;
DROP TABLE IF EXISTS `workout`;
DROP TABLE IF EXISTS `exercise`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `schema_version`;

CREATE TABLE `schema_version` (
  `id` int NOT NULL AUTO_INCREMENT,
  `version` varchar(20) NOT NULL,
  `applied_on` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(25) NOT NULL,
  `email` varchar(45) NOT NULL,
  `enabled` tinyint DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `exercise` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(225) DEFAULT NULL,
  `date_started` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `workout` (
  `id` int NOT NULL AUTO_INCREMENT,
  `workout_date` datetime NOT NULL,
  `comment` varchar(245) DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_workout_user` (`user_id`),
  CONSTRAINT `fk_workout_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `set` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exercise_id` int NOT NULL,
  `weight` float NOT NULL,
  `reps` int unsigned NOT NULL,
  `comment` varchar(245) DEFAULT NULL,
  `workout_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_set_exercise` (`exercise_id`),
  KEY `fk_set_workout` (`workout_id`),
  CONSTRAINT `fk_set_exercise` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_set_workout` FOREIGN KEY (`workout_id`) REFERENCES `workout` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

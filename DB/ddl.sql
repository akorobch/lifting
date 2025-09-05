-- ===========================================
-- Create database if it doesn't exist
-- ===========================================
CREATE DATABASE IF NOT EXISTS `lifting_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `lifting_db`;

-- ===========================================
-- Drop existing tables safely
-- ===========================================
START TRANSACTION;
DROP TABLE IF EXISTS `set`;
DROP TABLE IF EXISTS `workout`;
DROP TABLE IF EXISTS `exercise`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `schema_version`;
COMMIT;
-- Commit message: Dropped all existing tables to start fresh

-- ===========================================
-- Create schema_version table
-- ===========================================
START TRANSACTION;
CREATE TABLE IF NOT EXISTS `schema_version` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` VARCHAR(20) NOT NULL,
  `applied_on` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
COMMIT;
-- Commit message: Created schema_version table

-- ===========================================
-- Create user table
-- ===========================================
START TRANSACTION;
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(20) NOT NULL,
  `last_name` VARCHAR(25) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `enabled` TINYINT DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
);
COMMIT;
-- Commit message: Created user table

-- ===========================================
-- Create exercise table
-- ===========================================
START TRANSACTION;
CREATE TABLE IF NOT EXISTS `exercise` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(225) DEFAULT NULL,
  `date_started` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
);
COMMIT;
-- Commit message: Created exercise table

-- ===========================================
-- Create workout table
-- ===========================================
START TRANSACTION;
CREATE TABLE IF NOT EXISTS `workout` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `workout_date` DATETIME NOT NULL,
  `comment` VARCHAR(245) DEFAULT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_workout_user` (`user_id`),
  CONSTRAINT `fk_workout_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
COMMIT;
-- Commit message: Created workout table with foreign key to user

-- ===========================================
-- Create set table
-- ===========================================
START TRANSACTION;
CREATE TABLE IF NOT EXISTS `set` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exercise_id` INT NOT NULL,
  `weight` FLOAT NOT NULL,
  `reps` INT UNSIGNED NOT NULL,
  `comment` VARCHAR(245) DEFAULT NULL,
  `workout_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_set_exercise` (`exercise_id`),
  KEY `fk_set_workout` (`workout_id`),
  CONSTRAINT `fk_set_exercise` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_set_workout` FOREIGN KEY (`workout_id`) REFERENCES `workout` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
COMMIT;
-- Commit message: Created set table with foreign keys to exercise and workout

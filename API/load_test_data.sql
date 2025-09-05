START TRANSACTION;
INSERT INTO `schema_version` VALUES
(1, '1.0.0', '2025-08-27 20:26:29', 'Initial schema creation with exercise, set, workout tables'),
(2, '1.0.1', '2025-08-28 09:26:29', 'Added user table');
COMMIT;

START TRANSACTION;
INSERT INTO `user` VALUES
(1, 'Alex', 'Korobchevsky', 'akorobch@devops-innovations.com', 1),
(2, 'Rachita', 'D', 'rachita@devops-innovations.com', 1);
COMMIT;

START TRANSACTION;
INSERT INTO `exercise` VALUES
(1, 'Press', 'Standing shoulder press', '2025-08-25 22:00:00'),
(2, 'Squat', 'High bar back Squat', '2025-08-25 22:00:00'),
(3, 'Deadlift', 'Classic style with regular bar', '2025-08-25 22:00:00'),
(4, 'Bench', 'Flat wide-grip bench press', '2025-08-29 22:00:00'),
(5, 'Row', 'Bent row bar row', '2025-08-29 22:00:00'),
(6, 'Front Squat', 'Olympic style front squat', '2025-08-29 22:00:00');
COMMIT;

START TRANSACTION;
INSERT INTO `workout` VALUES
(1, '2025-08-25 22:00:00', 'First workout!', 1),
(4, '2025-08-28 22:00:00', 'Future workout', 1),
(5, '2025-08-30 22:00:00', 'New workout', 1),
(6, '2025-08-30 22:00:00', 'Not so new workout', 1);
COMMIT;

START TRANSACTION;
INSERT INTO `set` VALUES
(1, 2, 155, 5, 'Feeling sore', 1),
(2, 1, 95, 5, 'Moderate effort', 1),
(3, 3, 185, 5, 'Nice and easy', 1),
(4, 2, 165, 5, 'Still easy', 4),
(5, 1, 100, 5, 'Getting tricky', 4),
(6, 3, 195, 5, 'No problems', 4),
(7, 6, 135, 5, 'Pain in the wrists', 5),
(8, 4, 135, 5, 'Easy balance', 5),
(9, 5, 148, 4, 'Bar slipped', 5),
(10, 6, 145, 5, 'Wrists are getting better', 6),
(11, 4, 145, 5, 'Minimal effort', 6),
(12, 5, 148, 5, 'Feels good', 6);
COMMIT;

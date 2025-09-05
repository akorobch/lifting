DROP USER 'lifting_app'@'localhost';
CREATE USER 'lifting_app'@'localhost' IDENTIFIED BY 'Gr8P$ss!';
GRANT CREATE, ALTER, DROP, REFERENCES ON `lifting-db`.* TO 'lifting_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `lifting-db`.* TO 'lifting_app'@'localhost';
FLUSH PRIVILEGES;
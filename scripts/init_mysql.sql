CREATE DATABASE IF NOT EXISTS tripmind
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'tripmind'@'localhost' IDENTIFIED BY 'tripmind123';
GRANT ALL PRIVILEGES ON tripmind.* TO 'tripmind'@'localhost';
FLUSH PRIVILEGES;

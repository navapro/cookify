CREATE DATABASE IF NOT EXISTS cookify_db;
USE cookify_db;

CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ingredients TEXT,
    instructions TEXT
);

-- fill out with whatever (we can work on this today)
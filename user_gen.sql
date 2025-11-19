CREATE TABLE sg_user (
    sg_user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE flash_card_set (
    flash_card_set_id SERIAL PRIMARY KEY,
    sg_user_id INT NOT NULL,
);

CREATE TABLE flash_card (
    flash_card_id SERIAL PRIMARY KEY,
    flash_card_set_id INT NOT NULL,
    question VARCHAR(255) NOT NULL,
    answer VARCHAR(255) NOT NULL
);

CREATE TABLE textbook (
    textbook_id SERIAL PRIMARY KEY

);

CREATE TABLE summary (
    summary_id SERIAL PRIMARY KEY
    sg_user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL
);
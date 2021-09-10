-- $ sqlite3 posts.db < posts.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    post_id INTEGER primary key,
    user_id VARCHAR,
    text VARCHAR,
    timestamp VARCHAR
);

COMMIT;

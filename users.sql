-- $ sqlite3 users.db < users.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS followers;

CREATE TABLE users (
    user_id VARCHAR primary key,
    password VARCHAR,
    email VARCHAR
);

CREATE TABLE followers (
    user_id text,
    follow_id text,
    primary key (user_id, follow_id),
    foreign key (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE NO ACTION,
    foreign key (follow_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE NO ACTION
);

INSERT INTO users(user_id, password, email) VALUES ('Michael', 'SqwkBoi', 'michael@site.com');
INSERT INTO users(user_id, password, email) VALUES ('Joe', 'Clone3', 'joe@site.com');
INSERT INTO users(user_id, password, email) VALUES ('Chris', '545&545', 'chris@site.com');
INSERT INTO users(user_id, password, email) VALUES ('Zaid', 'Eripmav', 'zaid@site.com');
INSERT INTO users(user_id, password, email) VALUES ('Raul', '2Raptor4', 'raul@site.com');
INSERT INTO users(user_id, password, email) VALUES ('Ben', 'Fum6le', 'ben@site.com');

INSERT INTO followers(user_id, follow_id) VALUES ('Michael','Joe');
INSERT INTO followers(user_id, follow_id) VALUES ('Michael','Raul');
INSERT INTO followers(user_id, follow_id) VALUES ('Michael','Ben');

INSERT INTO followers(user_id, follow_id) VALUES ('Zaid','Michael');
INSERT INTO followers(user_id, follow_id) VALUES ('Zaid','Raul');
INSERT INTO followers(user_id, follow_id) VALUES ('Zaid','Joe');

INSERT INTO followers(user_id, follow_id) VALUES ('Ben','Zaid');
INSERT INTO followers(user_id, follow_id) VALUES ('Chris','Raul');
INSERT INTO followers(user_id, follow_id) VALUES ('Raul','Chris');
INSERT INTO followers(user_id, follow_id) VALUES ('Joe','Michael');

COMMIT;

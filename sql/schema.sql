DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id integer primary key autoincrement,
  username string not null unique,
  password string not null,
  nickname string not null unique,
  is_superuser boolean not null default false,
  disabled boolean not null default false
);

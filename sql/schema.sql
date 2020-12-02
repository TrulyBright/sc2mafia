DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id integer primary key autoincrement,
  username string not null,
  password string not null,
  nickname string not null,
  is_superuser boolean not null default false,
  disabled boolean not null default false
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id integer primary key autoincrement,
  naverId string not null unique,
  nickname string not null unique,
  is_superuser boolean not null default false,
  disabled boolean not null default false
);

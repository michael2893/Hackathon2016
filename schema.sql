drop table if exists tracks;
create table tracks (
  id integer primary key autoincrement,
  title text not null,
  artist text not null,
  album text not null,
  track_num integer not null
);
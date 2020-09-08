-- :name create_table_tag
create table tag (
  id integer primary key autoincrement,
  name text unique not null,
  description text not null,
  created_at datetime not null,
  updated_at datetime not null
);

-- :name create_table_file
create table file (
  id integer primary key autoincrement,
  uri text unique,
  name text not null,
  description text not null,
  mime_type text not null,
  created_at datetime not null,
  updated_at datetime not null
);

-- :name create_table_filetag
create table filetag (
  file integer references file(id) on delete cascade,
  tag integer references tag(id) on delete cascade,
  value text not null,
  created_at datetime not null,
  updated_at datetime not null,
  constraint filetag_pk primary key (file, tag) 
) without rowid;
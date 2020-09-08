-- :name create_table_tag
create table tag (
  id integer primary key autoincrement,
  name text unique,
  description text,
  created_at datetime,
  updated_at datetime
);

-- :name create_table_file
create table file (
  id integer primary key autoincrement,
  uri text unique,
  name text,
  description text,
  mime_type text,
  created_at datetime,
  updated_at datetime
);

-- :name create_table_filetag
create table filetag (
  file integer references file(id) on delete cascade,
  tag integer references tag(id) on delete cascade,
  value text,
  created_at datetime,
  updated_at datetime,
  constraint filetag_pk primary key (file, tag) 
) without rowid;
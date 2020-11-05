-- :name migrate_0_1_0_create_table_tag
create table if not exists tag (
  id integer primary key autoincrement,
  name text unique not null,
  description text not null,
  created_at datetime not null,
  updated_at datetime not null
);

-- :name migrate_0_1_0_create_table_file
create table if not exists file (
  id integer primary key autoincrement,
  uri text unique,
  name text not null,
  description text not null,
  mime_type text not null,
  created_at datetime not null,
  updated_at datetime not null
);

-- :name migrate_0_1_0_create_table_filetag
create table if not exists filetag (
  file integer references file(id) on delete cascade,
  tag integer references tag(id) on delete cascade,
  value text not null,
  created_at datetime not null,
  updated_at datetime not null,
  constraint filetag_pk primary key (file, tag) 
) without rowid;

-- :name migrate_0_1_0_create_table_config
create table if not exists config (
  key text primary key,
  value text,
  created_at datetime not null,
  updated_at datetime not null
) without rowid;
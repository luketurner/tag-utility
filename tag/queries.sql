-- :name add_file
insert into file (uri, name, description, mime_type, created_at, updated_at)
         values (:uri, :name, coalesce(:description, ''), :mime_type, current_timestamp, current_timestamp)
on conflict(uri) do update set updated_at=current_timestamp,
                               name=coalesce(:name, name),
                               mime_type=coalesce(:mime_type, mime_type),
                               description=coalesce(:description, description);

-- :name add_tag
insert into tag (name, description, created_at, updated_at)
         values (:name, coalesce(:description, ''), current_timestamp, current_timestamp)
on conflict(name) do update set updated_at=current_timestamp,
                                description=coalesce(:description, description);

-- :name add_filetag
with f as (select * from file where uri = :file_uri),
     t as (select * from tag where name = :tag_name)
insert into filetag (file, tag, value, created_at, updated_at)
select f.id, t.id, :tag_value, current_timestamp, current_timestamp from f, t where true
on conflict(file, tag) do update set updated_at=current_timestamp,
                                      value=:tag_value;

-- :name get_file :one
select * from file where uri = :uri;

-- :name get_tag :one
select * from tag where name = :name;

-- :name get_filetag :one
select * from filetag, 
              file on filetag.file = file.id,
              tag on filetag.tag = tag.id 
where file.uri = :file_uri and tag.name = :tag_name;

-- :name get_tags_for_file :many
select * from filetag, 
              file on filetag.file = file.id,
              tag on filetag.tag = tag.id
where file.uri = :file_uri
limit coalesce(cast (:limit as integer), -1);

-- :name delete_file
delete from file where uri = :uri;

-- :name delete_tag
delete from tag where name = :name;

-- :name delete_filetag
delete from filetag where file in (select id from file where uri = :file_uri) and
                           tag in (select id from tag where name = :tag_name);

-- :name count_tags :scalar
select count(*) from tag;

-- :name count_files :scalar
select count(*) from file;

-- :name count_filetags :scalar
select count(*) from filetag;

-- :name search_filetags :many
with possible_matches as (
  select filetag.file,
         count(tag.name) as tagcount
  from filetag,
       tag on filetag.tag = tag.id,
       file on filetag.file = file.id
  where case when :filter_tags then tag.name in :tags else true end
    and case when :filter_exclude_tags then tag.name not in :exclude_tags else true end
    and case when :filter_mime_types then file.mime_type in :mime_types else true end
    and case when :filter_exclude_mime_types then file.mime_type not in :exclude_mime_types else true end
  group by file.id
)
select file.*
from possible_matches,
     file on file.id = possible_matches.file
where case when :filter_tags then tagcount = :tag_count else true end;

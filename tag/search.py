import pony.orm as orm

def search(conn, tags):

    # TODO - investigate efficiency / can we do this better?

    tags_allowed = orm.select(t.id for t in conn.Tag if t.name in tags)

    query = orm.select(f for f in conn.File if f.file_tags.tag in tags_allowed )

    for tag in tags:
        query = query.where(lambda f: orm.JOIN(tag in f.file_tags.tag.name))
    
    print("query", query.get_sql())
    return query
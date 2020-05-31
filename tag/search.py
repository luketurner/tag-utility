import pony.orm as orm

def search(conn, tags):

    query = orm.select(f for f in conn.File)

    for tag in tags:
        query = query.where(lambda f: orm.JOIN(tag in f.file_tags.tag.name))
    
    return query
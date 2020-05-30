from contextlib import contextmanager
from collections import namedtuple
from datetime import datetime

from pony.orm import *

Connection = namedtuple('Connection', ['Config', 'File', 'Tag', 'FileTag', 'db'])

@contextmanager
def connect(filename, create_db=True):
  """Context manager for creating a connection to a tag database."""

  db = Database()

  class Config(db.Entity):
    key = PrimaryKey(str)
    value = Optional(str)

  class File(db.Entity):
    id = PrimaryKey(int, auto=True)
    uri = Required(str, unique=True, index=True)
    mime_type = Optional(str)
    name = Optional(str)
    description = Optional(str)
    data = Optional(bytes)
    file_tags = Set('FileTag')
    created_at = Required(datetime)
    updated_at = Required(datetime)

  class Tag(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    description = Optional(str)
    file_tags = Set('FileTag')
    created_at = Required(datetime)
    updated_at = Required(datetime)

  class FileTag(db.Entity):
    file = Required(File)
    tag = Required(Tag)
    PrimaryKey(file, tag)
    value = Optional(str)
    created_at = Required(datetime)
    updated_at = Required(datetime)

  db.bind(provider='sqlite', filename=filename, create_db=create_db)
  db.generate_mapping(create_tables=create_db)

  with db_session:
    yield Connection(db=db, Config=Config, File=File, Tag=Tag, FileTag=FileTag)

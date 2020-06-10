import sys
from sqlite3 import version as sqlite_version
import pony.orm as pony
import os.path
import tag.util as util
from .error import TagException

__version__ = "0.0.1"


from collections import namedtuple

from contextlib import contextmanager
from datetime import datetime


Connection = namedtuple("Connection", ["Config", "File", "Tag", "FileTag", "db"])


@contextmanager
def connect(filename, create_db=True):
    """Context manager for creating a connection to a tag database."""

    # Absolutize relative paths w.r.t. the current working directory,
    # which is needed because Pony absolutizes w.r.t. the module code directory instead.
    filename = os.path.abspath(filename)

    db = pony.Database()

    class Config(db.Entity):
        key = pony.PrimaryKey(str)
        value = pony.Optional(str)

    class File(db.Entity):
        id = pony.PrimaryKey(int, auto=True)
        uri = pony.Required(str, unique=True, index=True)
        mime_type = pony.Optional(str)
        name = pony.Optional(str)
        description = pony.Optional(str)
        data = pony.Optional(bytes)
        file_tags = pony.Set("FileTag", cascade_delete=True)
        created_at = pony.Required(datetime)
        updated_at = pony.Required(datetime)

    class Tag(db.Entity):
        id = pony.PrimaryKey(int, auto=True)
        name = pony.Required(str, unique=True, index=True)
        description = pony.Optional(str)
        file_tags = pony.Set("FileTag", cascade_delete=True)
        created_at = pony.Required(datetime)
        updated_at = pony.Required(datetime)

    class FileTag(db.Entity):
        file = pony.Required(File, index=True)
        tag = pony.Required(Tag, index=True)
        pony.PrimaryKey(file, tag)
        value = pony.Optional(str, index=True)
        created_at = pony.Required(datetime)
        updated_at = pony.Required(datetime)

    db.bind(provider="sqlite", filename=filename, create_db=create_db)
    db.generate_mapping(create_tables=create_db)

    with pony.db_session:
        yield Connection(db=db, Config=Config, File=File, Tag=Tag, FileTag=FileTag)


def version():
    """Returns a human-readable version string."""
    return "{} (python {}; sqlite3 {})".format(
        __version__, "{}.{}.{}".format(*sys.version_info[0:3]), sqlite_version
    )


def version_info():
    """Returns a tuple representation of the version, with three numbers: (major, minor, patch)."""
    return map(int, __version__.split("."))


def add_file(conn, filename):

    uri = util.path_to_uri(filename)
    mime_type = util.guess_mime_type(filename)
    name = os.path.basename(filename)
    created_at = datetime.now()
    updated_at = datetime.now()
    new_instance = None
    try:
        new_instance = conn.File(
            uri=uri,
            mime_type=mime_type,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
        )
        pony.flush()
        return new_instance
    except Exception as e:
        util.parse_integrity_error(conn.File, e)
        if new_instance:
            new_instance.delete()  # prevent our instance from failing future flushes in the same transaction

        existing_instance = pony.get(x for x in conn.File if x.uri == uri)
        existing_instance.set(mime_type=mime_type, name=name, updated_at=updated_at)
        pony.flush()
        return existing_instance


def add_tag(conn, name):
    created_at = datetime.now()
    updated_at = datetime.now()
    new_instance = None
    try:
        new_instance = conn.Tag(name=name, created_at=created_at, updated_at=updated_at)
        pony.flush()
        return new_instance
    except Exception as e:
        util.parse_integrity_error(conn.Tag, e)
        if new_instance:
            new_instance.delete()  # prevent our instance from failing future flushes in the same transaction
        existing_instance = pony.get(x for x in conn.Tag if x.name == name)
        pony.flush()
        return existing_instance


def add_file_tags(conn, filename, tags=None):
    file = add_file(conn, filename)
    file_tags = []

    created_at = datetime.now()
    updated_at = datetime.now()
    new_instance = None

    for name, value in (tags or {}).items():
        value = '' if value is None else value # None should be treated identically to an empty string
        tag = add_tag(conn, name=name)
        new_instance = None
        try:
            new_instance = conn.FileTag(file=file, tag=tag, created_at=created_at, updated_at=updated_at, value=value)
            pony.flush()
            file_tags.append(new_instance)
        except Exception as e:
            util.parse_integrity_error(conn.FileTag, e)
            if new_instance:
                new_instance.delete()  # prevent our instance from failing future flushes in the same transaction
            existing_instance = pony.get(
                x for x in conn.FileTag if x.file == file and x.tag == tag
            )
            existing_instance.set(value=value, updated_at=updated_at)
            pony.flush()
            file_tags.append(existing_instance)

    return file_tags


def delete_file(conn, filename):
    return pony.delete(x for x in conn.File if x.uri == util.path_to_uri(filename))


def delete_file_tags(conn, filename, tags):
    return pony.delete(
        x
        for x in conn.FileTag
        if x.file.uri == util.path_to_uri(filename) and x.tag.name in tags
    )


def delete_tag(conn, name):
    return pony.delete(x for x in conn.Tag if x.name == name)


def get_file(conn, filename):
    return pony.get(x for x in conn.File if x.uri == path_to_uri(filename))


def get_file_tags(conn, filename):
    return pony.select(x for x in conn.FileTag if x.file.uri == path_to_uri(filename))


def get_tag(conn, name):
    return pony.get(x for x in conn.Tag if x.name == name)


def search(conn, tags):

    # TODO - investigate efficiency / can we do this better?

    tags_allowed = pony.select(t.id for t in conn.Tag if t.name in tags)

    query = pony.select(f for f in conn.File if f.file_tags.tag in tags_allowed)

    for tag in tags:
        query = query.where(lambda f: pony.JOIN(tag in f.file_tags.tag.name))

    return query

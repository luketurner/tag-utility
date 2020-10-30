import os.path

from sys import version_info as sys_version_info
from sqlite3 import version as sqlite_version

import pugsql
import urllib.parse
import tag.util as util

query = pugsql.module(os.path.dirname(__file__))


__version__ = "0.0.1"


def version():
    """Returns a human-readable version string."""
    return "{} (python {}; sqlite3 {})".format(
        __version__, "{}.{}.{}".format(*sys_version_info[0:3]), sqlite_version
    )


def version_info():
    """Returns a tuple representation of the version, with three numbers: (major, minor, patch)."""
    return map(int, __version__.split("."))


def connect(filename, migrate=False):
    """Opens a connection to the SQLite database specified by filename, which may or may not already exist.
    If the migration argument is True, the database schema will be created."""
    conn_url = f"sqlite:///file:{urllib.parse.quote(filename)}?mode=rwc&uri=true"
    query.connect(conn_url)
    if migrate:
        query.create_table_file()
        query.create_table_tag()
        query.create_table_filetag()


def disconnect():
    query.disconnect()


def add_file(filename, description=None, mime_type=None, name=None):
    query.add_file(
        uri=util.path_to_uri(filename),
        mime_type=mime_type or util.guess_mime_type(filename),
        name=name or os.path.basename(filename),
        description=description,
    )


def add_tag(name, description=None):
    query.add_tag(name=name, description=description)


def add_filetags(filename, tags, create_tags=True, create_file=True):
    file_uri = util.path_to_uri(filename)

    if create_file:
        add_file(filename)

    if len(tags) == 0:
        return

    if create_tags:
        query.add_tag(*[{"name": name, "description": None} for name in tags.keys()])

    query.add_filetag(
        *[
            {"file_uri": file_uri, "tag_name": name, "tag_value": value or ""}
            for name, value in tags.items()
        ]
    )


def get_file(filename):
    return query.get_file(uri=util.path_to_uri(filename))


def get_tag(name):
    return query.get_tag(name=name)


def get_filetag(filename, tagname):
    return query.get_filetag(file_uri=util.path_to_uri(filename), tag_name=tagname)


def get_tags_for_file(filename, limit=None):
    return query.get_tags_for_file(file_uri=util.path_to_uri(filename), limit=limit)


def get_files_for_tag(tagname, limit=None):
    return query.get_tags_for_file(tag_name=tagname, limit=limit)


def delete_file(filename):
    return query.delete_file(uri=util.path_to_uri(filename))


def delete_tag(name):
    return query.delete_tag(name=name)


def delete_filetag(filename, tagname):
    return query.delete_filetag(file_uri=util.path_to_uri(filename), tag_name=tagname)


def count_files():
    return query.count_files()


def count_filetags():
    return query.count_filetags()


def count_tags():
    return query.count_tags()


def search_filetags(
    tags=None, exclude_tags=None, mime_types=None, exclude_mime_types=None
):
    return query.search_filetags(
        tags=tags or [],
        exclude_tags=exclude_tags or [],
        mime_types=mime_types or [],
        exclude_mime_types=exclude_mime_types or [],
        # Note -- these filter_foo conditionals are used in the query to determine whether the client intended
        # to filter based on the particular element. This is done in Python instead of calculating it in SQL, because
        # I don't know how to determine whether a list parameter is empty in SQL.
        # Possible TODO -- handle this better
        filter_tags=tags is not None,
        filter_exclude_tags=exclude_tags is not None,
        filter_mime_types=mime_types is not None,
        filter_exclude_mime_types=exclude_mime_types is not None,
        # This tag_count is used to get around my inability to figure out the length of the :tags parameter from within the sql expression
        # Possible TODO -- handle this better
        tag_count=len(tags or [])
    )

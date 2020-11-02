import os.path

from sys import version_info as sys_version_info
from sqlite3 import version as sqlite_version

import pugsql
import urllib.parse
import tag.util as util

from sqlalchemy.exc import OperationalError as SqlalchemyOperationalError

query = pugsql.module(os.path.dirname(__file__))


__version__ = "0.1.0"


def version():
    """Returns a human-readable version string."""
    return "{} (python {}; sqlite3 {})".format(
        __version__, "{}.{}.{}".format(*sys_version_info[0:3]), sqlite_version
    )


def version_info():
    """Returns a tuple representation of the version, with three numbers: (major, minor, patch)."""
    return map(int, __version__.split("."))


def database_version_info():
    """Returns a 3-tuple -- e.g. (1, 2, 3) -- that represents the current version
    of the database schema. This is loaded from the database's config table, so there must be an
    open connection for this function to work, unlike the other version functions in this module.
    However, if the config table doesn't exist, this will return the default value (0, 0, 0)."""
    try:
        return map(int, get_config_value('tag_version').split("."))
    except SqlalchemyOperationalError as e:
        if "no such table: config" in e.args[0]:
            return (0, 0, 0)
        else:
            raise e


def connect(filename, migrate=False, strict_versions=True):
    """Opens a connection to the SQLite database specified by filename, which may or may not already exist.
    If the migration argument is True, the database schema will be created."""
    conn_url = f"sqlite:///file:{urllib.parse.quote(filename)}?mode=rwc&uri=true"
    query.connect(conn_url)

    if migrate:
        query.create_table_file()
        query.create_table_tag()
        query.create_table_filetag()
        query.create_table_config()
        if not get_config_value("tag_version"):
            set_config_value("tag_version", __version__)
        
    if strict_versions:
        dbmajor, dbminor, dbpatch = dbversion = database_version_info()
        mymajor, myminor, mypatch = myversion = version_info()
        if dbmajor > mymajor:
            raise TagException(f"Version mismatch with {filename}: it uses {dbversion}, we're using {myversion}")
        if dbmajor < mymajor:
            raise TagException(f"Version mismatch with {filename}: it uses {dbversion}, we're using {myversion}")



def disconnect():
    """Closes the open SQLite connection, if any."""
    query.disconnect()


def get_config_value(key):
    """Returns the value for the given config key,
    or None if the key doesn't exist in the database.
    Config keys should be strings, and the returned value will be a string."""
    result = query.get_config(key=key)
    return result["value"] if result else None


def set_config_value(key, value):
    """Sets the config `key` to the given `value`, overwriting any existing values.
    Both key and value should be strings."""
    query.set_config(key=key, value=value)


def add_file(filename, description=None, mime_type=None, name=None):
    """Adds a `file` object to the tag database.
    If a file object already exists with the same filename, that object will be updated instead of creating a new one.
    If mime_type is not specified, will attempt to guess the MIME type of the file based on its extension.
    If name is not specified, will default to the file's basename (e.g. "foo.txt.")."""
    query.add_file(
        uri=util.path_to_uri(filename),
        mime_type=mime_type or util.guess_mime_type(filename),
        name=name or os.path.basename(filename),
        description=description,
    )


def add_tag(name, description=None):
    """Adds a tag to the tag database. (Note -- this doesn't associate the tag with any files. Use add_filetags for that.)
    If a tag with the same name already exists, the existing tag will be used instead of creating a new one."""
    query.add_tag(name=name, description=description)


def add_filetags(filename, tags, create_tags=True, create_file=True):
    """Adds one or more filetags to the tag database. The filetags are linked to the file given by `filename`.
    The `tags` parameter should be a dict where keys are tag names and values are filetag data (or None to indicate no filetag data.)
    By default, this function will automatically create the associated file and tag records as well if they are missing.
    To disable this behavior (i.e. to create _only_ filetags), use the create_tags and create_file parameters."""
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
    """Returns the file object given by `filename`."""
    return query.get_file(uri=util.path_to_uri(filename))


def get_tag(name):
    """Returns the tag object given by `name`."""
    return query.get_tag(name=name)


def get_filetag(filename, tagname):
    """Returns the filetag object that refers to both the given filename and tagname."""
    return query.get_filetag(file_uri=util.path_to_uri(filename), tag_name=tagname)


def get_tags_for_file(filename, limit=None):
    """Returns a cursor for all the tags that are associated with `filename`.
    The `limit` parameter can be used to control the max number of results to return."""
    return query.get_tags_for_file(file_uri=util.path_to_uri(filename), limit=limit)


def get_files_for_tag(tagname, limit=None):
    """Returns a cursor for all the files that are associated with `tagname`.
    The `limit` parameter can be used to control the max number of results to return."""
    return query.get_tags_for_file(tag_name=tagname, limit=limit)


def delete_file(filename):
    """Deletes the specified file object, if it exists. Also deletes any filetags associated with the deleted file."""

    # Note -- Associated filetags should be handled by foreign key ON CASCADE DELETE clause.
    # However, it seems not all SQLite versions enforce that,
    # so we delete associated filetags manually before deleting the file.
    delete_filetags_for_file(filename)

    return query.delete_file(uri=util.path_to_uri(filename))


def delete_tag(name):
    """Deletes the specified tag object, if it exists. Also deletes any filetags associated with the deleted tag."""

    # Note -- Associated filetags should be handled by foreign key ON CASCADE DELETE clause.
    # However, it seems not all SQLite versions enforce that,
    # so we delete associated filetags manually before deleting the tag.
    delete_filetags_for_tag(name)

    return query.delete_tag(name=name)


def delete_filetag(filename, tagname):
    """Deletes the specified filetag object, if it exists."""
    return query.delete_filetag(file_uri=util.path_to_uri(filename), tag_name=tagname)


def delete_filetags_for_file(filename):
    """Deletes all the filetags associated with given `filename`."""
    return query.delete_tags_for_file(file_uri=util.path_to_uri(filename))


def delete_filetags_for_tag(tagname):
    """Deletes all the filetags associated with given `tagname`."""
    return query.delete_files_for_tag(tag_name=tagname)


def count_files():
    """Returns the number of files in the database."""
    return query.count_files()


def count_filetags():
    """Returns the number of filetags in the database."""
    return query.count_filetags()


def count_tags():
    """Returns the number of tags in the database."""
    return query.count_tags()


def search_files(
    tags=None, exclude_tags=None, mime_types=None, exclude_mime_types=None
):
    """Returns a cursor for all the file objects that match the requested search parameters.
    The `tags` parameter should be an array of tag names, ALL of which must match.
    For the other parameters (e.g. `exclude_tags` or `mime_types`), ANY of them must match."""
    return query.search_files(
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

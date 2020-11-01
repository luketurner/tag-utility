""" This module contains all the code specific to the tag CLI.

You can call the CLI, causing it to take over your program's argv, stdin and stdout, and automatically exiting on completion, with::

  from tag.cli import cli

  cli()
"""

import click

import os.path
import re
import functools
import json
import shlex

import tag.util as util

from tag import (
    connect,
    add_filetags,
    delete_file,
    delete_filetag,
    get_file,
    get_tags_for_file,
    count_files,
    count_tags,
    count_filetags,
    version,
    search_files,
    get_config_value,
    set_config_value
)


@click.group()
@click.option(
    "--database",
    "-d",
    default=None,
    type=click.Path(),
    help="Path to the database to use. If it doesn't exist, it will be created. If unspecified, the first .tag.sqlite file found in the current directory (or its parents) will be used. If no databases are found or specified, the default index.tag.sqlite database will be used (and created if missing).",
)
@click.option(
    "--output",
    "-o",
    default="plain",
    type=click.Choice(["plain", "json"], case_sensitive=False),
    help="Output format to use. The default is 'plain', which has a simple Unixy format. The 'json' format includes more information.",
)
@click.version_option(version())
@click.pass_context
def cli(ctx, database, output):
    """tag is a utility for organizing files in a non-hierarchical way using... guess what... *tags*! 
    
    More specifically, tag provides a CLI for making and interacting with *tag databases*, which are SQLite files with a certain schema.
    
    For example:

    \b
        # adds tag to foo.pdf
        tag add -t foobar foo.pdf 

    \b
        # prints foo.pdf
        tag ls foobar
    """
    ctx.ensure_object(dict)
    database = database or util.try_resolve_db() or "index.tag.sqlite"
    if not os.path.isfile(database) and database[-11:] != ".tag.sqlite":
        database += ".tag.sqlite"
    ctx.obj["db_filename"] = database
    ctx.obj["output_format"] = output


def db_session(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        connect(ctx.obj["db_filename"], migrate=True)
        return ctx.invoke(f, *args, **kwargs)

    return functools.update_wrapper(new_func, f)


@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--tag",
    "-t",
    multiple=True,
    metavar="NAME[=VALUE]",
    help="Specify a tag to add. Can be a simple tag like 'foo', or a key-value pair like 'foo=bar'.",
)
@db_session
def add(file, tag):
    """Adds file(s) to the database with given tags. Files already in the database will be updated in-place."""
    [add_filetags(f, parse_tags(tag)) for f in file]


@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--tag", "-t", multiple=True, metavar="NAME", help="Specify a tag to remove.",
)
@db_session
def rm(file, tag):
    """Removes files and/or tags from the database. The specified tags will be removed from the specified files. If no tags are specified, the files are wholly removed from the database. (Note, this does not affect your actual filesystem.)"""
    if len(tag) == 0:
        [delete_file(f) for f in file]
    else:
        [delete_filetag(f, t) for t in tag for f in file]


@cli.command()
@click.argument("tag", nargs=-1, type=str)
@click.option(
    "--exclude-tag",
    "-e",
    multiple=True,
    help="Exclude files with the given tag, even if they match other criteria. If specified multiple times, files with ANY of the specified tags will be excluded.",
)
@click.option(
    "--mime",
    "-m",
    multiple=True,
    help="Outputs files with the given MIME type. If specified multiple times, files must match ANY of the values.",
)
@click.option(
    "--exclude-mime",
    "-M",
    multiple=True,
    help="Exclude files with the given MIME type, even if they match other criteria. If specified multiple times, files with ANY of the specified values will be excluded.",
)
@db_session
def ls(tag, exclude_tag, mime, exclude_mime):
    """Outputs all the files tagged with given tag(s). If no tags are specified, outputs all the files in the database. If multiple tags are specified, outputs files matching ANY of the tags."""
    output_file_list(
        search_files(
            tags=tag if len(tag) > 0 else None,
            exclude_tags=exclude_tag if len(exclude_tag) > 0 else None,
            mime_types=mime if len(mime) > 0 else None,
            exclude_mime_types=exclude_mime if len(exclude_mime) > 0 else None,
        )
    )


@cli.command()
@click.argument("file", nargs=-1, type=click.Path())
@click.option(
    "--tags", "-t", is_flag=True, help="Show applied tags instead of general metadata."
)
@db_session
def show(file, tags):
    """Outputs details about file(s) in the database."""
    if tags:
        filetags = {}
        for f in file:
            for t in get_tags_for_file(f):
                filetags[t["id"]] = t
        output_filetag_list(filetags.values())
    else:
        output_file_info(get_file(f) for f in file)


@cli.command()
@db_session
def info():
    """Outputs details about the tag database."""
    output_info(
        tag_database=click.get_current_context().obj.get("db_filename"),
        file_count=count_files() or 0,
        tag_count=count_tags() or 0,
        filetag_count=count_filetags() or 0,
    )


@cli.command()
@db_session
@click.argument("key", nargs=-1, type=str)
@click.option("--value", "-v", type=str, help="If specified, overwrites the current value of each KEY with VALUE.")
def config(key, value):
    """Gets/sets the value for the given config key(s).
    By default, the current value of the key(s) are returned without modification.
    If --value/-v is used, the value will be overwritten and then returned."""
    for k in key:
        if value:
            set_config_value(key, value)
        queried_value = get_config_value(key)
        if queried_value:
            click.echo(queried_value)


def parse_tags(tags=None):
    return {
        k: v
        for k, v in map(
            lambda x: x.split("=", 1) if "=" in x else (x, None), tags or []
        )
    }


def pretty_dict(d):
    width = max(len(k) for k in d)
    return "\n".join(
        [
            " {:>{width}} = {}".format(k, "None" if v is None else v, width=width)
            for k, v in d.items()
        ]
    )


def output_info(**kwargs):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        click.echo(json.dumps(kwargs))
    else:
        click.echo(pretty_dict(kwargs))


def output_file_info(files):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        click.echo(json.dumps(list(files)))
    else:
        click.echo("\n\n".join(pretty_dict(d) for d in files))


def output_file_list(files):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        # TODO - fix this to output timestamps
        click.echo(json.dumps(list(files)))
    else:
        [click.echo(_uri_to_relpath(f["uri"]) + "  ", nl=False) for f in files]
        click.echo()


def output_filetag_list(filetags):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        # TODO - fix this to output timestamps
        click.echo(json.dumps(list(filetags)))
    else:
        [click.echo(ft["name"] + "  ", nl=False) for ft in filetags]
        click.echo()


def _uri_to_relpath(uri):
    return shlex.quote(util.uri_to_path(uri)[0])

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

from . import *
from .util import try_resolve_db, uri_to_path

import pony.orm as orm

from . import search
from .error import TagException


@click.group()
@click.option(
    "--database",
    "-d",
    default=None,
    type=click.Path(),
    help="Path to the database to use. If it doesn't exist, it will be created. If unspecified, the first .tag.sqlite file found in the current directory (or its parents) will be used. If no databases are found or specified, an index.tag.sqlite file will be created.",
)
@click.option(
    "--output",
    "-o",
    default="plain",
    type=click.Choice(["plain", "json"], case_sensitive=False),
    help="Output format to use. The default is 'plain', which has a simple Unixy format. The 'json' format includes more information."
)
@click.version_option(version())
@click.pass_context
def cli(ctx, database, output):
    """tag is a utility for organizing files in a non-hierarchical way using... guess what... *tags*! 
    
    More specifically, tag provides a CLI for making and interacting with *tag databases*, which are SQLite files with a certain schema.
    """
    ctx.ensure_object(dict)
    database = database or try_resolve_db() or "index.tag.sqlite"
    if not os.path.isfile(database) and database[-11:] != ".tag.sqlite":
        database += ".tag.sqlite"
    ctx.obj["db_filename"] = database
    ctx.obj["output_format"] = output


def db_session(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        with connect(ctx.obj["db_filename"]) as conn:
            return ctx.invoke(f, conn=conn, *args, **kwargs)

    return functools.update_wrapper(new_func, f)


@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--tag", "-t", multiple=True, metavar="NAME[=VALUE]", help="Specify a tag to add. Can be a simple tag like 'foo', or a key-value pair like 'foo=bar'."
)
@db_session
def add(conn, file, tag):
    """Adds file(s) to the database with given tags. Files already in the database will be updated in-place."""
    [add_file_tags(conn, f, parse_tags(tag)) for f in file]


@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--tag",
    "-t",
    multiple=True,
    metavar="NAME",
    help="Specify a tag to remove.",
)
@db_session
def rm(conn, file, tag):
    """Removes files and/or tags from the database. The specified tags will be removed from the specified files. If no tags are specified, the files are wholly removed from the database. (Note, this does not affect your actual filesystem.)"""
    if len(tag) == 0:
        [delete_file(conn, f) for f in file]
    else:
        [delete_file_tags(conn, f, tag) for f in file]


@cli.command()
@click.argument("tag", nargs=-1, type=str)
@db_session
def ls(conn, tag):
    """Outputs all the files tagged with given tag(s). If no tags are specified, outputs all the files in the database."""
    if len(tag) == 0:
        output_file_list(orm.select(f for f in conn.File))
        return
    output_file_list(search(conn, tags=parse_tags(tag)))


@cli.command()
@click.argument("file", nargs=-1, type=click.Path())
@click.option("--tags", "-t", is_flag=True, help="Show applied tags instead of general metadata.")
@db_session
def show(conn, file, tags):
    """Outputs details about file(s) in the database."""

    if tags:
        filetags = {}
        [filetags.update({ft.tag: ft}) for f in file for ft in get_file_tags(conn, f)]
        output_filetag_list(filetags.values())
    else:
        output_file_info(get_file(conn, f) for f in file)


@cli.command()
@db_session
def info(conn):
    """Outputs details about the tag database."""
    output_info(
        tag_database=click.get_current_context().obj.get("db_filename"),
        file_count=orm.count(x for x in conn.File) or 0,
        tag_count=orm.count(x for x in conn.Tag) or 0,
        filetag_count=orm.count(x for x in conn.FileTag) or 0
    )


def parse_tags(tags):
    return {
        k: v for k, v in map(lambda x: x.split("=", 1) if "=" in x else (x, None), tags)
    }


def pretty_dict(d):
    width = max(len(k) for k in d)
    return "\n".join(
        [" {:>{width}} = {}".format(k, "None" if v is None else v, width=width) for k, v in d.items()]
    )


def output_info(**kwargs):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        click.echo(json.dumps(kwargs))
    else:
        click.echo(pretty_dict(kwargs))

def output_file_info(files):
    fmt = click.get_current_context().obj.get("output_format")

    dicts_to_print = [f.to_dict(exclude=["created_at", "updated_at"]) for f in files]

    if fmt == "json":
        click.echo(json.dumps(dicts_to_print))
    else:
        click.echo("\n\n".join(pretty_dict(d) for d in dicts_to_print))


def output_file_list(files):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        # TODO - fix this to output timestamps
        click.echo(
            json.dumps([f.to_dict(exclude=["created_at", "updated_at"]) for f in files])
        )
    else:
        [click.echo(_uri_to_relpath(f.uri) + "  ", nl=False) for f in files]
        click.echo()


def output_filetag_list(filetags):
    fmt = click.get_current_context().obj.get("output_format")

    if fmt == "json":
        # TODO - fix this to output timestamps
        click.echo(
            json.dumps(
                [ft.to_dict(exclude=["created_at", "updated_at"]) for ft in filetags]
            )
        )
    else:
        [click.echo(ft.tag.name + "  ", nl=False) for ft in filetags]
        click.echo()


def _uri_to_relpath(uri):
    return shlex.quote(uri_to_path(uri)[0])

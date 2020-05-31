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

from . import ingest_file, connect, version
from .util import try_resolve_db

import pony.orm as orm

from . import search
from .error import TagException


@click.group()
@click.option(
    "--database",
    "-d",
    default=None,
    type=click.Path(),
    help="Specify the tag database to use.",
)
@click.option("--output", "-o", default="plain", type=click.Choice(["plain", "json"], case_sensitive=False))
@click.version_option(version())
@click.pass_context
def cli(ctx, database, output):
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
    "--tag", "-t", multiple=True, metavar="NAME[=VALUE]", help="Specify a tag to add."
)
@db_session
def add(conn, file, tag):
    """Add tags to files."""
    print("add", file, tag)
    [ingest_file(conn, f, tags=parse_tags(tag)) for f in file]


@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--tag",
    "-t",
    multiple=True,
    metavar="NAME[=VALUE]",
    help="Specify a tag to remove.",
)
@db_session
def rm(conn, file, tag):
    """Remove tags from files."""
    for f in file:
        print("rm", f, tag)


@cli.command()
@click.argument("tag", nargs=-1, type=str)
@db_session
def ls(conn, tag):
    """Lists files for given tags."""
    if len(tag) == 0:
        output_files(orm.select(f for f in conn.File))
        return
    output_files(search(conn, tags=parse_tags(tag)))


@cli.command()
@click.argument("file", nargs=-1, type=click.Path())
@db_session
def show(conn, file):
    """Shows details about files."""
    for f in file:
        output("show", f)


def parse_tags(tags):
    return {
        k: v
        for k, v in map(
            lambda x: x.split("=", 1) if "=" in x else (x, None), tags
        )
    }


def output_files(files):
    ctx = click.get_current_context()
    fmt = ctx.obj.get("output_format")

    if fmt == "json":
        # TODO - fix this to output timestamps
        click.echo(json.dumps([f.to_dict(exclude=["created_at", "updated_at"]) for f in files]))
    elif fmt == "plain":
        [click.echo(_uri_to_relpath(f.uri) + "  ", nl=False) for f in files]
        click.echo()

def _uri_to_relpath(uri):
    return shlex.quote(os.path.relpath(re.sub(r"^file://", "", uri)))
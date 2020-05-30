""" This module contains all the code specific to the tag CLI.

You can call the CLI, causing it to take over your program's argv, stdin and stdout, and automatically exiting on completion, with::

  from tag.cli import cli

  cli()
"""

import click

import os.path
import re
import functools

from . import ingest_file, connect, version
from .util import try_resolve_db

import pony.orm as orm

from .querylang import emit_term

@click.group()
@click.option("--database", "-d", default=None, type=click.Path(), help="Specify the tag database to use.")
@click.version_option(version())
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)
    database = database or try_resolve_db() or "index.tag.sqlite"
    if not os.path.isfile(database) and database[-11:] != ".tag.sqlite":
        database += ".tag.sqlite"
    ctx.obj["db_filename"] = database

def db_session(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        with connect(ctx.obj["db_filename"]) as conn:
            return ctx.invoke(f, conn=conn, *args, **kwargs)
    return functools.update_wrapper(new_func, f)

@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option("--tag", "-t", multiple=True, metavar="NAME[=VALUE]", help="Specify a tag to add.")
@db_session
def add(conn, file, tag):
    """Add tags to files."""
    print("add", file, tag)
    [ingest_file(conn, f) for f in file]

@cli.command()
@click.argument("file", nargs=-1, type=click.Path(exists=True))
@click.option("--tag", "-t", multiple=True, metavar="NAME[=VALUE]", help="Specify a tag to remove.")
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
        print([os.path.relpath(re.sub(r"^file://", "", uri)) for uri in orm.select(f.uri for f in conn.File)])
        return
    query = orm.select(x.file for x in conn.FileTag)
    for op, lhs, rhs in (emit_term(t, '=') for t in tag):
        print("op", op, "lhs", lhs, "rhs", rhs)
    print([os.path.relpath(re.sub(r"^file://", "", uri)) for uri in query])

@cli.command()
@click.argument("file", nargs=-1, type=click.Path())
@db_session
def show(conn, file):
    """Shows details about files."""
    for f in file:
        print("show", f)
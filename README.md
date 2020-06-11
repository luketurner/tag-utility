# tag-utility

> **WARNING:** `tag` is a work in progress! Use at your own risk!

`tag` is a CLI utility (and Python library) for organizing files in a non-hierarchical way using... *tags*. (Surprise!) A simple example:

``` bash
# adds the tag "foo" with value "bar" to myphoto.jpg
tag add -t foo=bar myphoto.jpg

# opens myphoto.jpg in feh image viewer
tag ls foo | feh -f -
```

Tags are stored in SQLite database(s) using a well-defined schema. They can be bare annotations (e.g. `foo`) or they can have a value (e.g. `foo=bar`). The `tag` utility's focused goal is to read and write the data in these files, which are called *tag databases*.

# Getting Started

``` bash
# NOTE: Only tested with Python 3.8+
pip install git+https://github.com/luketurner/tag-utility.git
```

# CLI Documentation

CLI documentation from `tag --help` can be seen below. (Note, this doesn't include all the documentation for sub-commands.)

```
Usage: tag [OPTIONS] COMMAND [ARGS]...

  tag is a utility for organizing files in a non-hierarchical way using...
  guess what... *tags*!

  More specifically, tag provides a CLI for making and interacting with *tag
  databases*, which are SQLite files with a certain schema.

  For example:

      # adds tag to foo.pdf
      tag add -t foobar foo.pdf 

      # prints foo.pdf
      tag ls foobar

Options:
  -d, --database PATH        Path to the database to use. If it doesn't exist,
                             it will be created. If unspecified, the first
                             .tag.sqlite file found in the current directory
                             (or its parents) will be used. If no databases
                             are found or specified, the default
                             index.tag.sqlite database will be used (and
                             created if missing).

  -o, --output [plain|json]  Output format to use. The default is 'plain',
                             which has a simple Unixy format. The 'json'
                             format includes more information.

  --version                  Show the version and exit.
  --help                     Show this message and exit.

Commands:
  add   Adds file(s) to the database with given tags.
  info  Outputs details about the tag database.
  ls    Outputs all the files tagged with given tag(s).
  rm    Removes files and/or tags from the database.
  show  Outputs details about file(s) in the database.
```

# Usage as a Library

The `tag` utility can also be imported and used as a Python library. For now, this is considered a power-user mode and isn't fully documented, nor is the API versioned.

Simple usage example:

``` python
from tag import *

with connect("mytags.tag.sqlite") as conn:
    assert len(get_file_tags(conn, "foo.pdf")) == 0

    add_file_tags(conn, "foo.pdf", { "foo": "baz", "bar": None })
    assert len(get_file_tags(conn, "foo.pdf")) == 2

    delete_file_tags(conn, "foo.pdf", ["bar"])
    assert len(get_file_tags(conn, "foo.pdf")) == 1
```


# Database Schema

A tag database has these tables:

1. The `file` table stores all the things being tagged. The table is called `file` for simplicity, but it may contain embedded data or links outside the local filesystem (e.g. HTTP, Git, S3 links).
2. The `tag` table stores tags. Tags have a unique id besides their name, but their name must also be unique.
3. The `file_tag` table stores relations between files and tags. Relations can include a value, so this is a little more simple than a pure join table.
4. The `config` table holds configuration information for later clients.

![entity relationship diagram](assets/tag_db_schema.png)


# Development

This section is for folks wanting to make changes to `tag-utility` itself.

Dependencies:

* Python 3.8+
* Poetry (tested with v1.0.5)
* Git (tested with v2.25.1)

First, clone the repository and install dependencies:

``` bash
git clone https://github.com/luketurner/tag-utility.git

cd tag-utility

poetry install
```

Then, you should be able to run `tag --help` using:

``` bash
poetry run tag --help
```

`tag` roughly hews to a test-driven development style. The test suite is run with:

``` bash
poetry run pytest
```

When new features or bugfixes are contributed, the changes must have accompanying acceptance tests if possible.

Code formatting is provided by `black`:

``` bash
poetry run black tag
poetry run black tests
```
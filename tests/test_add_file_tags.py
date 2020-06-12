import os.path
import pony.orm as orm

import tag

from .util import *

def test_add_filetags_should_create_new_file(conn, tmpfile):
    filetags = tag.add_filetags(conn, tmpfile)
    assert filetags == []
    assert orm.count(x for x in conn.File) == 1


def test_add_filetags_shouldnt_recreate_existing_file(conn, tmpfile):
    tag.add_filetags(conn, tmpfile)
    tag.add_filetags(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 1


def test_add_filetags_shouldnt_recreate_existing_file_when_tags_change(conn, tmpfile):
    tag.add_filetags(conn, tmpfile)
    tag.add_filetags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.File) == 1


def test_add_filetags_should_create_new_tags(conn, tmpfile):
    filetags = tag.add_filetags(conn, tmpfile, {"testtag": None})
    assert filetags[0].tag.name == "testtag"
    assert orm.count(x for x in conn.File) == 1
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 1


def test_add_filetags_shouldnt_recreate_existing_tags(conn, tmpfile):
    filetags = tag.add_filetags(conn, tmpfile, {"testtag": None})
    filetags = tag.add_filetags(conn, tmpfile, {"testtag": "asdf"})
    assert filetags[0].tag.name == "testtag"
    assert orm.count(x for x in conn.Tag) == 1


def test_add_filetags_should_create_missing_filetags(conn, tmpfile):
    tag.add_filetags(conn, tmpfile)
    tag.add_filetags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag" and x.value == "testval") == 1

def test_add_filetags_should_update_existing_filetags(conn, tmpfile):
    tag.add_filetags(conn, tmpfile, {"testtag": None})
    tag.add_filetags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag") == 1
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag" and x.value == "testval") == 1

def test_add_filetags_should_allow_updating_multiple_tags(conn, tmpfile):
    tag.add_filetags(conn, tmpfile, {"testtag": "testval", "testtag2": "testval2"})
    tag.add_filetags(conn, tmpfile, {"testtag": None, "testtag3": "testval3"})
    assert orm.count(x for x in conn.File) == 1
    assert orm.count(x for x in conn.FileTag) == 3
    assert orm.count(x for x in conn.Tag) == 3
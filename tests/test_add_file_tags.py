import os.path
import pony.orm as orm

import tag

from .util import *

def test_add_file_tags_should_create_new_file(conn, tmpfile):
    file_tags = tag.add_file_tags(conn, tmpfile)
    assert file_tags == []
    assert orm.count(x for x in conn.File) == 1


def test_add_file_tags_shouldnt_recreate_existing_file(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile)
    tag.add_file_tags(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 1


def test_add_file_tags_shouldnt_recreate_existing_file_when_tags_change(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile)
    tag.add_file_tags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.File) == 1


def test_add_file_tags_should_create_new_tags(conn, tmpfile):
    file_tags = tag.add_file_tags(conn, tmpfile, {"testtag": None})
    assert file_tags[0].tag.name == "testtag"
    assert orm.count(x for x in conn.File) == 1
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 1


def test_add_file_tags_shouldnt_recreate_existing_tags(conn, tmpfile):
    file_tags = tag.add_file_tags(conn, tmpfile, {"testtag": None})
    file_tags = tag.add_file_tags(conn, tmpfile, {"testtag": "asdf"})
    assert file_tags[0].tag.name == "testtag"
    assert orm.count(x for x in conn.Tag) == 1


def test_add_file_tags_should_create_missing_file_tags(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile)
    tag.add_file_tags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag" and x.value == "testval") == 1

def test_add_file_tags_should_update_existing_file_tags(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile, {"testtag": None})
    tag.add_file_tags(conn, tmpfile, {"testtag": "testval"})
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag") == 1
    assert orm.count(x for x in conn.FileTag if x.tag.name == "testtag" and x.value == "testval") == 1

def test_add_file_tags_should_allow_updating_multiple_tags(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile, {"testtag": "testval", "testtag2": "testval2"})
    tag.add_file_tags(conn, tmpfile, {"testtag": None, "testtag3": "testval3"})
    assert orm.count(x for x in conn.File) == 1
    assert orm.count(x for x in conn.FileTag) == 3
    assert orm.count(x for x in conn.Tag) == 3
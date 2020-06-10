import os.path
import pony.orm as orm

import tag

from .util import *

def test_delete_file_should_delete_file_from_db(conn, tmpfile, sample_file_tag):
    assert orm.count(x for x in conn.File) > 0
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 0

def test_delete_file_should_delete_filetags_from_db(conn, tmpfile, sample_file_tag):
    assert orm.count(x for x in conn.FileTag) > 0
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.FileTag) == 0


def test_delete_file_shouldnt_delete_tags_from_db(conn, tmpfile, sample_file_tag):
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.Tag) == 1


def test_delete_file_should_do_nothing_if_file_doesnt_exist_in_db(conn, tmpfile):
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 0
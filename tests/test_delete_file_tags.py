import os.path
import pony.orm as orm

import tag

from .util import *

def test_delete_filetags_should_delete_filetags_from_db(conn, tmpfile, sample_filetag):
    assert orm.count(x for x in conn.FileTag) > 0
    tag.delete_filetags(conn, tmpfile, ["testtag"])
    assert orm.count(x for x in conn.FileTag) == 0

def test_delete_filetags_shouldnt_delete_files_from_db(conn, tmpfile, sample_filetag):
    tag.delete_filetags(conn, tmpfile, ["testtag"])
    assert orm.count(x for x in conn.File) == 1

def test_delete_filetags_shouldnt_delete_tags_from_db(conn, tmpfile, sample_filetag):
    tag.delete_filetags(conn, tmpfile, ["testtag"])
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 1

def test_delete_filetags_should_ignore_filetags_not_in_db(conn, tmpfile, sample_filetag):
    tag.delete_filetags(conn, tmpfile, ["testtag", "testwrongtag"])
    assert orm.count(x for x in conn.FileTag) == 0
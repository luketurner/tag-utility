import os.path
import pony.orm as orm

import tag

from .util import *

def test_delete_tag_should_delete_tags_from_db(conn, tmpfile, sample_filetag):
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 1
    tag.delete_tag(conn, "testtag")
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 0

def test_delete_tag_should_ignore_tags_not_in_db(conn, tmpfile, sample_filetag):
    tag.delete_tag(conn, "testwrongtag")
    assert orm.count(x for x in conn.Tag) > 0

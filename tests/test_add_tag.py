import os.path
import pony.orm as orm

import tag

from .util import *

def test_add_tag_should_create_new_tag(conn):
    t1 = tag.add_tag(conn, "test-tag")
    assert t1.id
    assert orm.count(x for x in conn.Tag) == 1


def test_add_tag_should_update_existing_tag_with_same_name(conn):
    t1 = tag.add_tag(conn, "test-tag")
    t2 = tag.add_tag(conn, "test-tag")
    assert t1.id == t2.id
    assert orm.count(x for x in conn.Tag) == 1


def test_add_tag_should_not_update_existing_tag_if_name_different(conn):
    t1 = tag.add_tag(conn, "test-tag")
    t2 = tag.add_tag(conn, "test-tag2")
    assert t1.id != t2.id
    assert orm.count(x for x in conn.Tag) == 2

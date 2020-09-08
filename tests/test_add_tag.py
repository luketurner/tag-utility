import os.path
import pony.orm as orm

import tag

from .util import *

def test_add_tag_should_create_new_tag(tmpdb):
    tag.add_tag("test-tag")
    assert tag.count_tags() == 1


def test_add_tag_should_update_existing_tag_with_same_name(tmpdb):
    tag.add_tag("test-tag")
    tag.add_tag("test-tag")
    assert tag.count_tags() == 1


def test_add_tag_should_not_update_existing_tag_if_name_different(tmpdb):
    tag.add_tag("test-tag")
    tag.add_tag("test-tag2")
    assert tag.count_tags() == 2

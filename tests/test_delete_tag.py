import os.path

import tag

from .util import *


def test_delete_tag_should_delete_tags_from_db(sample_filetag):
    assert tag.count_tags() == 1
    tag.delete_tag("testtag")
    assert tag.count_tags() == 0


def test_delete_tag_should_delete_filetags_from_db(sample_filetag):
    assert tag.count_filetags() == 1
    tag.delete_tag("testtag")
    assert tag.count_filetags() == 0


def test_delete_tag_should_ignore_tags_not_in_db(sample_filetag):
    tag.delete_tag("testwrongtag")
    assert tag.count_tags() == 1

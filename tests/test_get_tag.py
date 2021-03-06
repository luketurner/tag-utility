import os.path

import tag

from .util import *


def test_get_tag_should_return_tag(sample_filetag):
    t = tag.get_tag("testtag")
    assert t["name"] == "testtag"


def test_get_tag_should_return_None_for_missing_tags(sample_filetag):
    t = tag.get_tag("wrongtag")
    assert t is None

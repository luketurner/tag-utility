import os.path
import pony.orm as orm

import tag

from .util import *

def test_add_filetags_should_create_new_file(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": None})
    assert tag.count_files() == 1


def test_add_filetags_shouldnt_recreate_existing_file(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": None})
    tag.add_filetags(tmpfile, {"testtag": None})
    assert tag.count_files() == 1


def test_add_filetags_shouldnt_recreate_existing_file_when_tags_change(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": None})
    tag.add_filetags(tmpfile, {"testtag2": "testval"})
    assert tag.count_files() == 1


def test_add_filetags_should_create_new_tags(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": None})
    assert tag.count_tags() == 1


def test_add_filetags_shouldnt_recreate_existing_tags(tmpdb, tmpfile):
    tag.add_tag(name="testtag", description="foo")
    tag.add_filetags(tmpfile, {"testtag": "asdf"})
    assert tag.count_tags() == 1
    assert tag.get_tag("testtag")["description"] == "foo"


def test_add_filetags_should_create_missing_filetags(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": "testval"})
    assert tag.count_filetags() == 1

def test_add_filetags_should_update_existing_filetags(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": None})
    tag.add_filetags(tmpfile, {"testtag": "testval"})
    assert tag.count_filetags() == 1
    assert tag.get_filetag(tmpfile, "testtag")["value"] == "testval"

def test_add_filetags_should_allow_updating_multiple_tags(tmpdb, tmpfile):
    tag.add_filetags(tmpfile, {"testtag": "testval", "testtag2": "testval2"})
    tag.add_filetags(tmpfile, {"testtag": None, "testtag3": "testval3"})
    assert tag.count_files() == 1
    assert tag.count_tags() == 3
    assert tag.count_filetags() == 3
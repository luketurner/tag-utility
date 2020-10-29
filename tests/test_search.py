import os.path
import pony.orm as orm

import tag

from .util import *


def test_search_with_no_criteria_should_return_all_filetags(
    tmpdb, tmpfile, sample_filetag
):
    files = list(tag.search_filetags())
    assert len(files) == 1


def test_search_should_return_filetags_matching_tags(
    tmpdb, tmpfile, sample_filetag
):
    files = list(tag.search_filetags(tags=["testtag"]))
    assert len(files) == 1


def test_search_should_not_return_files_without_matching_tags(
    tmpdb, tmpfile, sample_filetag
):
    files = list(tag.search_filetags(tags=["badtag"]))
    assert len(files) == 0


def test_search_should_exclude_tags_based_on_exclude_tags(
    tmpdb, tmpfile, sample_filetag
):
    files = list(tag.search_filetags(exclude_tags=["testtag"]))
    assert len(files) == 0
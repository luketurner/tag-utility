import os.path

import tag

from .util import *


def test_search_with_no_criteria_should_return_all_filetags(sample_filetag):
    files = list(tag.search_files())
    assert len(files) == 1


def test_search_should_return_files_matching_tags(sample_filetag):
    files = list(tag.search_files(tags=["testtag"]))
    assert len(files) == 1


def test_search_should_not_return_files_with_partial_tag_matches(sample_filetag):
    files = list(tag.search_files(tags=["testtag", "othertag"]))
    assert len(files) == 0


def test_search_should_not_return_files_without_matching_tags(sample_filetag):
    files = list(tag.search_files(tags=["badtag"]))
    assert len(files) == 0


def test_search_should_exclude_tags_based_on_exclude_tags(sample_filetag):
    files = list(tag.search_files(exclude_tags=["testtag"]))
    assert len(files) == 0


def test_search_should_return_filetags_matching_any_mime_types(sample_filetag):
    files = list(tag.search_files(mime_types=["text/plain", "foo/bar"]))
    assert len(files) == 1


def test_search_should_exclude_filetags_with_exclude_mime_types(sample_filetag):
    files = list(tag.search_files(exclude_mime_types=["text/plain"]))
    assert len(files) == 0


def test_search_should_match_files_with_no_tags(sample_file):
    files = list(tag.search_files())
    assert len(files) == 1

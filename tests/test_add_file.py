import os.path
import pony.orm as orm

import tag

from .util import *


def test_add_file_should_create_new_file(conn, tmpfile):
    file = tag.add_file(conn, tmpfile)
    assert file.id
    assert orm.count(x for x in conn.File) == 1


def test_add_file_should_update_existing_file(conn, tmpfile):
    file1 = tag.add_file(conn, tmpfile)
    file2 = tag.add_file(conn, tmpfile)
    assert file1.id == file2.id
    assert orm.count(x for x in conn.File) == 1


def test_add_file_should_not_update_existing_file_if_filename_different(conn, tmpfiles):
    files = [tag.add_file(conn, x) for x in tmpfiles]
    assert files[0].id != files[1].id
    assert orm.count(x for x in conn.File) == len(tmpfiles)


def test_add_file_should_escape_uri_values(conn, tmpdir):
    filename = touch(os.path.join(tmpdir, "test\\file name"))
    f = tag.add_file(conn, filename)
    assert "test%5Cfile%20name" in f.uri
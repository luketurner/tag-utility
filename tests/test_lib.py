import os.path
import pytest
import tag
import pony.orm as orm


@pytest.fixture
def conn(tmpdir):
    with tag.connect(os.path.join(tmpdir, "testdb.sqlite")) as c:
        yield c


@pytest.fixture
def tmpfile(tmpdir):
    filename = os.path.join(tmpdir, "test-filename")
    with open(filename, "w") as f:
        f.write("test-content")
    yield filename


def test_creating_new_db_should_succeed(conn):
    assert conn


def test_add_file_should_create_new_file(conn, tmpfile):
    file = tag.add_file(conn, tmpfile)
    assert file.id
    assert orm.count(x for x in conn.File) == 1


def test_add_file_should_update_existing_file(conn, tmpfile):
    file1 = tag.add_file(conn, tmpfile)
    file2 = tag.add_file(conn, tmpfile)
    assert file1.id == file2.id
    assert orm.count(x for x in conn.File) == 1


def test_add_file_should_not_update_existing_file_if_filename_different(conn, tmpfile):
    file1 = tag.add_file(conn, tmpfile)
    file2 = tag.add_file(conn, tmpfile + "other")
    assert file1.id != file2.id
    assert orm.count(x for x in conn.File) == 2


def test_add_file_should_escape_uri_values(conn, tmpdir):
    filename = os.path.join(tmpdir, "test\\file name")
    with open(filename, "w") as file:
        file.write("test-content")
    f = tag.add_file(conn, filename)
    assert "test%5Cfile%20name" in f.uri


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


def test_add_file_tag_should_create_new_file(conn, tmpfile):
    file_tags = tag.add_file_tags(conn, tmpfile)
    assert file_tags == []
    assert orm.count(x for x in conn.File) == 1


def test_add_file_tags_should_create_new_tags(conn, tmpfile):
    file_tags = tag.add_file_tags(conn, tmpfile, {"testtag": None})
    assert file_tags[0].tag.name == "testtag"
    assert orm.count(x for x in conn.File) == 1
    assert orm.count(x for x in conn.Tag if x.name == "testtag") == 1


def test_delete_file_should_delete_file_from_db(conn, tmpfile):
    tag.add_file(conn, tmpfile)
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 0


def test_delete_file_should_do_nothing_if_file_doesnt_exist_in_db(conn, tmpfile):
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.File) == 0


def test_delete_file_should_delete_file_tags_from_db(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile, {"test-tag": "test-value"})
    assert orm.count(x for x in conn.FileTag) == 1
    tag.delete_file(conn, tmpfile)
    assert orm.count(x for x in conn.FileTag) == 0


def test_delete_tag_should_delete_file_tags_from_db(conn, tmpfile):
    tag.add_file_tags(conn, tmpfile, {"test-tag": "test-value"})
    assert orm.count(x for x in conn.FileTag) == 1
    tag.delete_tag(conn, "test-tag")
    assert orm.count(x for x in conn.FileTag) == 0

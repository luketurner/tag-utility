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
  with open(filename, 'w') as f:
    f.write("test-content")
  yield filename

def test_creating_new_db_should_succeed(conn):
  assert conn

def test_insert_file_should_succeed(conn):
  f = tag.insert(conn, conn.File, uri="file://test", name="test-name")
  assert f.id
  assert f.name == "test-name"

def test_upsert_file_should_update_existing_by_id(conn):
  f = tag.upsert(conn, conn.File, uri="file://test", name="test-name")
  assert f.id
  assert f.name == "test-name"
  f2 = tag.upsert(conn, conn.File, id=f.id, uri="file://test2", name="test-name2")
  assert f2.id == f.id
  assert f2.uri == "file://test2"
  assert f.uri == "file://test2"

def test_upsert_file_should_update_existing_by_uri(conn):
  f = tag.upsert(conn, conn.File, uri="file://test", name="test-name")
  assert f.id
  assert f.name == "test-name"
  f2 = tag.upsert(conn, conn.File, uri="file://test", name="test-name2")
  assert f2.id == f.id
  assert f2.name == "test-name2"
  assert f.name == "test-name2"

def test_upsert_tag_should_update_existing_by_id(conn):
  tag1 = tag.upsert(conn, conn.Tag, name="test-tag", description="test-desc")
  assert tag1.id
  assert tag1.name == "test-tag"
  tag2 = tag.upsert(conn, conn.Tag, id=tag1.id, name="test-tag2", description="test-desc2")
  assert tag2.id == tag1.id
  assert tag1.name == "test-tag2"
  assert tag2.name == "test-tag2"

def test_ingest_file_should_create_file_if_missing(conn, tmpfile):
  f = tag.ingest_file(conn, tmpfile)
  assert f.id

def test_ingest_file_should_return_file_if_existing(conn, tmpfile):
  f = tag.ingest_file(conn, tmpfile)
  f2 = tag.ingest_file(conn, tmpfile)
  assert f.id == f2.id

def test_ingest_file_should_create_tags_if_missing(conn, tmpfile):
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value" })
  tags = list(orm.select(x for x in conn.Tag))
  assert len(tags) == 2

def test_ingest_file_should_not_create_tags_if_existing(conn, tmpfile):
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value" })
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value2" })
  tags = list(orm.select(x for x in conn.Tag))
  assert len(tags) == 2

def test_ingest_file_should_create_file_tags_if_missing(conn, tmpfile):
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value" })
  file_tags = list(orm.select(x for x in conn.FileTag))
  assert len(file_tags) == 2

def test_ingest_file_should_not_create_file_tags_if_existing(conn, tmpfile):
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value" })
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value2" })
  file_tags = list(orm.select(x for x in conn.FileTag))
  assert len(file_tags) == 2

def test_ingest_file_should_update_file_tags_if_existing_and_changed(conn, tmpfile):
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value" })
  tag.ingest_file(conn, tmpfile, { "test-tag": None, "test-tag2": "test-value2" })
  file_tag = orm.select(x for x in conn.FileTag if x.tag.name == "test-tag2").first()
  assert file_tag.value == 'test-value2'
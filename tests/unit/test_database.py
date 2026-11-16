"""Unit tests for SQLite database connectivity and scoped sessions."""

from oqteris.database.connection import DatabaseManager
from oqteris.models.entities import RecentFile


def test_database_schema_initialization(test_db: DatabaseManager):
    assert test_db.engine is not None

    with test_db.session_scope() as session:
        # Create a sample entity
        rec = RecentFile(
            file_path="C:/sample.pdf",
            file_name="sample.pdf",
            file_size_bytes=1024,
            page_count=5,
        )
        session.add(rec)

    with test_db.session_scope() as session:
        fetched = session.query(RecentFile).filter_by(file_name="sample.pdf").first()
        assert fetched is not None
        assert fetched.page_count == 5

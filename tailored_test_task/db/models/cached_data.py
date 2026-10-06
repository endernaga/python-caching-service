from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from tailored_test_task.db.base import Base


class CachedStringData(Base):
    """Model for caching string data."""

    __tablename__ = "cached_string_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    input_string = Column(String, nullable=False, index=True, unique=True)
    output_string = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"<CachedStringData(id={self.id}, "
            f"input_string={self.input_string}, "
            f"output_string={self.output_string}, "
            f"created_at={self.created_at})>"
        )


class CachedListData(Base):
    """Model for caching list data."""

    __tablename__ = "cached_list_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    input_hash = Column(String, nullable=False, index=True, unique=True)
    output_string = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"<CachedListData(id={self.id}, "
            f"input_hash={self.input_hash}, "
            f"output_string={self.output_string}, "
            f"created_at={self.created_at})>"
        )

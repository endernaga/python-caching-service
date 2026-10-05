from sqlalchemy.orm import DeclarativeBase

from tailored_test_task.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta

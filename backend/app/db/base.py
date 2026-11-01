from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM metadata. Apply versioned SQL migrations instead of create_all."""

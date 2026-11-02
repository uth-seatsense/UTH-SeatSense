from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM metadata; apply versioned SQL migrations instead of create_all."""

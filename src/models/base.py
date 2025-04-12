from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    """Base model for all database models."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls, data):
        """Create model instance from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__table__.columns.keys()})
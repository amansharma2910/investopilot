from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    openai_key = Column(String, nullable=True)
    stocks = Column(ARRAY(String), nullable=True)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String)
    embedding = Column(ARRAY(Float))
    document_metadata = Column(JSON)  # Changed from 'metadata' to 'document_metadata'
    user_id = Column(String)

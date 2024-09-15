from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    openai_key = Column(String, nullable=True)
    stocks = Column(ARRAY(String), nullable=True)

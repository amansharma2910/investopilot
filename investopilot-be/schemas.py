from typing import Union, List, Dict

from pydantic import BaseModel, UUID4


class User(BaseModel):
    id: str
    openai_key: str
    stocks: Union[str, list[str]]

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    content: str
    embedding: List[float]
    document_metadata: Dict[str, str]  # Changed from 'metadata' to 'document_metadata'
    user_id: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: UUID4

    class Config:
        orm_mode = True
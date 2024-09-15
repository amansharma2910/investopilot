from typing import Union

from pydantic import BaseModel


class User(BaseModel):
    id: int
    openai_key: str
    stocks: Union[str, list[str]]

    class Config:
        orm_mode = True
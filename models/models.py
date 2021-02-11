from pydantic import BaseModel
from typing import Optional

class Meme(BaseModel):
    id: int
    name: str
    caption: str
    url : str

class MemeIn(BaseModel):
    name: str
    caption: str
    url : str

class MemeBody(BaseModel):
    caption : Optional[str]
    url : Optional[str]

from pydantic import BaseModel
from typing import Optional
from .metadata import Metadata
from .common import Id

class Organization(BaseModel):
    id: Optional[Id]
    name: Optional[str]

class _Organization(BaseModel):
    id: Id
    name: str

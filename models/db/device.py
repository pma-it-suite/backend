from pydantic import BaseModel
from typing import Optional
from .metadata import Metadata
from .common import Id

class Device(BaseModel):
    _id: Optional[Id]
    name: Optional[str]
    user_id: Optional[Id]
    metadata: Optional[Metadata]

class _Device(BaseModel):
    _id: Id
    name: str
    user_id: Id
    metadata: Optional[Metadata]

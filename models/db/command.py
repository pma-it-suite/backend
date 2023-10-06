from pydantic import BaseModel
from typing import Optional, Any
from .common import Id

class Command(BaseModel):
    id: Optional[Id]
    status: str
    args: Any
    name: str
    issuer_id: Id

class _Command(BaseModel):
    id: Id
    status: str
    args: Any
    name: str
    issuer_id: Id

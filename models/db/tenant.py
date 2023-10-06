from pydantic import BaseModel
from typing import Optional
from .metadata import Metadata
from .common import Id

class Tenant(BaseModel):
    id: Optional[Id]
    organization_id: Optional[Id]
    name: Optional[str]

class _Tenant(BaseModel):
    id: Id
    organization_id: Id
    name: str

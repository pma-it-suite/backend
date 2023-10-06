from pydantic import BaseModel
from typing import Optional
from .metadata import Metadata
from .common import Id

class Subscription(BaseModel):
    id: Optional[Id]
    tenant_id: Optional[Id]
    name: Optional[str]

class _Subscription(BaseModel):
    id: Id
    tenant_id: Id
    name: str

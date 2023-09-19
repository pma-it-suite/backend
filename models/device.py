from pydantic import BaseModel
from .common import Id
from typing import Optional


class Device(BaseModel):
    _id: Id
    name: str
    user_id: Id
    metadata: Optional[Metadata]

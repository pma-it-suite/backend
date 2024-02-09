from .common import Id, BaseModelWithId
from .metadata import Metadata
from typing import Optional


class Device(BaseModelWithId):
    name: str
    user_id: Id
    metadata: Optional[Metadata] = {}

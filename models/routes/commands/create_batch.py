from typing import Optional
from models.db.common import BaseModelWithConfig, Id
from models.db.command import CommandNames


class CreateBatchRequest(BaseModelWithConfig):
    device_ids: list[Id]
    name: CommandNames
    args: Optional[str] = None
    issuer_id: Id


class CreateBatchResponse(BaseModelWithConfig):
    command_ids: list[Id]

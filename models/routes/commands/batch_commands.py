from pydantic import BaseModel
from models.db.common import Id, BaseModelWithConfig, BaseModelWithId
from models.db.command import CommandNames
from typing import Optional


class BatchCommandsRequest(BaseModelWithId):
    name: CommandNames
    args: Optional[str]
    issuer_id: Id


class BatchCommandsResponse(BaseModelWithConfig):
    command_ids: list[Id]

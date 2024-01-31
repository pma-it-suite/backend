from pydantic import BaseModel
from models.db.common import Id, BaseModelWithConfig, BaseModelWithId
from models.db.command import CommandNames


class BatchCommandsRequest(BaseModelWithId):
    name: CommandNames
    args: Optional[str]
    issuer_id: Id


class BatchCommandsRequest(BaseModelWithConfig):
    command_ids: list[Id]

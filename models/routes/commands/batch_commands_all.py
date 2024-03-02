from models.db.common import Id, BaseModelWithConfig
from models.db.command import Command


class BatchAllCommandsResponse(BaseModelWithConfig):
    commands: list[Command]

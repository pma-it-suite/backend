from models.db.command import CommandStatus
from models.db.common import BaseModelWithConfig, Id


class CommandStatusRequest(BaseModelWithConfig):
    command_id: Id
    status: CommandStatus

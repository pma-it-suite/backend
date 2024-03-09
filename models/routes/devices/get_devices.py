from models.db.common import BaseModelWithConfig, Id
from models.db.device import Device


class GetDevicesResponse(BaseModelWithConfig):
    devices: list[Device]

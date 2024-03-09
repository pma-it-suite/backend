from models.db.common import BaseModelWithConfig, Id
from models.db.device import Device


class GetDeviceResponse(BaseModelWithConfig):
    device: Device

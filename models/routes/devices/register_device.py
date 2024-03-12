from typing import Optional
from models.db.common import BaseModelWithConfig, Id


class RegisterDeviceRequest(BaseModelWithConfig):
    device_name: str
    user_id: Id
    issuer_id: Id
    user_secret: str


class RegisterDeviceResponse(BaseModelWithConfig):
    device_id: Id

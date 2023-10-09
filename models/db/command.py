from .common import Id, BaseModelWithId


class Command(BaseModelWithId):
    status: str
    args: str
    name: str
    issuer_id: Id

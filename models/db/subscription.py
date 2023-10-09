from .common import Id


class Subscription(BaseModelWithId):
    tenant_id: Id
    name: str

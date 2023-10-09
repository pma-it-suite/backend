from .common import Id, BaseModelWithId


class Tenant(BaseModelWithId):
    organization_id: Id
    name: str

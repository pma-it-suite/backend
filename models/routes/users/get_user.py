from pydantic import BaseModel
from models.db.user import DbUser


class GetUserResponse(DbUser):
    pass

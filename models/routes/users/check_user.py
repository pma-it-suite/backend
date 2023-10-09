from pydantic import BaseModel
from models.db.user import DbUser


class CheckUserResponse(DbUser):
    pass

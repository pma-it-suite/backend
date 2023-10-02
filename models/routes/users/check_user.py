from pydantic import BaseModel
from models.db.user import Users


class CheckUserResponse(Users):
    pass

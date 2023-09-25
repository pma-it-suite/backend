from pydantic import BaseModel
from models.db.user import Users


class GetUserResponse(Users):
    pass

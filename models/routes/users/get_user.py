from pydantic import BaseModel
from models.db.user import DbUserRedacted


class GetUserResponse(DbUserRedacted):
    pass

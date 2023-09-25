from fastapi import APIRouter
from config.db import get_database
from config.main import DB_NAME, USERS_COLLECTION_NAME
from bson.objectid import ObjectId
import docs.get_user as docs
import models.routes.users.get_user as models
from models.db.common import Id
import random
from utils.errors import DefaultDataNotFoundException, InvalidDataException

router = APIRouter()
ROUTE_BASE = "/users"
TAG = "users"

# Initialize MongoDB client
client = get_database()
db = client[DB_NAME]
users_collection = db[USERS_COLLECTION_NAME]


@router.get(ROUTE_BASE + '/',
            response_model=models.GetUserResponse,
            description=docs.Desc,
            summary=docs.Summary,
            tags=[TAG],
            status_code=200)
def get_user(user_id: Id):
    """
    Get user by id
    """
    if user_id is None:
        msg = f"invalid request - user id must be set"
        return InvalidDataException(detail=msg)

    user = users_collection.find_one({"_id": user_id})

    if user:
        return models.GetUserResponse(**user)
    else:
        return DefaultDataNotFoundException(detail=msg)

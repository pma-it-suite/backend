from fastapi import APIRouter
from config.db import get_database
from config.main import DB_NAME, USERS_COLLECTION_NAME
from bson.objectid import ObjectId
import models.routes.users as models
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
            response_model=models.get_user.GetUserResponse,
            summary="Get user by id",
            tags=[TAG],
            status_code=200)
def get_user(user_id: Id):
    _validate_user_id_or_throw(user_id)

    user = users_collection.find_one({"_id": user_id})

    if user:
        return models.get_user.GetUserResponse(**user)
    else:
        msg = f"no user found with user id: {user_id}"
        raise DefaultDataNotFoundException(detail=msg)


@router.get(ROUTE_BASE + '/check',
            response_model=models.CheckUserResponse,
            summary="Check user by user_id",
            tags=[TAG],
            status_code=200)
def check_username(user_id: Id):
    _validate_user_id_or_throw(user_id)

    user = users_collection.find_one({"_id": user_id})

    if user:
        return models.get_user.GetUserResponse(**user)
    else:
        msg = f"no user found with user id: {user_id}"
        raise DefaultDataNotFoundException(detail=msg)


def _validate_user_id_or_throw(user_id: Id):
    if not user_id:
        msg = f"invalid request - user id must be set"
        raise InvalidDataException(detail=msg)

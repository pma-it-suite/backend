from fastapi import APIRouter
from config.db import get_users_collection
from bson.objectid import ObjectId
import models.routes.users as models
from models.db.common import Id, EmailStr, RaisesException
from models.db.user import DbUser, RawUser
from utils.errors import (
    DefaultDataNotFoundException,
    InvalidDataException,
    InvalidPasswordException,
)
from utils.users import validate_user_id_or_throw, get_db_user_or_throw_if_404, register_user_to_db
from utils.auth import get_auth_token_from_user_id, hash_and_compare
import utils.errors as exceptions

router = APIRouter()
ROUTE_BASE = "/users"
TAG = "users"

# Initialize MongoDB client
users_collection = get_users_collection()


@router.get(
    ROUTE_BASE + "/get",
    response_model=models.get_user.GetUserResponse,
    summary="Get user by id",
    tags=[TAG],
    status_code=200,
)
async def get_user(user_id: Id):
    validate_user_id_or_throw(user_id)

    user = get_db_user_or_throw_if_404(user_id)
    return models.get_user.GetUserResponse(**user.dict())


@router.post(
    ROUTE_BASE + "/register",
    response_model=models.RegisterUserResponse,
    summary="Register user",
    tags=[TAG],
    status_code=201,
)
async def register_user(user_register_form: models.RegisterUserRequest):
    user_id = register_user_to_db(user_register_form)

    auth_token_str = await get_auth_token_from_user_id(user_id)
    return models.RegisterUserResponse(**{
        "user_id": user_id,
        "jwt": auth_token_str
    })


@router.post(
    ROUTE_BASE + "/login",
    response_model=models.LoginUserResponse,
    summary="Login user",
    tags=[TAG],
    status_code=200,
)
async def login_user(login_form: models.LoginUserRequest):
    user_id = login_form.user_id
    validate_user_id_or_throw(user_id)

    user = get_db_user_or_throw_if_404(user_id)
    if hash_and_compare(login_form.password, user.password_hash):
        auth_token_str = await get_auth_token_from_user_id(user_id)
        return models.LoginUserResponse(jwt=auth_token_str)
    else:
        msg = f"invalid password for user_id: {user_id}"
        raise InvalidPasswordException(detail=msg)

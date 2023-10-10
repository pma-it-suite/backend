from fastapi import APIRouter
from config.db import get_users_collection
from bson.objectid import ObjectId
from typing import Optional
import models.routes.users as models
from models.db.common import Id, EmailStr, RaisesException
from models.db.user import DbUser, RawUser
from utils.errors import (
    DefaultDataNotFoundException,
    InvalidDataException,
    InvalidPasswordException,
)
from utils.users import validate_user_id_or_throw, get_db_user_or_throw_if_404, register_user_to_db
import utils.errors as exceptions
import logging

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

    return models.RegisterUserResponse(**{"user_id": user_id})


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
    if login_form.password_hash == user.password_hash:
        return models.LoginUserResponse()
    else:
        msg = f"invalid password for user_id: {user_id}"
        raise InvalidPasswordException(detail=msg)

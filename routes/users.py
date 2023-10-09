from fastapi import APIRouter
from config.db import get_users_collection
from bson.objectid import ObjectId
from typing import Optional
import models.routes.users as models
from models.db.common import Id, EmailStr, RaisesException
from models.db.user import DbUser, RawUser
from utils.errors import DefaultDataNotFoundException, InvalidDataException, InvalidPasswordException
from utils.users import validate_user_id_or_throw, get_db_user_or_throw_if_404
import utils.errors as exceptions
import bcrypt
import uuid
import pymongo.errors as pymongo_exceptions
import pymongo.results as pymongo_results
import logging

router = APIRouter()
ROUTE_BASE = "/users"
TAG = "users"

# Initialize MongoDB client
users_collection = get_users_collection()


@router.get(ROUTE_BASE + '/get',
            response_model=models.get_user.GetUserResponse,
            summary="Get user by id",
            tags=[TAG],
            status_code=200)
def get_user(user_id: Id):
    validate_user_id_or_throw(user_id)

    user = get_db_user_or_throw_if_404(user_id)
    return models.get_user.GetUserResponse(**user.dict())


@router.post(ROUTE_BASE + '/register',
             response_model=models.RegisterUserResponse,
             summary="Register user",
             tags=[TAG],
             status_code=201)
def register_user(user_register_form: models.RegisterUserRequest):
    encoded_new_pass = user_register_form.raw_password.encode('utf-8')
    password_hash = str(bcrypt.hashpw(encoded_new_pass, bcrypt.gensalt()))

    encoded_secret = (password_hash + user_register_form.email).encode('utf-8')
    user_secret_hash = str(bcrypt.hashpw(encoded_secret, bcrypt.gensalt()))

    user_id = str(uuid.uuid4())
    db_user_data = DbUser(
        **{
            "_id": user_id,
            "metadata": {},
            "user_secret_hash": user_secret_hash,
            "password_hash": password_hash,
            "device_ids": [],
            **user_register_form.dict()
        }).dict()

    logging.info(f"registering user with: {db_user_data}...")

    try:
        result = users_collection.insert_one(db_user_data)
    except pymongo_exceptions.DuplicateKeyError as dupe_error:
        detail = "Invalid user insertion: duplicate email"
        raise exceptions.DefaultDuplicateDataException(
            detail=detail) from dupe_error
    except Exception as ex:
        detail = "Unknown database error when registering user"
        raise exceptions.DatabaseError(detail=detail) from ex

    return models.RegisterUserResponse(**{"user_id": user_id})


@router.post(ROUTE_BASE + '/login',
             response_model=models.LoginUserResponse,
             summary="Login user",
             tags=[TAG],
             status_code=200)
def login_user(login_form: models.LoginUserRequest):
    user_id = login_form.user_id
    validate_user_id_or_throw(user_id)

    user = get_db_user_or_throw_if_404(user_id)
    if login_form.password_hash == user.password_hash:
        return models.LoginUserResponse()
    else:
        msg = f"invalid password for user_id: {user_id}"
        raise InvalidPasswordException(detail=msg)

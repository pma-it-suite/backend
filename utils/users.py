from typing import Optional
from utils.errors import DefaultDataNotFoundException, InvalidDataException, InvalidPasswordException
from models.db.user import DbUser, RawUser
from models.routes.users.register_user import RegisterUserRequest
from models.db.common import Id, EmailStr, RaisesException
from config.db import get_users_collection
import bcrypt
import pymongo.errors as pymongo_exceptions
import pymongo.results as pymongo_results
from icecream import ic
import utils.errors as exceptions
import logging


def validate_user_id_or_throw(user_id: Id):
    if not user_id:
        msg = f"invalid request - user id must be set"
        raise InvalidDataException(detail=msg)


def get_db_user_or_throw_if_404(
        user_identifier: Id | EmailStr) -> DbUser | RaisesException:
    user = _get_raw_user_or_throw_if_404(user_identifier)
    return DbUser(**user)


def _get_raw_user_from_db(user_identifier: Id | EmailStr) -> Optional[RawUser]:
    users_collection = get_users_collection()
    if "@" in user_identifier:
        filter = {"email": user_identifier}
    else:
        filter = {"_id": user_identifier}
    user = users_collection.find_one(filter)
    return user


def _get_raw_user_or_throw_if_404(
        user_identifier: Id | EmailStr) -> RawUser | RaisesException:
    user_result = _get_raw_user_from_db(user_identifier)
    if user_result is None or not user_result:
        msg = f"no user found with user identifier: {user_identifier}"
        raise DefaultDataNotFoundException(detail=msg)
    return user_result


def register_user_to_db(user_register_form: RegisterUserRequest) -> Id:
    users_collection = get_users_collection()
    encoded_new_pass = user_register_form.raw_password.encode('utf-8')
    password_hash = str(bcrypt.hashpw(encoded_new_pass, bcrypt.gensalt()))

    encoded_secret = (password_hash + user_register_form.email).encode('utf-8')
    user_secret_hash = str(bcrypt.hashpw(encoded_secret, bcrypt.gensalt()))

    db_user = DbUser(
        **{
            "metadata": {},
            "user_secret_hash": user_secret_hash,
            "password_hash": password_hash,
            "device_ids": [],
            **user_register_form.dict()
        })

    db_user_data = db_user.dict()

    logging.info(f"registering user with: {db_user_data}...")

    try:
        result = users_collection.insert_one(db_user_data)
    except pymongo_exceptions.DuplicateKeyError as dupe_error:
        detail = "Invalid user insertion: duplicate email"
        raise exceptions.DefaultDuplicateDataException(
            detail=detail) from dupe_error
    except Exception as ex:
        detail = f"Unknown database error when registering user, {ex}"
        raise exceptions.DatabaseError(detail=detail) from ex

    user_id = str(result.inserted_id)
    return user_id


def check_if_admin_by_id(user_id: Id) -> bool:
    return True

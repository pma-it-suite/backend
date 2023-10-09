from typing import Optional
from utils.errors import DefaultDataNotFoundException, InvalidDataException, InvalidPasswordException
from models.db.user import DbUser, RawUser
from models.db.common import Id, EmailStr, RaisesException


def validate_user_id_or_throw(user_id: Id):
    if not user_id:
        msg = f"invalid request - user id must be set"
        raise InvalidDataException(detail=msg)


def get_db_user_or_throw_if_404(
        user_identifier: Id | EmailStr) -> DbUser | RaisesException:
    user = _get_raw_user_or_throw_if_404(user_identifier)
    return models.get_user.GetUserResponse(**user)


def _get_raw_user_from_db(user_identifier: Id | EmailStr) -> Optional[RawUser]:
    if "@" in user_identifier:
        filter = {"email": user_identifier}
    else:
        filter = {"_id": user_identifier}
    print(filter)
    user = users_collection.find_one(filter)
    print(user)
    return user


def _get_raw_user_or_throw_if_404(
        user_identifier: Id | EmailStr) -> RawUser | RaisesException:
    user_result = _get_raw_user_from_db(user_identifier)
    if user_result == None:
        msg = f"no user found with user identifier: {user_identifier}"
        raise DefaultDataNotFoundException(detail=msg)
    return user_result

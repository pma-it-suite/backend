# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
"""
Holds methods which perform several operations on the
incoming Header string, which is expected to be a JWT.
Additional functionality to validate and decode the
incoming JWT.
"""

from typing import Dict, Any, Optional

from fastapi import Header

from models.db.auth import Token
import utils.errors as exceptions
import utils.users as user_utils
import models.db.common as common_models


async def check_header_token_is_admin(token: str = Header(
        None)) -> common_models.Id:
    """
    Will check for valid token and existing user, as well as
    making sure that the user is an admin.

    Returns 404 if user not found, 401 if other error.
    """
    user_id = await get_user_id_from_header_and_check_existence(token)

    is_admin = await user_utils.check_if_admin_by_id(user_id)
    if is_admin:
        return user_id

    detail = "User is not an authorized administrator"
    raise exceptions.UnauthorizedIdentifierData(detail=detail)


async def get_user_id_from_header_and_check_existence(  # pylint: disable=invalid-name
        token: str = Header(None)) -> common_models.Id:
    """
    Gets the token from the header and treats it as a `Id`,
    checking for existence of the user, else raising a 404.

    If valid and existent, returns the value of the Id.
    """
    payload_dict = await get_payload_from_token_header(token)
    user_id = payload_dict.get("user_id")
    if not user_id:
        detail = "User ID not in JWT header payload dict."
        raise exceptions.InvalidDataException(detail=detail)
    await user_utils.get_db_user_or_throw_if_404(user_id)
    return user_id


async def get_auth_token_from_header(token: str = Header(None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    returning it if available, else raises an authentication error.
    """
    await check_token_data_passed_in(token)
    valid_token = await get_token_from_optional_header(token)
    return valid_token


async def get_token_from_optional_header(token: Optional[str] = Header(
        None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    returning it if available, else returns None
    """
    if token:
        await check_token_str_is_decodable(token)
        return token
    return


async def get_payload_from_token_header(token: str = Header(None)) -> Dict[
        str, Any]:
    """
    Attempts to get the auth token string from the request header,
    and, in the process, decodes the token, returning the payload if valid,
    else raising an authorization exception
    """
    await check_token_data_passed_in(token)
    token_payload = await get_payload_from_optional_token_header(token)
    return token_payload


async def get_payload_from_optional_token_header(  # pylint: disable=invalid-name
        token: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Returns the payload from a valid token header if one is present,
    if not header is passed in, returns None.
    """
    if token:
        await check_token_str_is_decodable(token)
        token_payload = Token.get_dict_from_enc_token_str(token)
        return token_payload


async def get_user_id_from_optional_token_header_check_existence(  # pylint: disable=invalid-name
        token: Optional[str] = Header(None)) -> common_models.Id:
    """
    Returns the user_id from a valid token header if one is
    present and valid, if no header is passed in, returns None.
    """
    if token:
        return await get_user_id_from_header_and_check_existence(token)
    return


async def check_token_data_passed_in(token_str: str) -> None:
    """
    Checks if the token data exists and was passed in.
    If not, raises invalid data exception.
    """
    if not token_str:
        detail = "Missing header token string!"
        raise exceptions.InvalidDataException(detail=detail)


async def check_token_str_is_decodable(token_str: str) -> None:
    """
    Checks if encoded token string passed in is valid
    and decodable.

    If not, raises an authentication error.
    """
    invalid_token_data = not Token.check_if_valid(token_str)
    if invalid_token_data:
        raise exceptions.InvalidAuthHeaderException


async def get_auth_token_from_user_id(user_id: common_models.Id) -> str:
    """
    Returns an encoded token string with the given user_id in it's payload.
    """
    payload_dict = {'user_id': user_id}
    encoded_jwt_str = Token.get_enc_token_str_from_dict(payload_dict)
    return encoded_jwt_str


def hash_and_compare(raw: str, hash_to_compare: str) -> bool:
    encoded = raw.encode('utf-8')
    hash = str(bcrypt.hashpw(encoded, bcrypt.gensalt()))
    return hash == hash_to_compare

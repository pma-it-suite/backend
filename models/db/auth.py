# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=fixme
#       - don't want to break lint but also don't want to create tickets.
#         as soon as this is on the board, remove this disable.
# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
"""
Data Class for JWT Token Operations
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import jwt

from config.main import JWT_SECRET_KEY, JWT_EXPIRY_TIME


class Token:
    """
    Main top-level Token Class. Holds the static methods
    that perform several different operations on tokens
    depending on if it is an encoded string or a payload
    dict.
    """
    @staticmethod
    def get_dict_from_enc_token_str(encoded_token_str: str) -> Dict[Any, Any]:
        """
        Decodes the token string and checks to make sure
        it is both not expired and valid before doing so.
        Returns a dict.
        """
        valid = Token.check_if_valid(encoded_token_str)
        is_expired = Token.check_if_expired(encoded_token_str)
        if valid and not is_expired:
            payload_dict = jwt.decode(encoded_token_str,
                                      JWT_SECRET_KEY,
                                      algorithms=["HS256"])
        else:
            payload_dict = {'Error:', 'not valid'}
        return payload_dict

    @staticmethod
    def get_enc_token_str_from_dict(
            payload_dict: Dict[Any, Any],
            expiry_time: Optional[timedelta] = None) -> str:
        """
        Encodes a payload dict into a token string.
        Allows for an optional expiry date depending on
        User input. Returns an encoded string.
        """

        custom_expiry_time_set = expiry_time is not None

        if custom_expiry_time_set:
            expire = datetime.utcnow() + expiry_time
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_TIME)

        time_payload = {'exp': expire}
        payload_dict.update(time_payload)
        encoded_token_str = jwt.encode(payload_dict,
                                       JWT_SECRET_KEY,
                                       algorithm="HS256")

        # TODO: figure out this bug
        if isinstance(encoded_token_str, str):
            return encoded_token_str
        return encoded_token_str.decode()

    @staticmethod
    def check_if_expired(encoded_token_str: str) -> bool:
        """
        Tries to decode an encoded string
        and checks if it raises the expiry error.
        """
        try:
            jwt.decode(encoded_token_str, JWT_SECRET_KEY, algorithms=["HS256"])
            return False
        except jwt.ExpiredSignatureError:
            return True

    @staticmethod
    def check_if_valid(encoded_token_str: str) -> bool:
        """
        Tries to decode an encoded string
        and checks if it raises any invalid errors.
        """
        try:
            jwt.decode(encoded_token_str, JWT_SECRET_KEY, algorithms=["HS256"])
            return True
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError,
                jwt.exceptions.ExpiredSignatureError):
            return False

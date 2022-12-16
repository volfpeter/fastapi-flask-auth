from typing import Optional, Protocol

from fastapi import HTTPException, Request, status


class Decoder(Protocol):
    """
    Decoder protocol.
    """

    def json(self, cookie: str, /) -> dict:
        """
        Decodes the given cookie.

        Arguments:
            cookie: The cookie value.

        Returns:
            The decoded and validated cookie content.

        Raises:
            Exception: If the cookie is invalid.
        """
        ...


class FlaskSessionAuthenticator:
    """
    Authenticator that decodes and validates Flask session cookies and extracts
    the user ID from the session if it includes one.

    Unless you're dealing with cookies that were produced by a Flask application with
    highly customized session encoding, you can use `FlaskSessionDecoder` from the
    lightweight `flask-session-decoder` library to create a decoder for the authenticator.
    Of course, you can use anything else that satisfies the `Decoder` protocol.
    """

    __slots__ = (
        "_decoder",
        "_error_status_code",
        "_id_field",
        "_session_header",
    )

    # -- Init

    def __init__(
        self,
        *,
        decoder: Decoder,
        error_status_code: int = status.HTTP_401_UNAUTHORIZED,
        id_field="_user_id",
        session_header: str = "session",
    ) -> None:
        """
        Initialization.

        Arguments:
            decoder: The Flask session decoder to use to decode the session cookie.
            error_status_code: The status code to use in raised `HTTPException`s.
                               Default value is `401` (unauthorized).
            id_field: The field that stores the user ID in the session cookie.
            session_header: The name of the session header.
        """
        self._decoder = decoder
        self._error_status_code = error_status_code
        self._id_field = id_field
        self._session_header = session_header

    # -- FastAPI dependencies

    def get_session_cookie(self, request: Request) -> Optional[dict]:
        """
        FastAPI dependency that returns the session cookie from the request if it has one.
        """
        cookie = request.cookies.get(self._session_header)
        if cookie is None:
            return None

        try:
            return self._decoder.json(cookie)
        except Exception:
            return None

    def get_user_id(self, request: Request) -> Optional[str]:
        """
        FastAPI dependency that returns the user ID from the session cookie if it has one.
        """
        cookie = self.get_session_cookie(request)
        return cookie.get(self._id_field) if cookie is not None else None

    def requires_session_cookie(self, request: Request) -> dict:
        """
        FastAPI dependency that returns the session cookie from the request,
        or raises an `HTTPException` if there's no valid session cookie.
        """
        cookie = self.get_session_cookie(request)
        if cookie is None:
            raise HTTPException(
                status_code=self._error_status_code,
                detail="No valid session cookie was found.",
            )

        return cookie

    def requires_user_id(self, request: Request) -> str:
        """
        FastAPI dependency that returns the user ID from the session cookie,
        or raises an `HTTPException` if there's no valid session cookie or
        if it doesn't contain a user ID.
        """
        user_id = self.get_user_id(request)
        if user_id is None:
            raise HTTPException(
                status_code=self._error_status_code,
                detail="User ID was not found.",
            )

        return user_id

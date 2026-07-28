"""Public exceptions raised by :mod:`pysiebanxico`."""

from __future__ import annotations


class BanxicoError(Exception):
    """Base exception for errors raised by this package."""


class AuthenticationError(BanxicoError):
    """Raised when a token is missing, invalid, or rejected by the API."""


class InvalidRequestError(BanxicoError):
    """Raised when a public method receives invalid arguments."""


class InvalidResponseError(BanxicoError):
    """Raised when the SIE API response cannot be interpreted safely."""


class SeriesNotFoundError(BanxicoError):
    """Raised when the requested series cannot be found."""


class RateLimitError(BanxicoError):
    """Raised when the SIE API rate limit has been exceeded."""

    def __init__(self, message: str, *, seconds_to_reset: int | None = None) -> None:
        super().__init__(message)
        self.seconds_to_reset = seconds_to_reset

"""Independent Python client for Banco de México's SIE API."""

from .client import BanxicoClient
from .exceptions import (
    AuthenticationError,
    BanxicoError,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
    SeriesNotFoundError,
)
from .models import Observation, SeriesData

__version__ = "0.1.0.dev0"

__all__ = [
    "AuthenticationError",
    "BanxicoClient",
    "BanxicoError",
    "InvalidRequestError",
    "InvalidResponseError",
    "Observation",
    "RateLimitError",
    "SeriesData",
    "SeriesNotFoundError",
]

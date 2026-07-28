"""Synchronous client for Banco de México's SIE API."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Any

import requests

from .exceptions import (
    AuthenticationError,
    BanxicoError,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
    SeriesNotFoundError,
)
from .models import SeriesData
from .parsing import parse_series_data

DEFAULT_BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1"
MAX_SERIES_PER_REQUEST = 20


class BanxicoClient:
    """Client for historical time series published through the SIE API."""

    def __init__(
        self,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        clean_token = token.strip() if isinstance(token, str) else ""
        if not clean_token:
            raise AuthenticationError("A non-empty SIE API token is required.")
        if timeout <= 0:
            raise InvalidRequestError("timeout must be greater than zero.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json", "Bmx-Token": clean_token})

    def get_series_data(
        self,
        series_ids: str | Sequence[str],
        *,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
    ) -> tuple[SeriesData, ...]:
        """Return historical observations for one or more SIE series.

        Dates are optional ISO-8601 strings (``YYYY-MM-DD``) or
        :class:`datetime.date` values. The SIE API accepts at most 20 series per
        request; callers with more series should issue multiple calls for now.
        """
        ids = _validate_series_ids(series_ids)
        start = _parse_iso_date(start_date, name="start_date")
        end = _parse_iso_date(end_date, name="end_date")
        if (start is None) != (end is None):
            raise InvalidRequestError("start_date and end_date must be provided together.")
        if start is not None and end is not None and start > end:
            raise InvalidRequestError("start_date must not be after end_date.")

        path = f"/series/{','.join(ids)}/datos"
        if start is not None and end is not None:
            path = f"{path}/{start.isoformat()}/{end.isoformat()}"

        return parse_series_data(self._get_json(path))

    def _get_json(self, path: str) -> dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}{path}", timeout=self.timeout)
        except requests.RequestException as exc:
            raise BanxicoError("The SIE API request failed.") from exc

        payload = _response_json(response)
        message = _api_message(payload)
        if response.status_code in {401, 403}:
            raise AuthenticationError(message or "The SIE API rejected the token.")
        if response.status_code == 404:
            raise SeriesNotFoundError(message or "The requested SIE series was not found.")
        if response.status_code == 429:
            raise RateLimitError(
                message or "The SIE API rate limit has been exceeded.",
                seconds_to_reset=_seconds_to_reset(payload),
            )

        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise BanxicoError(message or "The SIE API returned an HTTP error.") from exc

        return payload


def _validate_series_ids(series_ids: str | Sequence[str]) -> tuple[str, ...]:
    candidates = (series_ids,) if isinstance(series_ids, str) else tuple(series_ids)
    if not candidates:
        raise InvalidRequestError("At least one series identifier is required.")
    if len(candidates) > MAX_SERIES_PER_REQUEST:
        raise InvalidRequestError(
            f"The SIE API accepts at most {MAX_SERIES_PER_REQUEST} series per request."
        )

    clean_ids: list[str] = []
    for series_id in candidates:
        if not isinstance(series_id, str) or not series_id.strip():
            raise InvalidRequestError("Every series identifier must be a non-empty string.")
        clean_ids.append(series_id.strip())
    return tuple(clean_ids)


def _parse_iso_date(value: str | date | None, *, name: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise InvalidRequestError(f"{name} must be an ISO-8601 date string or date object.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InvalidRequestError(f"{name} must use YYYY-MM-DD format.") from exc


def _response_json(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise InvalidResponseError("The SIE API returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise InvalidResponseError("The SIE API response must be a JSON object.")
    return payload


def _api_message(payload: dict[str, Any]) -> str | None:
    bmx = payload.get("bmx")
    if not isinstance(bmx, dict):
        return None
    message = bmx.get("mensaje")
    return message.strip() if isinstance(message, str) and message.strip() else None


def _seconds_to_reset(payload: dict[str, Any]) -> int | None:
    bmx = payload.get("bmx")
    if not isinstance(bmx, dict):
        return None
    value = bmx.get("secondsToReset")
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

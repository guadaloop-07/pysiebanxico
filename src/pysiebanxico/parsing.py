"""Pure parsing functions for SIE API payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .exceptions import InvalidResponseError
from .models import Observation, SeriesData, SeriesMetadata

_MISSING_VALUES = frozenset({"", "N/E", "N.D.", "ND", "NA", "N/A"})


def parse_series_data(payload: Any) -> tuple[SeriesData, ...]:
    """Parse a ``/datos`` payload into immutable public models."""
    if not isinstance(payload, Mapping):
        raise InvalidResponseError("The SIE API response must be a JSON object.")

    bmx = payload.get("bmx")
    if not isinstance(bmx, Mapping):
        raise InvalidResponseError("The SIE API response does not contain a 'bmx' object.")

    message = bmx.get("mensaje")
    if isinstance(message, str) and message.strip():
        raise InvalidResponseError(f"The SIE API returned an error: {message.strip()}")

    raw_series = bmx.get("series")
    if not isinstance(raw_series, Sequence) or isinstance(raw_series, (str, bytes)):
        raise InvalidResponseError("The SIE API response does not contain a series list.")

    return tuple(_parse_series(item) for item in raw_series)


def parse_series_metadata(payload: Any) -> tuple[SeriesMetadata, ...]:
    """Parse a series metadata payload into immutable public models."""
    raw_series = _series_list(payload)
    result: list[SeriesMetadata] = []
    for item in raw_series:
        if not isinstance(item, Mapping):
            raise InvalidResponseError("A series response must be a JSON object.")
        series_id = item.get("idSerie")
        title = item.get("titulo")
        if not isinstance(series_id, str) or not series_id.strip():
            raise InvalidResponseError("A series response does not contain a valid 'idSerie'.")
        if title is not None and not isinstance(title, str):
            raise InvalidResponseError("A series title must be a string when present.")
        result.append(SeriesMetadata(series_id=series_id.strip(), title=title))
    return tuple(result)


def _parse_series(raw_series: Any) -> SeriesData:
    if not isinstance(raw_series, Mapping):
        raise InvalidResponseError("A series response must be a JSON object.")

    series_id = raw_series.get("idSerie")
    if not isinstance(series_id, str) or not series_id.strip():
        raise InvalidResponseError("A series response does not contain a valid 'idSerie'.")

    title = raw_series.get("titulo")
    if title is not None and not isinstance(title, str):
        raise InvalidResponseError("A series title must be a string when present.")

    raw_observations = raw_series.get("datos", [])
    if not isinstance(raw_observations, Sequence) or isinstance(raw_observations, (str, bytes)):
        raise InvalidResponseError("A series 'datos' field must be a list.")

    clean_id = series_id.strip()
    observations = tuple(_parse_observation(clean_id, item) for item in raw_observations)
    return SeriesData(series_id=clean_id, title=title, observations=observations)


def _series_list(payload: Any) -> Sequence[Any]:
    if not isinstance(payload, Mapping):
        raise InvalidResponseError("The SIE API response must be a JSON object.")
    bmx = payload.get("bmx")
    if not isinstance(bmx, Mapping):
        raise InvalidResponseError("The SIE API response does not contain a 'bmx' object.")
    message = bmx.get("mensaje")
    if isinstance(message, str) and message.strip():
        raise InvalidResponseError(f"The SIE API returned an error: {message.strip()}")
    raw_series = bmx.get("series")
    if not isinstance(raw_series, Sequence) or isinstance(raw_series, (str, bytes)):
        raise InvalidResponseError("The SIE API response does not contain a series list.")
    return raw_series


def _parse_observation(series_id: str, raw_observation: Any) -> Observation:
    if not isinstance(raw_observation, Mapping):
        raise InvalidResponseError("An observation must be a JSON object.")

    raw_date = raw_observation.get("fecha")
    if not isinstance(raw_date, str):
        raise InvalidResponseError("An observation does not contain a valid date.")

    try:
        observation_date = datetime.strptime(raw_date.strip(), "%d/%m/%Y").date()
    except ValueError as exc:
        raise InvalidResponseError(f"Unsupported SIE date: {raw_date!r}") from exc

    raw_value = raw_observation.get("dato")
    return Observation(
        series_id=series_id,
        date=observation_date,
        value=_parse_value(raw_value),
        raw_value=None if raw_value is None else str(raw_value),
    )


def _parse_value(raw_value: Any) -> float | None:
    if raw_value is None:
        return None

    if isinstance(raw_value, bool):
        return None
    if isinstance(raw_value, int | float):
        return float(raw_value)

    value = str(raw_value).strip()
    if value.upper() in _MISSING_VALUES:
        return None

    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None

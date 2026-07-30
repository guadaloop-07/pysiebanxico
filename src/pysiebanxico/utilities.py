"""Dependency-free utilities for working with SIE series results."""

from __future__ import annotations

from collections.abc import Sequence

from .models import SeriesData, SeriesMetadata


def index_by_id(series: Sequence[SeriesData]) -> dict[str, SeriesData]:
    """Return series indexed by identifier.

    Raises:
        ValueError: If more than one item has the same series identifier.
    """
    result: dict[str, SeriesData] = {}
    for item in series:
        if item.series_id in result:
            raise ValueError(f"Duplicate series identifier: {item.series_id!r}.")
        result[item.series_id] = item
    return result


def to_records(series: Sequence[SeriesData]) -> list[dict[str, str | float | None]]:
    """Flatten observations into JSON- and CSV-friendly records.

    Dates are represented as ISO-8601 strings. ``value`` is numeric when the
    SIE observation can be parsed, while ``raw_value`` preserves the original
    API text.
    """
    return [
        {
            "series_id": item.series_id,
            "title": item.title,
            "date": observation.date.isoformat(),
            "value": observation.value,
            "raw_value": observation.raw_value,
        }
        for item in series
        for observation in item.observations
    ]


def metadata_to_records(metadata: Sequence[SeriesMetadata]) -> list[dict[str, str | None]]:
    """Convert series metadata into JSON- and CSV-friendly records."""
    return [{"series_id": item.series_id, "title": item.title} for item in metadata]

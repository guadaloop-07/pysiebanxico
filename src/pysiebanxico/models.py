"""Typed data models returned by the public client."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Observation:
    """A single observation returned by the SIE API."""

    series_id: str
    date: date
    value: float | None
    raw_value: str | None


@dataclass(frozen=True, slots=True)
class SeriesData:
    """Historical observations and optional title for one SIE series."""

    series_id: str
    title: str | None
    observations: tuple[Observation, ...]


@dataclass(frozen=True, slots=True)
class SeriesMetadata:
    """Metadata currently published by the SIE API for one series."""

    series_id: str
    title: str | None

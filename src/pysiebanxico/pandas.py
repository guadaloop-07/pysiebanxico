"""Optional pandas integrations for :mod:`pysiebanxico`."""

from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

from .models import SeriesData, SeriesMetadata
from .utilities import metadata_to_records, to_records

if TYPE_CHECKING:
    DataFrame = Any

_LONG_COLUMNS = ["series_id", "title", "date", "value", "raw_value"]
_METADATA_COLUMNS = ["series_id", "title"]


def to_dataframe(
    series: Sequence[SeriesData], *, layout: str = "long", series_id: str | None = None
) -> DataFrame:
    """Convert historical observations to a pandas DataFrame.

    The default ``long`` layout has one row per observation. The ``wide``
    layout uses dates as its index and series identifiers as columns. Set
    ``series_id`` to select one returned series before conversion.

    Raises:
        ImportError: If pandas is not installed.
        KeyError: If ``series_id`` is not present in ``series``.
        ValueError: If ``layout`` is unsupported.
    """
    if layout not in {"long", "wide"}:
        raise ValueError("layout must be either 'long' or 'wide'.")

    selected = _select_series(series, series_id)
    pandas = _require_pandas()
    frame = pandas.DataFrame.from_records(to_records(selected), columns=_LONG_COLUMNS)
    if layout == "long":
        return cast("DataFrame", frame)
    if frame.empty:
        return cast("DataFrame", pandas.DataFrame(index=pandas.Index([], name="date")))

    wide = frame.pivot(index="date", columns="series_id", values="value")
    return cast("DataFrame", wide.sort_index())


def metadata_to_dataframe(metadata: Sequence[SeriesMetadata]) -> DataFrame:
    """Convert series metadata to a pandas DataFrame."""
    pandas = _require_pandas()
    return cast(
        "DataFrame",
        pandas.DataFrame.from_records(metadata_to_records(metadata), columns=_METADATA_COLUMNS),
    )


def _select_series(series: Sequence[SeriesData], series_id: str | None) -> tuple[SeriesData, ...]:
    if series_id is None:
        return tuple(series)
    if not isinstance(series_id, str) or not series_id.strip():
        raise ValueError("series_id must be a non-empty string when provided.")

    clean_id = series_id.strip()
    selected = tuple(item for item in series if item.series_id == clean_id)
    if not selected:
        raise KeyError(clean_id)
    return selected


def _require_pandas() -> ModuleType:
    try:
        return import_module("pandas")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "pandas support requires the optional dependency. "
            'Install it with: pip install "pysiebanxico[pandas]".'
        ) from exc

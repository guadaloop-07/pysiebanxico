"""Tests for dependency-free data utilities."""

from datetime import date

import pytest

from pysiebanxico import (
    Observation,
    SeriesData,
    SeriesMetadata,
    index_by_id,
    metadata_to_records,
    to_records,
)


@pytest.fixture
def series() -> tuple[SeriesData, ...]:
    return (
        SeriesData(
            series_id="SF43718",
            title="FIX",
            observations=(
                Observation("SF43718", date(2024, 1, 2), 17.0297, "17.0297"),
                Observation("SF43718", date(2024, 1, 3), None, "N/E"),
            ),
        ),
        SeriesData(
            series_id="SF46410",
            title=None,
            observations=(Observation("SF46410", date(2024, 1, 2), 2.5, "2.5"),),
        ),
    )


def test_index_by_id_indexes_series_and_rejects_duplicates(series: tuple[SeriesData, ...]) -> None:
    result = index_by_id(series)

    assert result["SF43718"] == series[0]
    with pytest.raises(ValueError, match="Duplicate"):
        index_by_id((series[0], series[0]))


def test_to_records_flattens_observations(series: tuple[SeriesData, ...]) -> None:
    assert to_records(series) == [
        {
            "series_id": "SF43718",
            "title": "FIX",
            "date": "2024-01-02",
            "value": 17.0297,
            "raw_value": "17.0297",
        },
        {
            "series_id": "SF43718",
            "title": "FIX",
            "date": "2024-01-03",
            "value": None,
            "raw_value": "N/E",
        },
        {
            "series_id": "SF46410",
            "title": None,
            "date": "2024-01-02",
            "value": 2.5,
            "raw_value": "2.5",
        },
    ]


def test_metadata_to_records() -> None:
    metadata = (SeriesMetadata("SF43718", "FIX"), SeriesMetadata("SF46410", None))

    assert metadata_to_records(metadata) == [
        {"series_id": "SF43718", "title": "FIX"},
        {"series_id": "SF46410", "title": None},
    ]

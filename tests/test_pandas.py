"""Tests for optional pandas conversions."""

from datetime import date

import pandas as pd
import pytest

from pysiebanxico import Observation, SeriesData, SeriesMetadata
from pysiebanxico import pandas as pandas_module
from pysiebanxico.pandas import metadata_to_dataframe, to_dataframe


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
            title="Other",
            observations=(Observation("SF46410", date(2024, 1, 2), 2.5, "2.5"),),
        ),
    )


def test_to_dataframe_returns_long_and_wide_layouts(series: tuple[SeriesData, ...]) -> None:
    long = to_dataframe(series)
    wide = to_dataframe(series, layout="wide")

    assert list(long.columns) == ["series_id", "title", "date", "value", "raw_value"]
    assert pd.isna(long.loc[1, "value"])
    assert wide.loc["2024-01-02", "SF43718"] == 17.0297
    assert wide.loc["2024-01-02", "SF46410"] == 2.5


def test_to_dataframe_can_select_series_and_validate_arguments(
    series: tuple[SeriesData, ...],
) -> None:
    selected = to_dataframe(series, series_id="SF43718")

    assert selected["series_id"].unique().tolist() == ["SF43718"]
    with pytest.raises(KeyError):
        to_dataframe(series, series_id="missing")
    with pytest.raises(ValueError, match="layout"):
        to_dataframe(series, layout="table")


def test_to_dataframe_handles_empty_results() -> None:
    frame = to_dataframe((), layout="wide")

    assert frame.empty
    assert frame.index.name == "date"


def test_metadata_to_dataframe() -> None:
    frame = metadata_to_dataframe((SeriesMetadata("SF43718", "FIX"),))

    assert frame.to_dict("records") == [{"series_id": "SF43718", "title": "FIX"}]


def test_to_dataframe_explains_how_to_install_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_pandas(_: str) -> None:
        raise ModuleNotFoundError

    monkeypatch.setattr(pandas_module, "import_module", missing_pandas)

    with pytest.raises(ImportError, match=r"pysiebanxico\[pandas\]"):
        to_dataframe(())

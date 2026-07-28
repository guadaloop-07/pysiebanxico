from __future__ import annotations

from typing import Any

import pytest
import requests

from pysiebanxico import (
    AuthenticationError,
    BanxicoClient,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
)


class FakeResponse:
    def __init__(self, payload: Any, *, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def json(self) -> Any:
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.headers: dict[str, str] = {}
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout: float) -> FakeResponse:
        self.calls.append((url, timeout))
        return self.response


def test_get_series_data_builds_range_request_and_parses_observations() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "bmx": {
                    "series": [
                        {
                            "idSerie": "SF43718",
                            "titulo": "Exchange rate",
                            "datos": [
                                {"fecha": "31/01/2024", "dato": "17.1842"},
                                {"fecha": "29/02/2024", "dato": "N/E"},
                            ],
                        }
                    ]
                }
            }
        )
    )
    client = BanxicoClient(
        " token ", base_url="https://example.test/v1/", timeout=12, session=session
    )

    result = client.get_series_data(["SF43718"], start_date="2024-01-01", end_date="2024-12-31")

    assert session.headers == {"Accept": "application/json", "Bmx-Token": "token"}
    assert session.calls == [
        ("https://example.test/v1/series/SF43718/datos/2024-01-01/2024-12-31", 12)
    ]
    assert result[0].series_id == "SF43718"
    assert result[0].observations[0].value == 17.1842
    assert result[0].observations[1].value is None
    assert result[0].observations[1].raw_value == "N/E"


def test_get_series_data_rejects_invalid_dates_and_too_many_series() -> None:
    client = BanxicoClient("token", session=FakeSession(FakeResponse({"bmx": {"series": []}})))

    with pytest.raises(InvalidRequestError, match="provided together"):
        client.get_series_data("SF43718", start_date="2024-01-01")
    with pytest.raises(InvalidRequestError, match="must use YYYY-MM-DD"):
        client.get_series_data("SF43718", start_date="01/01/2024", end_date="2024-01-02")
    with pytest.raises(InvalidRequestError, match="at most 20"):
        client.get_series_data([f"SF{index}" for index in range(21)])


def test_client_raises_public_errors_for_token_response_and_rate_limit() -> None:
    with pytest.raises(AuthenticationError, match="non-empty"):
        BanxicoClient(" ")

    unauthorized = BanxicoClient(
        "token",
        session=FakeSession(FakeResponse({"bmx": {"mensaje": "Invalid token"}}, status_code=401)),
    )
    with pytest.raises(AuthenticationError, match="Invalid token"):
        unauthorized.get_series_data("SF43718")

    rate_limited = BanxicoClient(
        "token",
        session=FakeSession(
            FakeResponse(
                {"bmx": {"mensaje": "Too many requests", "secondsToReset": "30"}}, status_code=429
            )
        ),
    )
    with pytest.raises(RateLimitError) as error:
        rate_limited.get_series_data("SF43718")
    assert error.value.seconds_to_reset == 30


def test_client_rejects_invalid_json() -> None:
    client = BanxicoClient("token", session=FakeSession(FakeResponse(ValueError("not JSON"))))

    with pytest.raises(InvalidResponseError, match="invalid JSON"):
        client.get_series_data("SF43718")

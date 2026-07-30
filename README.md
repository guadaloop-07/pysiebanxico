# pysiebanxico

[![CI](https://github.com/guadaloop-07/pysiebanxico/actions/workflows/ci.yml/badge.svg)](https://github.com/guadaloop-07/pysiebanxico/actions/workflows/ci.yml)

An independent Python client for querying time series, historical data, and
metadata from Banco de México's Economic Information System (SIE).

> Status: this package is in early development. Historical-series retrieval is
> available; the public API may still change before version 0.1.0.

## Goal

`pysiebanxico` aims to provide a clear, typed, and tested interface for the SIE
REST API. The first release will cover historical data, current values, and
metadata; it will not include frequency conversion or a graphical interface.

## Installation

The distribution has not yet been published to PyPI. Once a stable version is
available, install it with:

```bash
python3 -m pip install pysiebanxico
```

## Planned usage

```python
from pysiebanxico import BanxicoClient

client = BanxicoClient()  # Reads BANXICO_TOKEN from the environment.
series = client.get_series_data(["SF43718"], start_date="2024-01-01", end_date="2024-12-31")

for observation in series[0].observations:
    print(observation.date, observation.value)
```

The client also exposes `get_current_value()` for the latest published
observation and `get_series_metadata()` for series titles in Spanish or English.
It automatically splits requests containing more than 20 series, the maximum
accepted by the SIE API. For transient network failures, server errors, or rate
limits, opt into limited retries with `BanxicoClient(max_retries=2)`.

Values such as `N/E`, `N.D.`, `ND`, `NA`, and `N/A` are exposed as `None` while
the original text remains available through `Observation.raw_value`.

## Data utilities

Use dependency-free helpers to index results or export plain records:

```python
from pysiebanxico import index_by_id, to_records

fix = index_by_id(series)["SF43718"]
records = to_records(series)
```

For pandas integration, install the optional extra:

```bash
python3 -m pip install "pysiebanxico[pandas]"
```

```python
from pysiebanxico.pandas import metadata_to_dataframe, to_dataframe

long = to_dataframe(series)
wide = to_dataframe(series, layout="wide")
metadata_frame = metadata_to_dataframe(metadata)
```

The long layout contains `series_id`, `title`, `date`, `value`, and `raw_value`.
The wide layout uses dates as its index and series identifiers as columns.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## Security

Each user must use their own SIE token. Do not commit tokens, `.env` files,
`tokens.yaml`, PyPI credentials, or API responses that contain them. Report
security issues according to [SECURITY.md](SECURITY.md).

## Independence notice

This project is an independent library. It is not affiliated with, sponsored by,
or endorsed by Banco de México. It uses Banco de México's public SIE API and
requires each user to provide their own token.

## License

Distributed under the [MIT License](LICENSE).

# pysiebanxico documentation

`pysiebanxico` is an independent Python client for Banco de México's Economic
Information System (SIE) API.

## Quick start

Set your personal SIE token outside your source code:

```bash
export BANXICO_TOKEN="your-token"
```

Then query a series:

```python
from pysiebanxico import BanxicoClient

client = BanxicoClient()
series = client.get_series_data("SF43718", start_date="2024-01-01", end_date="2024-01-31")
```

## Available features

- Historical observations through `get_series_data()`.
- Latest observations through `get_current_value()`.
- Series titles through `get_series_metadata()`.
- Automatic batching for requests with more than 20 series identifiers.
- Optional retries for transient API failures.
- Plain records and optional pandas DataFrames for analysis.

See the [README](../README.md) for installation, pandas examples, and the full
project overview. See [CONTRIBUTING.md](../CONTRIBUTING.md) for development and
contribution guidance.

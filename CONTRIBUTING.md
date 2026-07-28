# Contributing to pysiebanxico

Thank you for contributing. This project aims to provide a small, predictable,
and stable API for consuming Banco de México's SIE API.

## Set up the environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
pre-commit install
```

Before opening a pull request, run:

```bash
pre-commit run --all-files
ruff check .
ruff format --check .
mypy
pytest
python3 -m build
twine check dist/*
```

## Change workflow

Work on a branch from `main`: `feat/`, `fix/`, `docs/`, or `chore/`. Keep
changes focused and add tests for every behavioral change. Open a pull request;
continuous integration must pass before merging.

Use clear commit messages, such as `feat: add metadata endpoint` or
`fix: preserve missing observations`.

## Tests and network access

Regular tests must not call the live API or require a token. Use mocked
responses and fixtures. If integration tests are added, they must run manually
and read the token only from CI-provider secrets.

## Secrets

Do not include tokens, `.env`, `tokens.yaml`, PyPI credentials, or response
data that contains them. See [SECURITY.md](SECURITY.md) if you detect an
exposure.

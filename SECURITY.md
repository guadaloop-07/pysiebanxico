# Security policy

## Secrets

Do not publish SIE tokens, PyPI credentials, `.env` files, or `tokens.yaml`.
If a secret reaches the repository history, revoke or rotate it immediately:
removing it from the latest commit does not remove it from previous commits.

## Reporting a vulnerability

Do not open a public issue for a vulnerability or exposed credential. Contact
the maintainer listed in the package metadata privately and include a
description, reproduction steps, and estimated impact. Receipt will be
acknowledged and a fix coordinated before disclosing details.

## Scope

Tokens used to access the SIE are each user's responsibility. The package must
not log, display, or redistribute tokens.

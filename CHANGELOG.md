# Changelog

All notable changes to this project will be documented in this file. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Packaging, local validation, CI, and contribution-policy foundation.
- Historical-series client with typed observations, date and token validation,
  SIE response parsing, and public error types.
- Current-value and series-metadata client methods.
- Environment-token configuration, automatic multi-request batching, and
  opt-in retries for transient SIE API failures.

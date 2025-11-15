# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-15

### Added
- Initial release of FMI Weather Warnings integration
- Fetch weather warnings from Finnish Meteorological Institute CAP RSS feed
- Parse Common Alerting Protocol (CAP) format data
- Sensor entity showing count of active weather warnings
- Detailed warning attributes including:
  - Severity (Minor, Moderate, Severe, Extreme)
  - Urgency (Immediate, Expected, Future, Past)
  - Certainty (Observed, Likely, Possible, Unlikely)
  - Event type
  - Affected geographical area
  - Effective and expiration times
  - Safety instructions
  - Detailed descriptions
- Optional location-based filtering for warnings
- Config flow for easy setup through Home Assistant UI
- English translations
- Automatic updates every 5 minutes
- HACS compatibility
- Comprehensive documentation and examples
- Example automations and dashboard cards

### Technical Details
- Uses `feedparser` library for RSS parsing
- Implements Home Assistant DataUpdateCoordinator for efficient data management
- Cloud polling integration type
- Compatible with Home Assistant 2023.1.0+

[1.0.0]: https://github.com/Aasikki/fmi-weather-warnings/releases/tag/v1.0.0

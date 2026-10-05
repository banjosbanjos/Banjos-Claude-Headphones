# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Sourcing helper `tools/find_sources.py` and `docs/sourcing-guide.md` for getting wanted songs into the library legally. Free mode (Freegal weekly queue, free download links, ear-only fallback) is the default. Paid mode is optional.
- HEP-0001 proposing a built-in `headphones want` subsystem.
- SPEC open issues OI-8 (vinyl surface noise) and OI-9 (sourcing).

### Changed

- Sourcing is free only by default. SPEC §6.1, ADR-0001, the evaluation plan and the README now use only free, legal sources. Source labels gain `owned_purchase`, `freegal`, `free_download` and `cc_licensed`.

## [0.2.0-draft] - 2026-10-05

### Changed

- Spec revised after ten adversarial reviews. See docs/reviews/adversarial-reviews.md.

## [0.1.0-draft] - 2026-10-05

### Added

- Initial specification draft.

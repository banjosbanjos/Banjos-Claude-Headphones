# ADR-0002: Spotify boundary

- Status: Accepted
- Date: 2026-10-05

## Context

Facts checked on 2026-10-05:

- Spotify Developer Policy III.13: do not analyze Spotify Content or the Spotify Service for any purpose, including building user profiles or derived listenership metrics.
- Spotify Developer Policy III.14: do not use the Spotify Platform or any Spotify Content to train a machine learning or AI model, or otherwise ingest Spotify Content into one.
- February 2026 Web API changes: `external_ids` (ISRC), `popularity`, `available_markets` and `linked_from` removed from track objects. Bulk fetch endpoints, artist top tracks and new releases removed. Development Mode apps need a Premium owner and are limited to 5 users and one Client ID per developer for new apps.
- Audio Features, Audio Analysis, Recommendations and Related Artists were already closed to new apps in November 2024.

A Headphones-owned Spotify client that pulled metadata and passed it to Claude would ingest Spotify content into an AI model.

## Decision

1. Headphones ships no Spotify Web API client (SPEC REQ-SPOT-01).
2. Spotify data reaches the agent only through the official Spotify connector the listener authorizes in Claude, under its own terms.
3. Headphones stores nothing from Spotify except a listener-confirmed track URI per asset, as an opaque link.
4. Identity comes from Chromaprint fingerprints and MusicBrainz, not Spotify.
5. The listener's own extended streaming history export may be imported locally, off by default, pending the open question in SPEC OI-1.

## Consequences

- No ISRC from Spotify. Matching an owned file to a Spotify track needs the listener's confirmation.
- Behavioral metrics need the data export, which takes Spotify up to 30 days to deliver.
- The design does not depend on Spotify keeping any endpoint open.

## Revisit when

Spotify changes its Developer Policy, the official connector's terms change, or the project obtains written guidance from Spotify.

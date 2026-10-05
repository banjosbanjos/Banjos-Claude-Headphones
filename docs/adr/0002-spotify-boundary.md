# ADR-0002: Spotify boundary

- Status: Accepted, amended in 0.2.0
- Date: 2026-10-05

## Context

Facts checked on 2026-10-05:

- **Developer Policy** (https://developer.spotify.com/policy/): binds apps built on the Spotify Platform. Do not analyze Spotify Content or the Spotify Service. Do not use the Spotify Platform or any Spotify Content to train a machine learning or AI model "or otherwise ingest Spotify Content into a machine learning or AI model".
- **User Guidelines** (https://www.spotify.com/us/legal/user-guidelines/), part of the Terms of Use every listener accepts: forbid "using any part of the Services or Content to train a machine learning or AI model or otherwise ingesting Spotify Content into a machine learning or AI model", and forbid ripping or recording.
- **Developer Terms** (https://developer.spotify.com/terms): define Spotify Content broadly, including user data.
- **Web API changes**: Audio Features, Audio Analysis, Recommendations and Related Artists closed to new apps in November 2024. The February 2026 changes applied to Development Mode apps and removed several endpoints and fields. The removal of `external_ids` (ISRC) was reversed in March 2026 (https://developer.spotify.com/documentation/web-api/references/changes/march-2026).
- **Spotify in Claude**: Spotify launched its Claude integration on 2026-04-23 (https://newsroom.spotify.com/2026-04-23/claude-integration/). It lets Claude search, recommend, play and control Spotify. Its use is governed by Spotify's and Anthropic's terms for that integration.

## Decision

1. Headphones ships no Spotify Web API client (SPEC REQ-SPOT-01), so it is not a Spotify Platform app.
2. Spotify data reaches the agent only through Spotify's own connector in Claude.
3. Headphones stores nothing obtained from Spotify. It stores only Spotify URIs the listener typed or pasted (links and external tracks), as opaque strings, and, if the listener imports it, their own minimized streaming history (SPEC REQ-SPOT-03 to 05).
4. Identity comes from Chromaprint fingerprints and AcoustID, not Spotify.
5. History import and BEHAVIORAL metrics are off by default with a notice quoting the User Guidelines clause, pending SPEC OI-1.

## Consequences

- Matching an owned file to a Spotify track needs the listener's confirmation.
- Behavioral metrics need the listener's data export, which Spotify can take up to 30 days to deliver.
- Nothing in Headphones depends on any Spotify endpoint staying open.

## Revisit when

Spotify's User Guidelines, Developer Policy or connector terms change, or Spotify answers the OI-1 question.

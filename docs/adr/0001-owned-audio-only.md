# ADR-0001: Analyze owned audio only

- Status: Accepted
- Date: 2026-10-05

## Context

The harness needs audio to measure anything. The listener uses Spotify. Spotify streams are DRM-protected, Spotify's terms forbid stream ripping and copying, and its Developer Policy forbids analyzing Spotify content or ingesting it into an AI model. The 30-second preview URLs that some projects used for analysis were removed from most responses in November 2024 and further in February 2026, and previews would be too short for structure, endings or chill moments anyway.

Other streaming services (Apple Music, Tidal, Deezer, YouTube Music) have the same DRM and similar terms.

## Decision

Headphones analyzes only audio files the listener has put in a local library. It never fetches, records or intercepts audio from any service. The recommended sources are DRM-free purchases, with Bandcamp first because it carries most of the listener's profile (independent rock, power pop, jangle pop, picked country, small-group jazz) and sells lossless downloads. Listening happens on Headphones' own player (mpv), so the audio analyzed and the audio heard are the same file.

## Consequences

- The listener must buy or already own a track before Headphones can measure it. This costs money and limits coverage to what is sold DRM-free.
- Timestamps from the station are exact for the analyzed asset, which makes tap validation possible.
- Spotify remains useful for discovery and history, outside Headphones (ADR-0002).
- Values describe the owned master, which may differ from the streaming master. The skill tells the agent this.

## Alternatives considered

- **Loopback capture of Spotify playback.** Rejected. Violates Spotify's terms and the project's legal constraints.
- **Preview clips.** Rejected. Mostly removed, too short, and still Spotify content.
- **YouTube downloads.** Rejected. YouTube's terms forbid downloading except through its own features.

# ADR-0001: Analyze owned audio only

- Status: Accepted, amended in 0.2.0
- Date: 2026-10-05

## Context

The harness needs audio to measure anything. The listener uses Spotify. Spotify streams are DRM-protected, and Spotify's User Guidelines forbid ripping or recording content and forbid ingesting Spotify Content into an AI model. The 30-second preview URLs some projects analyzed were withdrawn from new apps in November 2024, and would be too short for structure, endings or chill moments anyway. Other streaming services have the same DRM and similar terms.

## Decision

Headphones analyzes only audio files the listener has put in a local library. It never fetches, records or intercepts audio from any service. Listening for analysis happens on Headphones' own station (mpv), so the audio analyzed and the audio heard are the same file.

The practical path, cheapest first:

1. **What you already own.** Existing downloads and CD rips cost nothing.
2. **DRM-free downloads.** Most of the listener's anchor artists are on major labels, and major-label catalogs are generally sold DRM-free on the iTunes Store (AAC) and Amazon (MP3). Independent releases are often on Bandcamp or Qobuz in lossless formats. Availability differs by artist and country, so check per purchase.
3. **Used CDs**, ripped where local private-copying law allows.

Store licences generally allow personal, non-commercial use only. Bandcamp's terms, for example, grant use "solely for personal, non-commercial use". Making stems for personal analysis fits that. Publishing stems or using purchased files for someone else's product does not.

For music the listener does not own, external playback mode (SPEC §7.4.4) lets them record ear judgments and moments while listening on Spotify. Nothing is measured from that audio.

## Consequences

- A track must be owned before Headphones can measure it. The evaluation plan estimates roughly $150 to $300 of purchases on top of what the listener already owns.
- Station timestamps are exact for the analyzed asset, which makes tap validation possible.
- Spotify stays useful for discovery, external playback mode and history, outside Headphones (ADR-0002).
- Values describe the owned master, which may differ from the streaming master. The skill tells the agent this.

## Alternatives considered

- **Loopback capture of Spotify playback.** Rejected. Breaks Spotify's terms.
- **Preview clips.** Rejected. Mostly withdrawn, too short, and still Spotify content.
- **YouTube downloads.** Rejected. YouTube's terms forbid downloading outside its own features.

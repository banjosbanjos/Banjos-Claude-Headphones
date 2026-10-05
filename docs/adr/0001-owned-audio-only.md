# ADR-0001: Analyze owned audio only

- Status: Accepted, amended in 0.2.0
- Date: 2026-10-05

## Context

The harness needs audio to measure anything. The listener uses Spotify. Spotify streams are DRM-protected, and Spotify's User Guidelines forbid ripping or recording content and forbid ingesting Spotify Content into an AI model. The 30-second preview URLs some projects analyzed were withdrawn from new apps in November 2024, and would be too short for structure, endings or chill moments anyway. Other streaming services have the same DRM and similar terms.

## Decision

Headphones analyzes only audio files the listener has put in a local library. It never fetches, records or intercepts audio from any service. Listening for analysis happens on Headphones' own station (mpv), so the audio analyzed and the audio heard are the same file.

The listener wants this to cost nothing, so the path is free only (amended 2026-10-05):

1. **What you already own**, including past purchases re-downloaded from their stores.
2. **Freegal Music** through a public library card: DRM-free MP3s to keep, usually about 5 a week. Strong on Sony Music's labels, weak on Universal's.
3. **Free and name-your-price releases** on Bandcamp, and Creative Commons music.
4. **Ear-only** for the rest, through external playback mode.

Buying downloads or used CDs stays possible for anyone who wants it, but nothing requires it.

Store licences generally allow personal, non-commercial use only. Bandcamp's terms, for example, grant use "solely for personal, non-commercial use". Making stems for personal analysis fits that. Publishing stems or using purchased files for someone else's product does not.

For music the listener does not own, external playback mode (SPEC §7.4.4) lets them record ear judgments and moments while listening on Spotify. Nothing is measured from that audio.

## Consequences

- A track must be owned before Headphones can measure it. With a free-only plan, coverage is limited by Freegal's weekly allowance and catalog, so some favorite songs stay ear-only. The evaluation uses free sources and costs nothing.
- Station timestamps are exact for the analyzed asset, which makes tap validation possible.
- Spotify stays useful for discovery, external playback mode and history, outside Headphones (ADR-0002).
- Values describe the owned master, which may differ from the streaming master. The skill tells the agent this.

## Alternatives considered

- **Loopback capture of Spotify playback.** Rejected. Breaks Spotify's terms.
- **Preview clips.** Rejected. Mostly withdrawn, too short, and still Spotify content.
- **YouTube downloads.** Rejected. YouTube's terms forbid downloading outside its own features.

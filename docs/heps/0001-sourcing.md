# HEP-0001: Sourcing, so every wanted song can reach Headphones

- **Author:** @banjosbanjos (drafted with AI assistance)
- **Created:** 2026-10-05
- **Status:** Discussion

## Summary

Add a `headphones want` subsystem that keeps the listener's want list, checks what is already owned, finds the cheapest legal way to get the rest, flags songs that exist only on physical media, and marks songs as acquired when their files arrive. A standalone version already exists as `tools/find_sources.py` and is documented in [docs/sourcing-guide.md](../sourcing-guide.md). This HEP proposes making it part of Headphones.

## Motivation

Headphones only measures owned audio (ADR-0001). The listener wants every song they would ever want to be available to it. Without help, finding each song across stores, comparing album and single prices, and spotting songs that were never sold digitally is slow manual work across thousands of songs. Songs that cannot be obtained would also drop out silently. This subsystem makes coverage measurable and the gaps explicit.

## Proposal

1. **Want list.** `headphones want add "Artist - Title"`, `headphones want import <file>`, and `headphones want import --spotify-export <dir>`. Export import runs locally, keeps only artist, title, album and a play count (plays of 30 s or more), and discards everything else before writing, in line with REQ-SPOT-05. Where AcoustID or MusicBrainz identifies a recording, the entry stores the MBID.
2. **Owned check.** Match the want list against the library by MBID, then by normalized artist and title.
3. **Availability check** (`headphones want check`), opt-in, run only on request:
   - iTunes Search API (paid mode only): album search plus album track lookup, then song search for the rest. At most 20 calls per minute.
   - MusicBrainz: store links ("purchase for download", "download for free") and release media formats (CD, vinyl, cassette). At most one call per second, with an identifying User-Agent.
   - Bandcamp, Amazon, Qobuz and Discogs are linked by search URL only. No scraping.
   - Results cached per query.
4. **Plan, free by default.** Group wanted songs as: already own, free download link found (MusicBrainz "download for free"), weekly Freegal queue (most-played first, sized to the listener's weekly allowance and number of cards), and ear-only (songs the listener reports are not on Freegal). The free plan makes no network calls unless MusicBrainz checking is turned on. An optional paid mode prices songs on the iTunes Store and picks album or singles, whichever is cheaper.
5. **Auto-match on ingest.** When `library add` ingests a file that matches a wanted song, mark it acquired and queue analysis.
6. **Agent access.** One MCP tool, `hp_want_summary`, returning counts per group and the estimated cost only. It returns no song titles from imported Spotify data. The full list stays in the CLI and in files.
7. **Never** buy, download or scrape anything.

## Affected requirements and metrics

- Amend REQ-ID-04 so that the sourcing subsystem may call the MusicBrainz API under the limits above. Analysis identity stays AcoustID-only.
- New REQ-WANT-01 to REQ-WANT-07 covering items 1 to 7.
- REQ-MCP-02 tool list gains `hp_want_summary` (read only).
- SPEC §8.1 gains the `want` commands. SPEC G7 and docs/privacy.md gain the two new opt-in network calls.
- No metric definitions change.

## Alternatives considered

- **Keep it as a separate script.** Works today, but cannot auto-match purchases or show coverage to the agent.
- **Use a store's affiliate or partner feed** (Apple Enterprise Partner Feed). Heavier, needs an agreement, no real benefit for one listener.
- **Scrape Bandcamp or Amazon.** Rejected. Against their terms and fragile.
- **Read artist and title from the Spotify connector.** Rejected. Would store connector data (REQ-SPOT-02).

## Security and privacy impact

Two new outbound HTTPS calls, both opt-in and only on request: itunes.apple.com and musicbrainz.org. They send artist, title and album text plus the listener's IP address, so Apple and MusicBrainz could learn which songs the listener is looking for. No new listeners, child processes, weights or evidence sources. Responses are untrusted text and follow REQ-MCP-03 and REQ-LS-18. The want list joins the privacy inventory, export and `forget all`, plus a new `forget --wants`.

## Legal and terms impact

Checked 2026-10-05:

- iTunes Search API: public, no key, roughly 20 calls per minute. Promotional assets such as artwork are licensed only for promoting store content. The subsystem uses text and links only, no artwork.
- MusicBrainz: core data CC0. One request per second and an identifying User-Agent are required.
- Spotify: the export is the listener's own data, processed locally. Imported titles never reach the agent through this subsystem (item 6), which keeps clear of SPEC OI-1.
- Freegal is named only as a suggestion. No integration.

## Evaluation impact

Helps the acquisition protocol for first-listen tracks (evaluation plan §2) by finding albums cheaply. No effect on ear scales, the golden set or past results.

## Status

Discussion.

## Discussion link

To be posted once GitHub Discussions is turned on.

## Decision

Pending. The listener of record decides under the single-maintainer model in GOVERNANCE.md.

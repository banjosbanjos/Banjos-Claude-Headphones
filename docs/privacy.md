# Privacy

Headphones is local software for one person. This page lists every kind of personal data it handles, where it lives, and how to remove it.

## Data inventory

| Data | Source | Where | Leaves the machine? |
|---|---|---|---|
| Library index (file hashes, technical metadata, tags) | Your audio files | SQLite in the data directory | No |
| Audio fingerprints | Computed from your files | SQLite | Only if online identity lookup is on: fingerprint and duration sent to AcoustID |
| Stems and feature arrays | Derived from your files | Content-addressed cache in the data directory | No |
| Evaluation records | Analysis | SQLite, exportable as JSON | No, except through the agent (see below) |
| Ear judgments and taps | You, at the listening station | SQLite | No, except through the agent |
| Stated preferences | You, via `headphones stated add` | SQLite | No, except through the agent |
| Spotify extended streaming history | Your own data export, imported by you | SQLite, only if BEHAVIORAL metrics are enabled | No, except through the agent |
| Linked Spotify URIs | You | SQLite | No, except through the agent |
| Logs | Headphones | Log directory, `asset_id` only at default verbosity | No |

## Through the agent

When Claude Code reads Headphones results through the MCP server, that content enters the conversation and is sent to the model provider under the terms that govern your Claude account. Headphones cannot control what happens after that. The MCP server returns only what a tool call asks for, never audio, never file paths.

## Defaults

- No telemetry, analytics or crash reporting.
- Online identity lookup is on by default and can be turned off with `identity.online = false`. `headphones init` asks before enabling it.
- BEHAVIORAL metrics and history import are off by default (SPEC REQ-SPOT-04).

## Your controls

| Command | Effect |
|---|---|
| `headphones export` | All records, ear judgments, stated preferences and history as JSON Lines |
| `headphones forget <asset>` | Removes one asset's records, ear judgments, cache and link |
| `headphones forget --history` | Removes all imported streaming history |
| `headphones forget all` | Removes the database, cache and logs. Leaves your audio files untouched. |
| `headphones cache prune` | Removes stems and feature arrays, keeps records |

## Retention

Nothing expires automatically. Stems are evicted by the cache size limit (SPEC REQ-CACHE-02). Records and ear judgments stay until you remove them.

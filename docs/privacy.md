# Privacy

Headphones is local software for one person. It has no server, and the project receives none of your data. This page lists every kind of data Headphones handles, where it lives, what leaves your machine, and how to remove it.

This page is informative, but SPEC.md makes it the definition of `headphones export` and `headphones forget` (REQ-STORE-05). Where it states a rule, the rule is cited by its SPEC REQ ID.

Directory names below use Linux defaults. Headphones uses the platform's standard user directories on macOS and Windows. `headphones doctor --unredacted` prints the actual paths.

| Name used here | Linux default | Protection |
|---|---|---|
| Data directory | `~/.local/share/headphones` (REQ-STORE-01) | 0700, files 0600 (REQ-STORE-08) |
| Cache directory | Content-addressed, keyed by SHA-256 (REQ-STORE-02) | 0700, files 0600 |
| Log directory | Platform log or state directory | 0700, files 0600 |
| Config directory | `~/.config/headphones` (SPEC §8.3) | User-only |
| Socket directory | Per-user runtime directory | 0700, socket 0600 (REQ-LS-12) |

On Windows the same directories use a current-user-only ACL instead of modes (REQ-STORE-08).

## Data inventory

"Through the agent" means the data reaches Claude Code when the agent calls an MCP tool, and from there goes to the model provider. See [What the agent sends to the model provider](#what-the-agent-sends-to-the-model-provider).

| Data | Source | Where | Sent off the machine? | Removed by |
|---|---|---|---|---|
| Library roots and asset paths | You, with `headphones library add` | Config file (roots) and SQLite (asset paths, device and inode) | No. MCP tools never accept or return paths (REQ-MCP-05, REQ-MCP-07). Paths appear in logs only at debug verbosity (REQ-SEC-07). | `forget <asset>` (that asset's paths), `forget all` |
| Config file | You and `headphones init` | TOML file in the config directory. Holds library roots, the lookup and history settings, named plugins and thresholds. | No | `forget all` |
| Library index and tags | Your audio files | SQLite. Holds `asset_id`, `pcm_sha256`, technical metadata, tag text and your optional `source` label (REQ-ING-03, REQ-ING-04, REQ-SRC-04). | Tag text, through the agent, inside `untrusted_metadata` (REQ-MCP-03). Audio never. | `forget <asset>`, `forget all` |
| Fingerprints | Computed from your files (REQ-ID-01) | SQLite | Only if you turn on online lookup. Then the fingerprint and duration go to AcoustID (REQ-ID-02). | `forget <asset>`, `forget all` |
| MBIDs, ISRCs and metadata from AcoustID | AcoustID response, only when lookup is on | SQLite, cached so each asset is looked up once (REQ-ID-04, REQ-ID-07). Only MBIDs, ISRCs, recording length and artist, title and album strings are kept. | Artist, title and album strings, through the agent, inside `untrusted_metadata` | `forget <asset>`, `forget all` |
| Stems and feature arrays | Derived from your files by analysis | Cache directory | No. Stems never leave the machine through any Headphones interface, and the MCP server never returns audio (REQ-SEP-03). | `cache prune`, LRU eviction (REQ-CACHE-02), `forget <asset>`, `forget all` |
| Renders in the cache | `hp_render` or `headphones render` | Cache directory | Yes, through the agent, when it asks for one. The PNG and its caption go to the model provider. Renders never contain tag text (REQ-REND-01). | `forget <asset>`, `forget all` |
| Render files written with `headphones render --out` | You | Wherever you wrote them | No | You. Headphones does not track these files. |
| Evaluation records | Analysis, plus ear, stated and behavioral values | SQLite. Values are append-only and superseded values are kept (REQ-STORE-04). | Through the agent. By default a compact summary per metric: ID, status, evidence class, confidence, main value and at most 5 timestamps (REQ-MCP-09). | `forget <asset>`, `forget all` |
| Ear judgments | You, at the station or with `headphones ear import` | SQLite, HMAC-chained (REQ-STORE-09). Includes taps, answers, free-text notes, the wording of any agent question (`capture.agent_prompt`, REQ-LS-19), familiarity and first-listen flags. | Values, through the agent, except in blind mode (REQ-MCP-06). Notes are omitted unless the agent asks for them by name (REQ-MCP-09). The agent's own question wording came from the agent. | `forget <asset>`, `forget all`. External-track ear values: `forget --external <uri>`, `forget all`. |
| Device labels and latency calibrations | You, with `headphones station --calibrate` | SQLite. Per label you choose: method, median correction and spread (REQ-LS-08). Labels are never taken from OS or Bluetooth device names. | Device labels only if the agent asks for `capture.device` by name (REQ-MCP-09). Never in logs (REQ-SEC-07). | `forget all` |
| Calibration events | The store, when an ear value and an analyzer value disagree beyond the agreement band (REQ-VAL-07) | SQLite | Through the agent as agreement statistics in `hp_calibration_report`, excluding sealed held-out assets and blind-mode assets (REQ-MCP-06) | `forget <asset>`, `forget all` |
| Stated preferences | You, with `headphones stated add` | SQLite, verbatim with date and context, HMAC-chained (REQ-EVID-04, REQ-STORE-09) | Indirectly, through the agent, when a composite uses one (for example the BUILD tempo range, REQ-COMP-03) | `forget --stated <id>`, `forget all`. `stated retract <id>` keeps the record but marks it no longer true. |
| Imported streaming history | Your own Spotify extended streaming history export, imported by you | SQLite, only when history is enabled. Minimized before writing to `ts`, `ms_played`, `spotify_track_uri`, `reason_start`, `reason_end`, `skipped` and `shuffle`. Incognito rows are dropped unless you opt in (REQ-SPOT-05). | No MCP tool returns raw rows. `BEHAVIORAL` values derived from history reach the agent in evaluations. | `forget --history`, `forget all`. The export files you downloaded from Spotify stay where you put them. |
| Linked and external Spotify URIs | You, with `headphones link` or `headphones station --external` | SQLite. Opaque strings Headphones never dereferences (REQ-SPOT-02). External-track records also hold the artist and title you typed (REQ-LS-11). | Through the agent, as track references and `untrusted_metadata` | Links: `forget <asset>`, `forget all`. External-track records: `forget --external <uri>`, `forget all`. |
| Run manifests | Each analysis run (REQ-OBS-01) | Data directory | No | `forget <asset>`, `forget all` |
| Job queue and pending ear requests | The agent (`hp_analyze`, `hp_request_ear`) and you (CLI) | Station and SQLite. Ear requests hold the agent's question wording. | Job state and request state go back to the agent. `hp_ear_status` never returns answers. | `forget <asset>`, `forget all` |
| Exclusion list | `forget <asset>` without `--allow-rescan` | SQLite. Holds the content hashes of forgotten assets so the next scan skips them (REQ-STORE-07). No paths or tags. | No | `forget all` |
| Logs | Headphones | Log directory, JSON Lines (REQ-OBS-02). Never contain tag text, ear notes, stated text, history fields or device labels. Paths only at debug verbosity (REQ-SEC-07). | No | 30-day rotation, `forget <asset>` (lines that name the asset), `forget all` |
| Evidence chain key | `headphones init` | OS keychain: Secret Service, macOS Keychain or Windows Credential Manager (REQ-STORE-09) | No | `forget all` |
| Evidence chain head file | Station and CLI | A 0600 file outside the database (REQ-STORE-09). Redaction entries written by `forget` hold a row count and time, never content. | No | `forget all` |
| Migration backups | Database migrations | Data directory | No | Deleted once a migration is confirmed. `forget` also removes matching rows from any backup that still exists (REQ-STORE-06). `forget all` removes them. |
| Exports you write | You, with `headphones export` | Wherever you wrote them | No | You |
| Benchmark records | `headphones bench run` | Data directory. Holds agent answers, scores and run settings. | The agent conversation during a run goes to the model provider. Published reports carry only aggregate numbers and `pcm_sha256` references (REQ-SRC-06). | `forget all`. Published reports stay published. |
| Model weights | Downloaded by `headphones init` | Weights directory | The download reveals your IP address to the weight host. Weights are not personal data. | Not removed by `forget all`. Delete the weights directory by hand if you want it gone. |
| Claude Code's own transcripts | Claude Code | Claude Code's local storage and the model provider, under your Claude account terms | Yes. Everything the agent read or wrote, including Headphones results. | Not Headphones. Use Claude Code's and your account's own controls. Headphones cannot delete them. |

Microphone audio. Latency calibration can use acoustic loopback through a microphone (REQ-LS-08). The recording is held in memory only and discarded once the latency is measured. Only the method, median correction and spread are stored.

## What the agent sends to the model provider

Anything Claude Code reads through the Headphones MCP server enters the conversation and is sent to the model provider under the terms of your Claude account. Headphones cannot control what happens after that. This includes:

- Library search results, including tag text inside `untrusted_metadata`.
- Evaluation values, evidence classes, confidence and timestamps.
- BUILD and FEEL results, which can draw on stated preferences and behavioral values.
- Rendered images and their captions.
- Agreement statistics from calibration reports.

Headphones limits what goes out by default:

- Ear notes (`capture.note`) and device labels (`capture.device`) are omitted unless the agent asks for them by name (REQ-MCP-09).
- `hp_ear_status` reports only whether a request is pending, answered or expired, never the answers.
- No tool returns audio, paths, raw history rows, or stderr from child processes (REQ-SEP-03, REQ-MCP-05, REQ-MCP-07).
- In blind mode no tool returns ear values or calibration data for the listed assets (REQ-MCP-06).

The agent also has Claude Code's shell and file tools, which run as you. Those tools can read the Headphones database directly, outside these limits. The deny rules Headphones ships block writes, not reads (REQ-STORE-11). See the [security self-assessment](security-self-assessment.md), threats T3 and T13.

## Network calls

This is every network call Headphones makes.

| Call | When | Destination | What is sent | Default | SPEC |
|---|---|---|---|---|---|
| Weight download | `headphones init`, and after an upgrade that changes weights | The weight host named in the release manifest, over HTTPS | An ordinary HTTPS request. The host learns your IP address, the time, and which weight files you fetched. | Runs at install | REQ-WGT-03 |
| Release signature check | `headphones init` and upgrade | Depends on the Sigstore verifier. Verification may fetch Sigstore's public trust material. | No personal data. The host may learn your IP address. | Runs at install | REQ-SEC-06 |
| AcoustID lookup | During ingest, once per asset, only when you turned it on | AcoustID web service, over HTTPS, under 3 requests per second | Fingerprint, duration, the project's registered AcoustID client key (shared by every Headphones user), a User-Agent string, and your IP address. Never file names, paths, tags or listening data. | Off. `init` asks, default "no". | REQ-ID-02, REQ-ID-07 |

There are no other calls. In particular:

- No telemetry, analytics, crash reporting or update checks (REQ-SEC-05).
- No direct MusicBrainz API calls (REQ-ID-04).
- No Spotify Web API client and no calls to the Spotify connector (REQ-SPOT-01, REQ-LS-11).
- Analyzers run with `HF_HUB_OFFLINE=1` and empty model caches, so a library that tries to download a model fails (REQ-WGT-02). On Linux, child processes also have no network at all (REQ-RES-01). macOS and Windows do not provide that isolation.
- Desktop notifications for queued ear forms are local (REQ-LS-20).

Outside Headphones but worth knowing: installing or upgrading the package with `uv` or `pip` contacts the package index, and Claude Code sends the conversation to the model provider.

AcoustID is free for non-commercial use only (REQ-ID-07). Data it returns is licensed CC BY-SA and is attributed (REQ-ID-04).

## Defaults

- **No telemetry.** Headphones never sends usage data, analytics or crash reports (REQ-SEC-05).
- **Online lookup is off.** `headphones init` asks whether to turn on AcoustID lookup, with the default answer "no", and says exactly what would be sent (REQ-ID-02). Without it, identity comes from tags and is marked `tags_only` (REQ-ID-03).
- **History and `BEHAVIORAL` metrics are off.** Turning them on shows a notice that quotes the Spotify User Guidelines clause forbidding "ingesting Spotify Content into a machine learning or AI model", and your data portability right as the counter-argument. It then asks for explicit confirmation (REQ-SPOT-04). Whether this use is allowed is unresolved (SPEC OI-1).
- **Incognito history rows are dropped** unless you opt in (REQ-SPOT-05).
- **Logs keep 30 days** and then rotate out (REQ-SEC-07).
- **The browser UI is off.** If it exists it binds to 127.0.0.1 only (REQ-LS-03).
- **Plugins are off** until you name them in the config file (REQ-PLUG-03).

## Your controls

| Command | What it does |
|---|---|
| `headphones export` | Writes every class in the inventory that Headphones holds, as JSON Lines. Each line has a record type: `library_entry` (paths, technical metadata, tags, source label, fingerprint and identity), `evaluation_record` (validates against [evaluation-record.schema.json](../schemas/evaluation-record.schema.json), REQ-STORE-03), `ear_value` (including notes and agent prompts), `stated`, `calibration_event`, `history_play`, `link`, `external_record` and `device_calibration`. Files that are not records are copied beside it: the config file, run manifests, logs, cached renders, benchmark records, and the job queue and pending ear requests. Stems and feature arrays are listed by hash and not copied, because they can be rebuilt from your audio. The evidence chain key is never exported, since anyone holding it could forge your chain. Render files written with `--out`, earlier exports and Claude Code transcripts are not held by Headphones and are not included. |
| `headphones forget <asset> [--allow-rescan]` | For every asset sharing the target's `pcm_sha256`, deletes library entries and paths, fingerprints and identity, links, values including superseded ones, ear judgments, calibration events, renders, stems and features, run manifests, queued jobs and ear requests, and log lines that name the asset. Adds the asset to the exclusion list so the next scan does not re-ingest it, unless you pass `--allow-rescan`. Then checkpoints the WAL and runs `VACUUM`. The database always runs with `PRAGMA secure_delete=ON` (REQ-STORE-07). Writes a redaction entry to the evidence chain with the rows removed, the count and the time, but no content, so `doctor` can tell a forget from tampering (REQ-STORE-09). Removes matching rows from any migration backup that still exists (REQ-STORE-06). Your audio file is not touched. History rows for a linked track, stated preferences (use `forget --stated`), external-track records (use `forget --external`), `--out` render files, exports and Claude Code transcripts are not affected. |
| `headphones forget --history` | Deletes all imported history rows, every `BEHAVIORAL` value derived from them, and any calibration event derived from those values. The same `VACUUM`, secure delete and backup cleanup apply. First-listen flags already stored on ear judgments are kept, because they are part of those judgments. |
| `headphones forget --stated <id>` | Deletes one stated preference and writes a redaction entry to the evidence chain. `headphones stated retract <id>` is the softer option: it keeps the record and marks it no longer true. |
| `headphones forget --external <uri>` | Deletes the external-track record for that URI and every ear value in it, with the same `VACUUM`, secure delete and redaction entry. |
| `headphones forget all` | Deletes the database, the cache, the logs, the config file, the evidence chain key in the OS keychain, and the chain head file. This also removes migration backups, the exclusion list and benchmark records. Leaves your audio files untouched. Before it runs, it warns that render files written elsewhere with `--out` and any exports you wrote must be deleted by you, and that Claude Code's transcripts are outside Headphones' reach. Deny rules installed into Claude Code settings by `init --claude-permissions` and the weights directory are left in place. |
| `headphones cache prune` | Removes stems and feature arrays. Evaluation records, ear judgments and everything else stay (REQ-SEP-03). |

Because values are append-only (REQ-STORE-04), `forget` is the only way anything is hard-deleted.

## Retention

Nothing expires automatically except the following.

| Data | Rule | SPEC |
|---|---|---|
| Logs | Rotated, 30 days kept by default | REQ-SEC-07 |
| Stems, then feature arrays | Evicted least-recently-used once the cache passes its size limit (20 GB by default) | REQ-CACHE-02 |
| Migration backups | Deleted once the migration is confirmed | REQ-STORE-06 |

Evaluation records are never evicted (REQ-CACHE-02). Superseded values, ear judgments, stated preferences, history, AcoustID results and calibration events stay until you run `forget`. Ear requests can become `expired`, but SPEC does not set when expired requests are deleted, so they stay until `forget`.

## Diagnostics are redacted by default

`headphones doctor` reports what is needed to reproduce a run elsewhere, without the audio. By default it redacts paths, device labels and asset identity (REQ-OBS-03). `--unredacted` shows them. Use the default output, for example `headphones doctor --json`, when you attach diagnostics to a public issue. `doctor` also warns when debug logs exist, since those may contain paths (REQ-SEC-07), and verifies the evidence chain (REQ-STORE-09).

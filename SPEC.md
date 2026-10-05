# Headphones Technical Specification

| Field | Value |
|---|---|
| Document | SPEC.md |
| Version | 0.1.0-draft |
| Status | Draft for review |
| Date | 2026-10-05 |
| Editors | Project maintainers (see [MAINTAINERS.md](MAINTAINERS.md)) |
| Companion documents | [METRICS.md](METRICS.md) (normative), [schemas/evaluation-record.schema.json](schemas/evaluation-record.schema.json) (normative), [docs/evaluation-plan.md](docs/evaluation-plan.md) (normative for validation), [docs/security-self-assessment.md](docs/security-self-assessment.md) (informative) |

## 0. Conventions

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL are to be read as described in BCP 14 ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals.

Requirements carry stable identifiers of the form `REQ-<AREA>-<NN>`. Identifiers are never reused. A removed requirement is marked *Withdrawn* and keeps its number.

Sections marked *(informative)* contain no requirements.

## 1. Introduction *(informative)*

### 1.1 Problem

A language model without ears reasons about a record from text written about it. Most of what makes a record land for a particular listener is never written down: where the drummer sits against the beat, whether the hi-hat is chopped or open, how long a note rings, whether the vocal is stacked, the half-second of nothing before the chorus. The project's listener has catalogued 35 such properties (the metric catalog in [METRICS.md](METRICS.md)) and a two-part profile (BUILD and FEEL tests) built on them. Until now every score against that profile has been an inference from reviews.

### 1.2 Mission

Give Claude Code a measured, inspectable, honest account of how a recording sounds, and give the listener a fast way to record what only their ears can judge, so that the two can be compared, calibrated, and used together.

### 1.3 What success looks like

1. For a track the listener owns, Claude can answer "does the snare sit behind the beat" with a number, a confidence, a plot it has looked at, and a statement of how that number was obtained.
2. Where the harness cannot know, it says so and asks the listener.
3. A pre-registered benchmark shows that Claude with the harness agrees with the listener's ear more often than Claude without it, metric by metric, or shows that it does not and the project reports that.

## 2. Scope

### 2.1 Goals

- G1. Compute the metrics in [METRICS.md](METRICS.md) from audio the listener owns.
- G2. Attach an evidence class, confidence, method identifier and provenance to every value.
- G3. Capture ear judgments and timestamped moments from the listener with sub-100 ms timing accuracy relative to the audio being played.
- G4. Expose results to Claude Code through a local MCP server, a skill, and rendered images.
- G5. Evaluate the existing BUILD and FEEL tests against audio.
- G6. Measure the harness's lift over a text-only baseline.
- G7. Run entirely on the listener's machine with no network dependency after models are installed.

### 2.2 Non-goals

- N1. Capturing, recording, downloading, caching or analyzing Spotify audio, or audio from any service whose terms forbid it.
- N2. Transcribing, analyzing, scoring or displaying lyrics. Vocal analysis is limited to acoustic properties (placement, breath, doubling, harmony count, proximity, timing). See [ADR-0004](docs/adr/0004-no-lyrics.md).
- N3. Training or fine-tuning any model on Spotify content, Spotify metadata, or Spotify-derived data.
- N4. Recommendation generation. Headphones measures. Recommending stays with the music profile skill, which may consume Headphones output.
- N5. A hosted or multi-tenant service. Headphones is single-user software.
- N6. Replacing the listener's judgment. EAR evidence decides preference questions (§5.3).
- N7. Genre classification. The profile judges production, not genre.

## 3. Actors and use cases *(informative)*

### 3.1 Actors

| Actor | Description |
|---|---|
| Listener | The single human user. Owns the audio library, provides ear judgments, is the ground truth for preference. |
| Agent | Claude Code, operating through the MCP server and skill. Can request analysis, read results, view renders, request ear judgments. Cannot create EAR evidence. |
| Maintainer | Person with commit rights. See [GOVERNANCE.md](GOVERNANCE.md). |
| Contributor | Anyone who proposes a change. |
| Official Spotify connector | The Spotify integration the listener has authorized inside Claude, governed by its own terms. Out of the harness's trust boundary. |

### 3.2 Use cases

- **UC-1 Adjudicate.** Listener asks "score *Inside Out* by Spoon against BUILD and FEEL". Agent resolves the track to an owned file, runs analysis if missing, reports each criterion with evidence class, timestamps and what the listener should verify by ear.
- **UC-2 Listening session.** Listener plays a track on the listening station, taps a key at a chill, at the moment their head starts moving, and at anything else worth marking, then answers a short ear form. Taps and answers become EAR evidence.
- **UC-3 Measure one property.** "Is the vocal on *Wet Sand* double-tracked?" Agent runs the doubling analyzer, shows a render, reports the result and confidence.
- **UC-4 Compare.** "Which of these three records has the driest drums?"
- **UC-5 Calibrate.** Listener scores a batch by ear. The harness reports agreement per metric and flags analyzers that disagree with the listener more than their declared accuracy allows.
- **UC-6 Control group.** Listener scores twenty records they dislike against FEEL. Harness runs the same detectors. Results answer whether FEEL is specific to the listener. (This is the profile's own pending experiment.)
- **UC-7 Benchmark.** Run the harness-versus-baseline evaluation in [docs/evaluation-plan.md](docs/evaluation-plan.md).
- **UC-8 History.** Listener imports their Spotify extended streaming history (their own data export) so behavioral metrics such as replays and skips can be computed.

## 4. Terminology

| Term | Meaning |
|---|---|
| Audio asset | One audio file in the local library, identified by the SHA-256 of its bytes (`asset_id`). |
| Recording | A distinct performance as identified by a MusicBrainz recording MBID. Several assets may share a recording (different masters, formats). |
| Stem | A separated source signal (drums, bass, vocals, guitar, piano, other) produced from an asset by the separator. |
| Beat grid | The sequence of beat and downbeat times produced for an asset (§7.3.3). |
| Analyzer | A versioned unit of code that produces one or more metric values from an asset and upstream artifacts. |
| Metric | A property in [METRICS.md](METRICS.md), with a stable ID such as `groove.pocket`. |
| Value | One result for one metric on one asset, with evidence class, confidence and provenance. |
| Evaluation record | The stored, schema-valid set of values for one asset at one point in time. |
| Ear judgment | A value entered by the listener through the listening station. |
| Tap | A timestamped key-press during playback. |
| Render | An image generated from analysis data for human or agent viewing. |

## 5. Evidence model

### 5.1 Evidence classes

Every value MUST carry exactly one evidence class.

| Class | Meaning | Example |
|---|---|---|
| `MEASURED` | Computed directly from the audio signal by a method whose accuracy on the validation suite meets the metric's stable threshold. | Integrated loudness, stereo correlation, track length, fade duration. |
| `ESTIMATED` | Computed from the audio by a model or heuristic, with a known but larger error, or depending on stem separation. | Snare onset offsets from a separated drum stem. Harmony voice count. |
| `PROXY` | A measurable signal believed to correlate with a perceptual property that cannot itself be measured. Never a claim about the property. | Time until a stable pulse is established, offered as a proxy for the head-nod test. |
| `EAR` | Entered by the listener through a human input event on the listening station. | "Head nod: yes, at about 6 s." A tap at 2:14.6. |
| `BEHAVIORAL` | Derived from the listener's own listening history. | Replayed within one hour on 4 of 9 plays. |
| `STATED` | Something the listener has said about their taste, recorded verbatim with date. | "100 to 126 BPM." |
| `TEXTUAL` | From written sources about the record. | A review says the album was recorded live to tape. |

- **REQ-EVID-01** A value MUST be labeled `MEASURED` only when the producing analyzer's maturity for that metric is `stable` (§11.3). Otherwise the strongest permitted label is `ESTIMATED`.
- **REQ-EVID-02** A `PROXY` value MUST name, in its `proxy_for` field, the metric it stands in for, and MUST NOT be reported by the agent as a value of that metric.
- **REQ-EVID-03** `EAR` evidence MUST originate from a human input event on the listening station (§7.4). No API, MCP tool, import path or CLI flag other than the listening station's interactive capture may create `EAR` evidence. Bulk import of past ear judgments is permitted only through `headphones ear import`, which MUST require interactive confirmation per file and MUST mark imported values with `capture_method: "import"`.
- **REQ-EVID-04** `STATED` evidence MUST be stored verbatim with the date and context it was given and MUST NOT be rewritten into a rule. (This carries the profile's "record what he says, not a tidied version" rule into the data model.)
- **REQ-EVID-05** Every value MUST carry a `confidence` in the closed interval 0 to 1, defined per metric in [METRICS.md](METRICS.md). For `EAR`, `STATED` and `BEHAVIORAL` values the confidence field records the listener's own certainty where given and is otherwise null.

### 5.2 Abstention

- **REQ-EVID-06** An analyzer MUST return `status: "abstained"` with a machine-readable `reason` instead of a value when its preconditions fail (for example, no drums detected for a groove metric, or separation quality below the metric's floor). An abstention is a valid result and MUST be shown to the agent as such.
- **REQ-EVID-07** An analyzer MUST NOT substitute a default or genre-typical value for a missing measurement.

### 5.3 Precedence

Measurement and judgment answer different questions. The rules below keep them from overwriting each other.

- **REQ-EVID-08** For questions of preference and felt experience (does it work for the listener, did it give chills, does the head move), `EAR` evidence takes precedence over every other class.
- **REQ-EVID-09** For questions of physical fact (how wide is the mix, how long is the fade), a `MEASURED` value is reported as measured even when an `EAR` value differs. The disagreement MUST be recorded as a calibration event (§11.5), not resolved by discarding either value.
- **REQ-EVID-10** Where both apply, the agent MUST present both and say which question each answers.
- **REQ-EVID-11** Below `EAR` for preference questions, the order of trust is `BEHAVIORAL`, `MEASURED`, `ESTIMATED`, `STATED`, `PROXY`, `TEXTUAL`. Plays outrank saves, matching the profile's evidence base.

### 5.4 Agent reporting rules

These are enforced by the skill (§7.6.2) and checked by the benchmark (§12).

- **REQ-EVID-12** When the agent states a metric value it MUST name its evidence class in words a listener understands ("measured", "estimated from the separated drum track", "a proxy", "your ear", "your play history", "you said", "from reviews").
- **REQ-EVID-13** When the agent has only `PROXY` or `TEXTUAL` support for a felt-experience claim it MUST say the listener should check by ear and SHOULD offer a timestamp to listen at.
- **REQ-EVID-14** The agent MUST NOT invent timestamps. Every timestamp it gives MUST come from a stored value, a render, or a tap.

## 6. Legal and sourcing constraints

This section is normative. It reflects the project's reading of third-party terms as of the date above. It is not legal advice. The project MUST re-check the referenced terms at every minor release (§15.4).

### 6.1 Audio sources

- **REQ-SRC-01** The harness MUST analyze only audio assets the listener has placed in the local library. It MUST NOT fetch audio from any network service.
- **REQ-SRC-02** The harness MUST NOT capture, record, loop back, or intercept audio from Spotify or any other streaming client. It MUST NOT include, document or link to tooling that does so.
- **REQ-SRC-03** On ingest the harness MUST refuse files that carry DRM it cannot decode. It MUST NOT include or invoke DRM circumvention.
- **REQ-SRC-04** The library ingest step SHOULD record an optional, listener-supplied `source` label per asset (for example `bandcamp`, `qobuz`, `cd-rip`, `other`). The harness does not and cannot verify this label. It exists so the listener can audit their own library.
- Recommended sources, in order: DRM-free purchases (Bandcamp, Qobuz, 7digital, HDtracks, artist stores), then copies the listener has made of physical media they own where local law permits. Private copying rules differ by country. The listener is responsible for the legality of their own library. See [ADR-0001](docs/adr/0001-owned-audio-only.md).

### 6.2 Spotify

The Spotify Developer Policy (sections III.13 and III.14 at the time of writing) forbids analyzing Spotify content and forbids ingesting Spotify content into a machine learning or AI model. The February 2026 Web API changes removed `external_ids` (ISRC) and `popularity` from track objects and removed several endpoints. See [ADR-0002](docs/adr/0002-spotify-boundary.md).

- **REQ-SPOT-01** Headphones MUST NOT include its own Spotify Web API client in any release. Spotify data reaches the agent only through the official Spotify connector the listener has authorized in Claude, under that connector's own terms.
- **REQ-SPOT-02** Headphones MUST NOT store responses obtained from the Spotify Web API or the Spotify connector, except a Spotify track URI that the listener has explicitly linked to an asset (§7.2.3). A URI is stored as an opaque string and is never dereferenced by Headphones code.
- **REQ-SPOT-03** Headphones MAY import the listener's Spotify extended streaming history, which the listener requests from Spotify as their own personal data. Import MUST be explicit, MUST be local, and MUST be deletable as a unit (see [docs/privacy.md](docs/privacy.md)).
- **REQ-SPOT-04** Whether the extended streaming history is "Spotify Content" under the Developer Policy is an open question (§17, OI-1). Until it is resolved, `BEHAVIORAL` metrics MUST be disabled by default and enabled only by explicit listener configuration with a notice that names this question.

### 6.3 Model and dependency licenses

- **REQ-LIC-01** Every runtime dependency and every model weight file MUST have a license on the allowlist in [ADR-0003](docs/adr/0003-dependency-and-model-licenses.md). Additions require an ADR amendment.
- **REQ-LIC-02** Weights whose license forbids commercial use MAY be supported only as an optional, separately installed plugin that is off by default and labeled as such. The core distribution MUST NOT depend on them.
- **REQ-LIC-03** The project MUST publish an SBOM in SPDX 2.3 or CycloneDX 1.5 format with every release, covering Python packages, native libraries and model weights with their hashes and licenses.

## 7. Architecture

### 7.1 Overview

```
                    +-------------------------------------------------+
  Listener          |                 Listener's machine              |
  (keyboard,        |                                                 |
   headphones)      |  +-----------------+       +------------------+ |
      |             |  | Listening       | taps  | Evidence Store   | |
      +------------>|  | Station (mpv)   |------>| SQLite + CAS     | |
                    |  +-----------------+       +------------------+ |
                    |          ^                     ^      ^         |
                    |          | play                |      |         |
                    |  +-----------------+   values  |      |         |
                    |  | Analysis Engine |-----------+      |         |
                    |  | (DAG of         |                  |         |
                    |  |  analyzers)     |<---+             |         |
                    |  +-----------------+    |             |         |
                    |          ^              |             |         |
                    |          | assets       | requests    | reads   |
                    |  +-----------------+  +------------------+      |
                    |  | Library, Ingest |  | MCP Server       |      |
                    |  | Identity        |  | (stdio only)     |      |
                    |  +-----------------+  +------------------+      |
                    |          ^                     ^                |
                    |   owned audio files            | stdio          |
                    |                         +------------------+    |
                    |                         | Claude Code      |    |
                    |                         | + Headphones     |    |
                    |                         |   skill          |    |
                    |                         +------------------+    |
                    +-------------------------------------------------+
                                                     |
                               official Spotify connector (separate,
                               governed by its own terms, not part
                               of Headphones)
```

Implementation language: Python 3.12 or later. Packaging: a single Python distribution `headphones` installed with `uv` or `pip`. Native dependencies: FFmpeg 6 or later, mpv 0.37 or later, Chromaprint `fpcalc`.

### 7.2 Library, ingest and identity

#### 7.2.1 Ingest

- **REQ-ING-01** `headphones library add <path>` MUST scan files and directories for audio in FLAC, WAV, AIFF, ALAC, MP3, AAC/M4A, Ogg Vorbis and Opus.
- **REQ-ING-02** Decoding MUST be performed by FFmpeg in a child process with resource limits (§10.4) and MUST NOT occur in the MCP server process.
- **REQ-ING-03** Each asset MUST be identified by `asset_id`, the lowercase hex SHA-256 of the file bytes. Renaming or moving a file MUST NOT change its identity. Re-tagging a file changes its bytes and therefore its `asset_id`. The library MUST detect this case by matching the decoded-audio hash (`pcm_sha256`, SHA-256 of the decoded 32-bit float PCM at the native sample rate) and MUST carry existing evaluations across when `pcm_sha256` matches.
- **REQ-ING-04** Ingest MUST record sample rate, bit depth where defined, channel count, duration, codec, and whether the file is lossy.
- **REQ-ING-05** Mono assets MUST be accepted. Metrics that need two channels MUST abstain with reason `mono_source`.
- **REQ-ING-06** Assets longer than 20 minutes MUST be accepted for library purposes, and analysis MUST either process them in windows or abstain with reason `too_long`. The limit is configurable.

#### 7.2.2 Identity resolution

Spotify no longer exposes ISRC, so identity comes from the audio itself and from open metadata.

- **REQ-ID-01** The harness MUST compute a Chromaprint fingerprint for every asset.
- **REQ-ID-02** The harness MAY look up the fingerprint on AcoustID to obtain MusicBrainz recording MBIDs. This lookup is the only network call in normal operation. It MUST be disableable (`identity.online = false`) and MUST send only the fingerprint and duration, never file names, paths or tags.
- **REQ-ID-03** Where the lookup is disabled or fails, identity MUST fall back to embedded tags (artist, title, album, MusicBrainz IDs if present) and MUST be marked `identity_confidence: "tags_only"`.
- **REQ-ID-04** Metadata fetched from MusicBrainz MUST be limited to the CC0-licensed core data (recording, release, artist, ISRC, length).

#### 7.2.3 Linking to Spotify

- **REQ-ID-05** The listener MAY link an asset to a Spotify track URI by pasting it into `headphones link <asset> <uri>`, or by confirming a match that the agent proposes after it has looked the track up through the official Spotify connector. Linking MUST require listener confirmation.
- **REQ-ID-06** Different masters matter. The harness MUST NOT assume a linked Spotify track uses the same master as the owned asset, and MUST tell the agent that values describe the owned asset.

### 7.3 Analysis engine

#### 7.3.1 Pipeline

Analysis is a directed acyclic graph of stages. Each stage reads artifacts from the content-addressed store and writes new ones.

```
decode -> resample(44.1k, float32) -> loudness
       \-> separate(stems) -> per-stem onsets -> drum transcription
       \-> beat & downbeat grid ----------------^       |
       \-> structure segmentation <-- stem activity <---+
       \-> pitch tracks (bass f0, vocal f0, polyphonic notes)
                         |
                         v
                metric analyzers -> composites (BUILD, FEEL) -> evaluation record
```

- **REQ-ENG-01** Every stage and analyzer MUST declare a name, a semantic version, its inputs, its outputs, and the model weights it uses with their SHA-256 hashes.
- **REQ-ENG-02** An artifact's cache key MUST be the hash of its inputs' cache keys, the stage version, and the stage's effective configuration. A change to any of these MUST invalidate downstream artifacts and no others.
- **REQ-ENG-03** The engine MUST resample to 44.1 kHz float32 for analysis while preserving the original channel layout. Analyzers that need the native rate (for example, true-peak) MUST read the decoded original.
- **REQ-ENG-04** A failing analyzer MUST NOT fail the whole run. Its metrics MUST be recorded with `status: "error"` and an error code, and the run MUST continue.

#### 7.3.2 Source separation

- **REQ-SEP-01** The reference separator is Demucs `htdemucs_6s` (MIT license), producing drums, bass, vocals, guitar, piano and other. The separator is pluggable through the stage contract.
- **REQ-SEP-02** The engine MUST compute a separation quality estimate per stem. The reference estimate is the residual ratio: energy of (mix minus sum of stems) relative to mix energy, plus per-stem leakage estimated from cross-stem onset coincidence. Metrics that depend on a stem MUST declare a floor and abstain below it.
- **REQ-SEP-03** Stems MUST be cached and MUST be deletable with `headphones cache prune`. Stems are derived copies of copyrighted audio and MUST NOT leave the machine through any Headphones interface. The MCP server MUST NOT return stem audio.

#### 7.3.3 Beat grid

- **REQ-BEAT-01** The reference beat and downbeat tracker is `beat_this` (MIT license, code and weights). Alternatives are pluggable.
- **REQ-BEAT-02** The grid MUST be represented as beat times and downbeat flags, not a single tempo, so that tempo drift in hand-played music is preserved.
- **REQ-BEAT-03** Microtiming analyzers MUST NOT measure against the raw tracker output, which already leans toward whatever the instruments do. They MUST measure against a *reference pulse*: a smoothed local fit (default: local linear regression over a window of 8 beats) of the consensus onset times of all available rhythmic stems. METRICS.md §2.3 defines it exactly.

#### 7.3.4 Other shared primitives

Shared primitives (onsets, drum transcription, pitch tracking, loudness, structure, stem activity) are specified in [METRICS.md](METRICS.md) §2 so that each metric refers to one definition.

### 7.4 Listening station

The listening station is where the listener hears the asset and where all `EAR` evidence is born.

- **REQ-LS-01** Playback MUST use mpv controlled over its JSON IPC socket. The station MUST record tap times using mpv's reported `audio-pts` at the moment of the key event, corrected by a measured output latency (§7.4.1).
- **REQ-LS-02** Tap timing accuracy MUST be within 100 ms of the audio actually heard at the listener's ears, at the 95th percentile, after latency calibration. Bluetooth output MUST trigger a warning that latency may vary.
- **REQ-LS-03** The station MUST offer a terminal interface (`headphones listen <track>`). A local browser interface MAY be added and, if added, MUST bind to 127.0.0.1 only and require a per-session token.
- **REQ-LS-04** Default tap keys: `c` chill, `n` head starts moving, `h` hook lands, `m` kept mistake, `space` generic mark, `u` undo last tap. Bindings are configurable.
- **REQ-LS-05** After playback, or on request, the station MUST present the ear form for the metrics the listener has chosen (default: the ear-only and ear-primary metrics in METRICS.md), with the scale defined per metric. Every field MUST allow "not sure" and "skip".
- **REQ-LS-06** The station MUST NOT play audio files outside the library.
- **REQ-LS-07** Loudness: the station MUST offer playback normalized to -14 LUFS integrated (default on) so that comparisons between tracks are not skewed by mastering level, and MUST record which mode was used with every ear judgment.

#### 7.4.1 Latency calibration

- **REQ-LS-08** `headphones listen --calibrate` MUST play a click train at 100 BPM for at least 16 clicks and ask the listener to tap along. The median offset becomes the per-device latency correction. The interquartile range is stored and shown with every tap captured on that device.

#### 7.4.2 Spotify companion mode

When the listener hears a track on Spotify instead of the station, they may still mark moments.

- **REQ-LS-09** In companion mode, the agent MAY read the playback position through the official Spotify connector when the listener says "mark". The resulting value is `EAR` evidence for the existence of the moment but MUST carry `capture_method: "companion"` and a timing uncertainty of at least ±2 s, and MUST be tied to the Spotify URI, not to an asset, unless the listener has linked the two.
- **REQ-LS-10** Companion-mode timestamps MUST NOT be used to validate analyzer timing (§11), because master and timing may differ from the owned asset.

### 7.5 Evidence store

- **REQ-STORE-01** Structured data MUST be stored in a single SQLite database under the data directory (default: the platform user-data directory, for example `~/.local/share/headphones` on Linux).
- **REQ-STORE-02** Large artifacts (stems, feature arrays, renders) MUST be stored in a content-addressed directory keyed by SHA-256.
- **REQ-STORE-03** Evaluation records MUST be exportable as JSON that validates against [schemas/evaluation-record.schema.json](schemas/evaluation-record.schema.json).
- **REQ-STORE-04** Values are append-only. A re-analysis creates new values and marks earlier ones `superseded_by`. Ear judgments are never superseded by analysis, only by a later ear judgment from the listener.
- **REQ-STORE-05** The store MUST support `headphones export` (all records, JSON Lines) and `headphones forget <asset|all>` (removal including cache) as described in [docs/privacy.md](docs/privacy.md).
- **REQ-STORE-06** Database migrations MUST be versioned and reversible for at least one minor version.

### 7.6 Claude Code integration

#### 7.6.1 MCP server

- **REQ-MCP-01** The MCP server MUST use the stdio transport only. It MUST NOT open a network listener.
- **REQ-MCP-02** The server MUST expose the tools below and no tool that writes `EAR` or `STATED` evidence. (`STATED` evidence is entered by the listener with `headphones stated add`.)
- **REQ-MCP-03** Every tool result that includes text derived from file tags or MusicBrainz MUST wrap that text in a clearly delimited `untrusted_metadata` field. The skill instructs the agent to treat it as data, never instructions (§13).
- **REQ-MCP-04** Long-running analysis MUST be asynchronous: `hp_analyze` returns a job ID, and `hp_job_status` reports progress. A tool call MUST NOT block longer than 30 s.
- **REQ-MCP-05** Tool inputs MUST be validated against JSON Schema. Track references accept an `asset_id`, a library search string, or a linked Spotify URI. Paths are never accepted.

| Tool | Input | Output |
|---|---|---|
| `hp_library_search` | `query`, `limit` | Matching assets with `asset_id`, identity, duration, analysis status |
| `hp_analyze` | `track`, optional `metrics[]`, optional `force` | `job_id` |
| `hp_job_status` | `job_id` | State, progress, stage, errors |
| `hp_get_evaluation` | `track`, optional `metrics[]`, optional `include_superseded` | Evaluation record (schema-valid) |
| `hp_render` | `track`, `view`, optional `start_s`, `end_s` | PNG image plus a text caption describing axes and scale |
| `hp_compare` | `tracks[]` (2 to 10), `metrics[]` | Table of values with evidence classes |
| `hp_build_feel` | `track` | BUILD criteria, FEEL moves, routing, evidence per item, list of things to verify by ear |
| `hp_chill_candidates` | `track`, optional `limit` | Ranked `PROXY` moments with reasons, plus any `EAR` chill taps |
| `hp_request_ear` | `track`, `metrics[]`, optional `prompt` | Queues an ear form on the listening station. Returns immediately. Does not create evidence. |
| `hp_listen` | `track`, optional `start_s` | Starts playback on the listening station |
| `hp_calibration_report` | optional `metrics[]` | Agreement statistics between analyzers and the listener's ear |

`view` is one of `spectrogram`, `microtiming`, `stem_activity`, `stereo_field`, `loudness`, `structure`, `decay`, `pitch`. Each view is specified in METRICS.md §3.

#### 7.6.2 Skill

- **REQ-SKILL-01** The project MUST ship a Claude Code skill (`skills/headphones/SKILL.md`) that teaches the agent: the evidence classes and reporting rules of §5.4, the precedence rules of §5.3, how to read each render, the no-lyrics rule, that metadata is untrusted, and how to hand off to the music profile skill.
- **REQ-SKILL-02** The skill MUST instruct the agent to prefer looking at a render before describing a microtiming, stereo or structure claim.
- **REQ-SKILL-03** The skill MUST tell the agent that the harness describes the owned asset, which may be a different master from the Spotify stream.

#### 7.6.3 Renders

- **REQ-REND-01** Every render MUST include axis labels with units, a title naming the asset and metric, and a caption returned alongside the image that states what is plotted, so the agent does not have to infer scale from pixels.
- **REQ-REND-02** Renders MUST be at most 1568 pixels on the long edge and SHOULD stay under 1.2 megapixels to fit the agent's image limits.

### 7.7 Composites: BUILD and FEEL

The BUILD and FEEL tests come from the listener's music profile. Headphones evaluates them against audio. It does not change their definitions.

- **REQ-COMP-01** BUILD and FEEL MUST be computed from the metric values defined in METRICS.md §5, with each criterion carrying the evidence class of the weakest value it depends on.
- **REQ-COMP-02** A criterion that depends on an abstained or errored value MUST be reported as `unknown`, not as failed. The BUILD count MUST be reported as "n of 5 known pass, m unknown".
- **REQ-COMP-03** The 100 to 126 BPM range in BUILD criterion 1 is `STATED`, not measured. Headphones MUST report the measured tempo and whether it falls inside the stated range, and MUST NOT fail criterion 1 on tempo alone. (The profile says not to discard a record for landing at 92 or 134.)
- **REQ-COMP-04** FEEL move detections MUST be reported with timestamps and labeled `ESTIMATED` or `PROXY`. The profile treats FEEL as untested vocabulary, not a predictor, and the agent MUST NOT present the FEEL count as a prediction of chills unless validation (§11) supports it.
- **REQ-COMP-05** Routing (anchor, rotation, resonance, skip) MUST be computed only from known criteria, MUST state how many criteria were unknown, and is advisory.

## 8. Interfaces

### 8.1 Command line

| Command | Purpose |
|---|---|
| `headphones init` | Create data directory and config, check native dependencies, download pinned model weights with hash verification |
| `headphones doctor` | Report dependency versions, model hashes, device latency calibration, disk use |
| `headphones library add <path>` / `list` / `remove <asset>` | Manage the library |
| `headphones link <asset> <spotify-uri>` | Link an asset to a Spotify URI |
| `headphones analyze <track> [--metrics ...] [--force]` | Run analysis |
| `headphones show <track> [--metrics ...] [--json]` | Print an evaluation |
| `headphones render <track> <view>` | Write a render to a file |
| `headphones listen <track>` / `--calibrate` | Listening station |
| `headphones ear import <file>` | Interactive import of past ear judgments |
| `headphones stated add` / `list` | Record and list stated preferences, verbatim |
| `headphones history import <spotify-export-dir>` | Import extended streaming history (off unless enabled, see REQ-SPOT-04) |
| `headphones calibrate report` | Analyzer versus ear agreement |
| `headphones bench run <plan>` | Run the evaluation benchmark |
| `headphones export` / `forget` / `cache prune` | Data portability and removal |
| `headphones mcp` | Run the MCP server on stdio |

- **REQ-CLI-01** Every command that prints results MUST support `--json` output that validates against a published schema.
- **REQ-CLI-02** Exit codes: 0 success, 1 usage error, 2 partial success (some metrics errored or abstained where the caller required them), 3 dependency missing, 4 data error, 5 internal error.

### 8.2 Analyzer plugin contract

Analyzers are Python entry points in the group `headphones.analyzers`.

```python
class Analyzer(Protocol):
    name: str                      # e.g. "groove.pocket.v1"
    version: str                   # SemVer of the method
    metrics: tuple[str, ...]       # metric IDs produced
    requires: tuple[str, ...]      # artifact types needed, e.g. ("stems", "beat_grid")
    weights: tuple[WeightRef, ...] # name, url, sha256, license

    def analyze(self, ctx: AnalysisContext) -> list[MetricResult]: ...
```

- **REQ-PLUG-01** `analyze` MUST be a pure function of the artifacts in `ctx` and the analyzer's configuration. It MUST NOT perform network I/O, read files outside `ctx`, or write outside its scratch directory.
- **REQ-PLUG-02** Each result MUST validate against the `value` definition in the schema.
- **REQ-PLUG-03** Third-party analyzers MUST be enabled explicitly by name in configuration. Installing a package that registers an entry point MUST NOT activate it.

### 8.3 Configuration

A single TOML file at the platform config directory (for example `~/.config/headphones/config.toml`). Unknown keys MUST cause a warning. Every threshold used to map a measurement to a category in METRICS.md MUST be configurable, and the active thresholds MUST be recorded in each evaluation record's `config_digest` and `thresholds` fields.

## 9. Data model

The normative schema is [schemas/evaluation-record.schema.json](schemas/evaluation-record.schema.json) (JSON Schema draft 2020-12). An example is in [schemas/examples/](schemas/examples/).

An evaluation record contains:

- `schema_version`, `record_id` (UUIDv7), `created_at` (RFC 3339 UTC)
- `asset`: `asset_id`, `pcm_sha256`, duration, sample rate, channels, codec, lossy flag, optional `source` label, `identity` (MBIDs, ISRC from MusicBrainz, `identity_confidence`, optional linked Spotify URI)
- `engine`: Headphones version, platform, `config_digest`, `thresholds`, and the list of stages and analyzers with versions and weight hashes
- `separation_quality`: per-stem estimates
- `values[]`: one entry per metric result
- `composites`: BUILD and FEEL

Each entry in `values[]` contains `metric_id`, `status` (`ok`, `abstained`, `error`), `evidence_class`, `confidence`, `value` (typed per metric), optional `category`, optional `timestamps[]`, optional `proxy_for`, `method` (analyzer name and version), and, for `EAR` values, `capture` (method, device, latency correction, normalization mode, captured_at).

- **REQ-DATA-01** The schema version follows SemVer independently of the software version (§15.2).
- **REQ-DATA-02** Readers MUST ignore unknown fields in a record whose major schema version they support.

## 10. Processing requirements

### 10.1 Determinism

- **REQ-DET-01** Given the same asset, configuration, software version, and model weights, analysis on the same platform MUST produce identical categorical outputs and numeric outputs within the tolerance declared per metric.
- **REQ-DET-02** All randomness (for example, Demucs shift augmentation) MUST be seeded from the asset's `pcm_sha256`. The default separator configuration MUST disable random shifts.
- **REQ-DET-03** Cross-platform (CPU versus GPU, different BLAS) differences MUST stay within the declared tolerance. The conformance suite (§11.2) runs on at least Linux x86_64 CPU and one GPU backend.

### 10.2 Performance targets *(informative service levels)*

On the reference machine (8-core x86_64 CPU, 16 GB RAM, no GPU), for a 4-minute stereo track:

| Stage | Target |
|---|---|
| Ingest and fingerprint | under 5 s |
| Separation (htdemucs_6s, CPU) | under 6 min |
| All analyzers after separation | under 90 s |
| `hp_get_evaluation` on a cached record | under 300 ms |

With a supported GPU, total analysis SHOULD finish in under 90 s. These are targets for the roadmap, not conformance requirements.

### 10.3 Caching

- **REQ-CACHE-01** Re-requesting analysis with unchanged inputs MUST return cached results without recomputation.
- **REQ-CACHE-02** The cache MUST have a configurable size limit (default 20 GB) with least-recently-used eviction of stems first, then feature arrays. Evaluation records are never evicted.

### 10.4 Resource limits

- **REQ-RES-01** Decoder and analyzer child processes MUST run with a memory limit (default 8 GB), a CPU time limit proportional to asset duration, and no network access where the platform allows it.
- **REQ-RES-02** Concurrent analysis jobs default to one. The listening station MUST remain responsive while analysis runs.

## 11. Validation and quality

### 11.1 Principle

No metric is trusted because its algorithm sounds right. Each analyzer earns its evidence class through measured accuracy against known answers. [docs/evaluation-plan.md](docs/evaluation-plan.md) is normative for the procedures.

### 11.2 Conformance suite

- **REQ-VAL-01** The project MUST maintain a synthetic conformance corpus generated by code in the repository: multitrack audio rendered from MIDI and sample sets with permissive licenses, with exactly known ground truth (pan positions, onset offsets in ms, ghost-note velocities, fade shapes, reverb times, double-tracking, harmony counts, silence gaps, compression settings).
- **REQ-VAL-02** Every analyzer MUST have conformance tests with declared accuracy targets for each metric it produces. CI MUST run the suite on every change to an analyzer, stage or weight file.
- **REQ-VAL-03** Synthetic audio is cleaner than real records. Passing the synthetic suite is necessary but not sufficient for `stable`.

### 11.3 Metric maturity

| Level | Entry criteria | Effect |
|---|---|---|
| `experimental` | Analyzer exists and passes unit tests. | Values hidden from the agent unless requested by metric ID. Max class `PROXY` or `ESTIMATED`. |
| `beta` | Meets synthetic accuracy target. Validated on at least 30 real tracks against listener ear judgments with agreement reported. | Shown to the agent. Max class `ESTIMATED`. |
| `stable` | Meets synthetic target and the real-track agreement threshold in METRICS.md for two consecutive minor releases. No open correctness bugs. | May be labeled `MEASURED` if the metric is classed measurable in METRICS.md. |

- **REQ-VAL-04** Maturity is recorded per metric per analyzer version in `metrics-maturity.toml` in the repository and changes only through a reviewed pull request that links the validation report.
- **REQ-VAL-05** A metric whose ceiling class in METRICS.md is `PROXY` or `EAR` can never be labeled `MEASURED`, whatever its maturity.

### 11.4 Regression

- **REQ-VAL-06** A golden set of at least 20 real tracks (owned by maintainers, never committed, referenced by `pcm_sha256`) MUST be re-run before each release. Any categorical change or numeric change beyond tolerance MUST be explained in the release notes.

### 11.5 Calibration events

- **REQ-VAL-07** When an `EAR` value and an analyzer value for the same metric and asset disagree beyond the metric's agreement band, the store MUST record a calibration event. `headphones calibrate report` MUST summarize them per metric with agreement statistics (METRICS.md §4).

## 12. Evaluation of harness lift

Summary of [docs/evaluation-plan.md](docs/evaluation-plan.md):

- Two arms on the same held-out tracks and the same questions: Claude Code without Headphones (text and connector access only) and Claude Code with Headphones.
- Ground truth is the listener's ear, captured blind on the listening station before either arm runs.
- Primary outcome: per-metric agreement with the ear. Secondary: calibration (does the agent's stated confidence match its hit rate), abstention honesty, rule compliance (§5.4), and the rate of invented timestamps.
- The plan, metrics and analysis are pre-registered in the repository before data collection.

## 13. Security and privacy summary

The full analysis is in [docs/security-self-assessment.md](docs/security-self-assessment.md) and [docs/privacy.md](docs/privacy.md). Key requirements:

- **REQ-SEC-01** No network listeners in any component (MCP stdio only, optional browser UI on loopback with token).
- **REQ-SEC-02** Text from tags, file names and MusicBrainz is untrusted and delimited (REQ-MCP-03).
- **REQ-SEC-03** Model weights MUST be fetched over HTTPS, verified by SHA-256 before use, and loaded with safe loaders (`safetensors` where available, otherwise `torch.load(weights_only=True)`). Weights that cannot be loaded safely MUST NOT be supported.
- **REQ-SEC-04** Media decoding happens in a resource-limited child process (REQ-ING-02).
- **REQ-SEC-05** No telemetry. No crash reporting that leaves the machine.
- **REQ-SEC-06** Releases MUST be signed (Sigstore keyless signing) and accompanied by SLSA provenance at level 2 or higher and an SBOM (REQ-LIC-03).

## 14. Observability

- **REQ-OBS-01** Every analysis run MUST produce a run manifest: inputs, stages executed or cached, timings, analyzer versions, weight hashes, warnings, errors.
- **REQ-OBS-02** Logs MUST be structured (JSON Lines) and written locally. Logs MUST NOT contain file paths at default verbosity, only `asset_id`.
- **REQ-OBS-03** `headphones doctor` MUST report everything needed to reproduce a run on another machine except the audio itself.

## 15. Versioning, compatibility and release

### 15.1 Software

Semantic Versioning 2.0.0. Before 1.0.0, minor versions may break interfaces with a migration note.

### 15.2 Schema

The evaluation record schema has its own SemVer. Adding optional fields is minor. Removing or changing the meaning of a field is major.

### 15.3 Metric methods

Each analyzer has its own SemVer. A change that can alter outputs on the conformance or golden sets is at least a minor bump. A change of definition (what the metric means) requires a new metric ID or a METRICS.md major revision.

### 15.4 Release process

1. Conformance suite and golden set pass. Changes explained.
2. Third-party terms re-checked (§6) and the date recorded in the release notes.
3. SBOM generated, licenses checked against ADR-0003.
4. Artifacts signed, provenance attached.
5. Two-maintainer approval once the project has two maintainers (see GOVERNANCE.md).

### 15.5 Deprecation

A deprecated interface, metric ID or schema field MUST remain functional for at least two minor releases or six months, whichever is longer, with warnings.

## 16. Governance and project maturity

Governance is defined in [GOVERNANCE.md](GOVERNANCE.md). The project adapts the CNCF maturity levels (Sandbox, Incubating, Graduated) as internal milestones in [ROADMAP.md](ROADMAP.md). It is not a CNCF project and makes no claim to be one.

## 17. Open issues

| ID | Issue | Current handling |
|---|---|---|
| OI-1 | Whether the listener's own Spotify extended streaming history counts as Spotify Content under the Developer Policy when processed by tools that feed an AI agent. | BEHAVIORAL metrics off by default (REQ-SPOT-04). Seek clarification. |
| OI-2 | Whether data the official Spotify connector returns may be combined with Headphones output in the agent's context under that connector's terms. | Headphones never stores connector output except a listener-confirmed URI (REQ-SPOT-02). Re-check connector terms each release. |
| OI-3 | Drum transcription model with an allowlisted license and acceptable accuracy on real recordings. | Candidate evaluation in milestone M1. Ghost notes and hi-hat articulation stay `experimental` until resolved. |
| OI-4 | Whether separation artifacts bias microtiming by more than the perceptual threshold (about 10 ms). | Measured in the synthetic suite (METRICS.md §2.3). Pocket stays `ESTIMATED` until bounded. |
| OI-5 | Perceptual metrics (head-nod, hook stickiness, repeat urge, chill) may have no valid audio proxy. | Ceiling class `EAR` or `PROXY`. The benchmark reports whether proxies beat chance. |

## 18. References

- RFC 2119, RFC 8174: requirement levels.
- Spotify Developer Policy, https://developer.spotify.com/policy/ (sections III.13, III.14, checked 2026-10-05).
- Spotify Web API February 2026 migration guide, https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide (checked 2026-10-05).
- ITU-R BS.1770-5, EBU R 128: loudness measurement.
- Rouard, Massa, Défossez, "Hybrid Transformers for Music Source Separation" (Demucs v4), ICASSP 2023.
- Foscarin, Schlüter, Widmer, "Beat this! Accurate beat tracking without DBN postprocessing", ISMIR 2024.
- Bittner et al., "A Lightweight Instrument-Agnostic Model for Polyphonic Note Transcription and Multipitch Estimation" (Basic Pitch), ICASSP 2022.
- Kim et al., "CREPE: A Convolutional Representation for Pitch Estimation", ICASSP 2018.
- CNCF TAG Security, Security Self-Assessment template.
- CNCF project maturity levels, https://github.com/cncf/toc/tree/main/process.

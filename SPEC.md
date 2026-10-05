# Headphones Technical Specification

| Field | Value |
|---|---|
| Document | SPEC.md |
| Version | 0.2.0-draft |
| Status | Draft, revised after ten adversarial reviews ([docs/reviews/adversarial-reviews.md](docs/reviews/adversarial-reviews.md)) |
| Date | 2026-10-05 |
| Editors | Project maintainers (see [MAINTAINERS.md](MAINTAINERS.md)) |
| Normative companions | [METRICS.md](METRICS.md), [schemas/](schemas/), [docs/evaluation-plan.md](docs/evaluation-plan.md) |
| Informative companions | [docs/security-self-assessment.md](docs/security-self-assessment.md), [docs/privacy.md](docs/privacy.md) (its data inventory and Controls sections are normative for REQ-STORE-05), [docs/adr/](docs/adr/) |

## 0. Conventions

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL are to be read as described in BCP 14 ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals.

Requirements carry stable identifiers of the form `REQ-<AREA>-<NN>`. Identifiers are never reused. A removed requirement is marked *Withdrawn* with the reason and keeps its number.

Sections marked *(informative)* contain no requirements. Keywords in informative companion documents describe intent and are not conformance requirements unless SPEC.md repeats them.

### 0.1 Conformance

| Conformance class | What it is | Must satisfy |
|---|---|---|
| **Implementation** | A complete Headphones distribution | Every requirement in SPEC.md and METRICS.md |
| **Analyzer plugin** | Code registered under `headphones.analyzers` | §8.2, §5.1 to §5.2, REQ-ENG-01, REQ-DET-01 to 03, REQ-SEC-03, and the METRICS.md entry for each metric it produces |
| **Record producer** | Anything that writes evaluation records | §9 and the schemas, §5 |
| **Record consumer** | Anything that reads evaluation records | REQ-DATA-02, REQ-EVID-12 to 14 when presenting values to a person |
| **MCP server** | The `headphones mcp` process | §7.6, §5.4, §13 |

"Conformance suite" in §11.2 means the accuracy test corpus, not this clause.

### 0.2 Document versioning

SPEC.md, METRICS.md and each schema carry their own SemVer. A change that alters a requirement's meaning is a minor bump before 1.0 and a major bump after. Editorial fixes are patch bumps. Every change is listed in [CHANGELOG.md](CHANGELOG.md).

## 1. Introduction *(informative)*

### 1.1 Problem

A language model without ears reasons about a record from text written about it. Most of what makes a record land for a particular listener is never written down: where the drummer sits against the beat, whether the hi-hat is chopped or open, how long a note rings, whether the vocal is stacked, the half-second of nothing before the chorus. The project's listener has catalogued 35 such properties (the metric catalog in [METRICS.md](METRICS.md)) and a two-part profile (the BUILD and FEEL tests) built on them. Until now every score against that profile has been an inference from reviews.

### 1.2 Mission

Give Claude Code a measured, inspectable, honest account of how a recording sounds, and give the listener a fast way to record what only their ears can judge, so that the two can be compared, calibrated, and used together.

### 1.3 What success looks like

1. For a track the listener owns, Claude can answer "does the snare sit behind the beat" with a number, a confidence, a plot it has looked at, and a statement of how that number was obtained.
2. Where the harness cannot know, it says so and asks the listener.
3. A pre-registered benchmark shows that Claude with the harness agrees with the listener's ear more often than Claude without it, or shows that it does not, and the project reports either result.

## 2. Scope

### 2.1 Goals

- G1. Compute the metrics in METRICS.md from audio the listener owns.
- G2. Attach an evidence class, confidence, method identifier and provenance to every value.
- G3. Capture ear judgments and timestamped moments from the listener, with timing accuracy defined in REQ-LS-02.
- G4. Expose results to Claude Code through a local MCP server, a skill, and rendered images, packaged as a Claude Code plugin.
- G5. Evaluate the BUILD and FEEL tests against audio.
- G6. Measure the harness's lift over a text-only baseline.
- G7. Run entirely on the listener's machine. The only network traffic is model download and release signature verification at install or upgrade, and the optional, opt-in identity lookup (§7.2.2).

### 2.2 Non-goals

- N1. Capturing, recording, downloading, caching or analyzing Spotify audio, or audio from any service whose terms forbid it.
- N2. Transcribing, analyzing, scoring or displaying lyrics. Vocal analysis is limited to acoustic properties. See [ADR-0004](docs/adr/0004-no-lyrics.md).
- N3. Training or fine-tuning any model.
- N4. Recommendation generation. Recommending stays with the listener's `music-recs` skill, which may consume Headphones output (§7.6.2).
- N5. A hosted or multi-tenant service.
- N6. Replacing the listener's judgment. Ear evidence decides preference questions (§5.3).
- N7. Genre classification.
- N8. Running in a cloud Claude Code session. The audio library, the audio device and the listener's ears are on the listener's machine, so Headphones and the Claude Code session that uses it MUST run there. To drive it from a phone or claude.ai, the listener uses Claude Code Remote Control from that machine. See [ADR-0005](docs/adr/0005-local-station-architecture.md).

## 3. Actors and use cases *(informative)*

### 3.1 Actors

| Actor | Description |
|---|---|
| Listener | The single human user. Owns the audio library, provides ear judgments, is the ground truth for preference. |
| Agent | Claude Code, operating through the MCP server and skill. Can request analysis, read results, view renders and ask for ear judgments. Its MCP tools cannot create EAR or STATED evidence. Claude Code's own shell and file tools run with the listener's privileges and could forge data, which §7.5.3 and §13 address. |
| Maintainer | Person with commit rights. See [GOVERNANCE.md](GOVERNANCE.md). |
| Spotify connector | The Spotify integration inside Claude, launched by Spotify on 2026-04-23 and governed by its own terms. Outside Headphones' trust boundary. Headphones never calls it. |

### 3.2 Use cases

- **UC-1 Adjudicate.** "Score *Inside Out* by Spoon against BUILD and FEEL." The agent finds the owned file, runs analysis if needed, and reports each criterion with evidence, timestamps and what to verify by ear.
- **UC-2 Listening session.** The listener plays a track on the station, taps keys at a chill, when their head or body starts moving, when the hook lands, then answers the Quick Ear form (METRICS.md §4.1).
- **UC-3 Measure one property.** "Is the vocal on *Wet Sand* double-tracked?"
- **UC-4 Compare.** "Which of these three records has the driest drums?"
- **UC-5 Calibrate.** The listener scores a batch by ear. The harness reports agreement per metric.
- **UC-6 Control group, ear only.** The listener scores FEEL by ear on records they dislike and records they love while playing them on Spotify, using external playback mode (§7.4.3). No purchase is needed. Detectors run later on whatever subset the listener chooses to own. This is the experiment the profile says can be run today.
- **UC-7 Benchmark.** Run [docs/evaluation-plan.md](docs/evaluation-plan.md).
- **UC-8 History.** The listener imports their Spotify extended streaming history, subject to §6.2.

## 4. Terminology

| Term | Meaning |
|---|---|
| Audio asset | One audio file in the library, identified by `asset_id`, the SHA-256 of its bytes. |
| Recording | A distinct performance, identified by a MusicBrainz recording MBID. Several assets may share one. |
| External track | A track the listener hears outside the station, identified only by a Spotify URI the listener typed or pasted. |
| Stem | A separated source signal (drums, bass, vocals, guitar, piano, other). |
| Beat grid | Beat and downbeat times for an asset (§7.3.3). |
| Analyzer | Versioned code that produces metric values. |
| Metric | A property in METRICS.md with a stable ID such as `groove.pocket`. Proxy values use the metric ID plus `.proxy`. |
| Value | One result for one metric on one subject, with evidence class, confidence and provenance. |
| Evaluation record | The stored, schema-valid set of values for one subject. |
| Ear judgment | A value the listener enters at the station. |
| Tap | A timestamped key press during listening. |
| First listen | A listen where the listener has never heard the track: no plays in imported history, no prior preview, and the listener confirms it at the station. |
| Station | The long-lived `headphones station` process that owns playback, taps, ear forms and analysis jobs (§7.4). |
| Ear tier | Whether a metric's ear question is in the Quick Ear form, the rotating extras, or the full form (METRICS.md §4.1). |
| Tolerance | The reproducibility bound for a metric's outputs (METRICS.md §1). |
| Agreement band | How far an analyzer value may differ from an ear value before a calibration event is recorded (METRICS.md §1). |

## 5. Evidence model

### 5.1 Evidence classes

Every value MUST carry exactly one evidence class.

| Class | Meaning | Example |
|---|---|---|
| `MEASURED` | Computed directly from the signal by a method at `stable` maturity, for a metric whose ceiling is `MEASURED`. | Integrated loudness, track length, side-to-mid ratio. |
| `ESTIMATED` | Computed from the audio by a model or heuristic with known larger error, or depending on stem separation. | Snare offsets from a separated drum stem. |
| `PROXY` | A measurable signal believed to correlate with a perceptual property that cannot itself be measured. Never a claim about the property. | Time until a stable pulse, offered for the head-nod test. |
| `EAR` | Entered by the listener through the station's own keyboard input. | "Head moved at about 6 s." A chill tap at 2:14.6. |
| `BEHAVIORAL` | Derived from the listener's listening history. | Replayed within one hour on 4 of 9 plays. |
| `STATED` | Something the listener said about their taste, verbatim, with date. | "100 to 126 BPM." |
| `TEXTUAL` | From written sources about the record. | A review says it was recorded live to tape. |

- **REQ-EVID-01** A value MUST be labeled `MEASURED` only when the producing analyzer's maturity for that metric is `stable` (§11.3) and the metric's ceiling is `MEASURED`. Otherwise the strongest permitted label is `ESTIMATED`.
- **REQ-EVID-02** A `PROXY` value MUST use the metric ID `<metric>.proxy`, MUST name the proxied metric in `proxy_for`, and MUST NOT be reported by the agent as a value of that metric.
- **REQ-EVID-03** `EAR` evidence MUST be created only by the station from keyboard input on the station's own terminal (§7.4), with one exception: `headphones ear import`, which MUST require the listener to confirm each file interactively on the station's terminal and MUST mark values `capture.method: "import"`. No other code path, MCP tool or CLI flag may create `EAR` evidence.
- **REQ-EVID-04** `STATED` evidence MUST be stored verbatim with the date and context it was given ([schemas/stated.schema.json](schemas/stated.schema.json)) and MUST NOT be rewritten into a rule.
- **REQ-EVID-05** Every value MUST carry a `confidence` field. For `ok` values with class `MEASURED`, `ESTIMATED` or `PROXY` it MUST be a number from 0 to 1 computed as the METRICS.md entry defines. For `EAR`, `STATED` and `BEHAVIORAL` values, and for values that are not `ok`, it MUST be null unless the listener gave their own certainty.

### 5.2 Abstention

- **REQ-EVID-06** An analyzer MUST return `status: "abstained"` with a reason code from the metric's entry when its preconditions fail. An abstention MUST be shown to the agent as an answer.
- **REQ-EVID-07** An analyzer MUST NOT substitute a default or typical value for a missing measurement. Values that are not `ok` MUST NOT carry a `value` field.

### 5.3 Precedence

Measurement and judgment answer different questions.

- **REQ-EVID-08** For questions of preference and felt experience (does it work for the listener, did it give chills, does the head move), Headphones and the agent MUST treat `EAR` evidence as decisive over every other class.
- **REQ-EVID-09** For questions of physical fact (how wide is the mix, how long is the fade), a `MEASURED` value MUST be reported as measured even when an `EAR` value differs. The disagreement MUST be recorded as a calibration event ([schemas/calibration-event.schema.json](schemas/calibration-event.schema.json)), not resolved by discarding either value.
- **REQ-EVID-10** Where both apply, the agent MUST present both and say which question each answers.
- **REQ-EVID-11** Below `EAR`, for preference questions, the agent MUST weigh evidence in this order: `BEHAVIORAL`, `MEASURED`, `ESTIMATED`, `STATED`, `PROXY`, `TEXTUAL`.

### 5.4 Agent reporting rules

These are taught by the skill (§7.6.2) and checked by the benchmark (§12).

- **REQ-EVID-12** When the agent states a value it MUST name its evidence class in plain words ("measured", "estimated from the separated drum track", "a rough proxy", "you marked", "your play history", "you said", "reviews say").
- **REQ-EVID-13** When the agent has only `PROXY` or `TEXTUAL` support for a felt-experience claim it MUST say the listener should check by ear and SHOULD offer a stored timestamp to listen at.
- **REQ-EVID-14** The agent MUST NOT invent timestamps. Every timestamp it gives MUST come from a stored value, a render caption, or a tap.

### 5.5 Composite evidence

- **REQ-EVID-15** A composite criterion (BUILD, FEEL) MUST carry `evidence_basis`, the set of evidence classes of all its inputs, not a single class. It MUST also carry `basis_summary`: `ear` if any input is `EAR`, else `analysis` if all inputs are `MEASURED` or `ESTIMATED`, else `proxy` if any input is `PROXY`. The agent MUST report the summary and name any `PROXY` or `EAR` inputs.

## 6. Legal and sourcing constraints

This section reflects the project's reading of third-party terms on the date above. It is not legal advice. The project MUST re-check every term referenced here at every minor release and record the date in the release notes (§15.4).

### 6.1 Audio sources

- **REQ-SRC-01** The harness MUST analyze only assets the listener has placed in the local library. It MUST NOT fetch audio from any network service.
- **REQ-SRC-02** The harness MUST NOT capture, record, loop back or intercept audio from Spotify or any other streaming client. It MUST NOT include, document or link to tooling that does.
- **REQ-SRC-03** Ingest MUST refuse files carrying DRM it cannot decode. The harness MUST NOT include or invoke DRM circumvention.
- **REQ-SRC-04** Ingest SHOULD record an optional listener-supplied `source` label per asset (`bandcamp`, `itunes`, `amazon`, `qobuz`, `hdtracks`, `artist_store`, `cd_rip`, `vinyl_rip`, `other`). The harness cannot verify it.
- **REQ-SRC-05** Store licences generally permit personal, non-commercial use only. Bandcamp's terms, for example, grant use "solely for personal, non-commercial use". Headphones' documentation MUST say so, and MUST say that anyone using Headphones commercially clears rights themselves.
- **REQ-SRC-06** Golden-set and validation assets (§11.4) MUST be run only by the person who owns them. Only aggregate numbers and `pcm_sha256` references may be published.

The practical path, in order (see [ADR-0001](docs/adr/0001-owned-audio-only.md)):

1. **Use what you already own.** `headphones library add` on existing files and CD rips. This costs nothing.
2. **Buy DRM-free downloads.** Major-label catalogs, which include most of the listener's anchor artists, are generally sold DRM-free on the iTunes Store (AAC) and Amazon (MP3). Independent releases are often on Bandcamp or Qobuz in lossless formats. Availability varies by artist and country and MUST be checked per purchase.
3. **Rip CDs you own** where local law allows private copying. Rules differ by country.

### 6.2 Spotify

Facts checked on 2026-10-05 (see [ADR-0002](docs/adr/0002-spotify-boundary.md) for sources):

- The Spotify **Developer Policy** binds apps built on the Spotify Platform. It forbids analyzing Spotify Content and ingesting it into an AI model.
- The Spotify **User Guidelines**, part of the Terms of Use every listener accepts, forbid "using any part of the Services or Content to train a machine learning or AI model or otherwise ingesting Spotify Content into a machine learning or AI model", and forbid ripping or recording.
- The **February 2026** Web API changes applied to Development Mode apps. They removed several endpoints and fields. The removal of `external_ids` (ISRC) was reversed in **March 2026**.
- The **Spotify connector in Claude** was launched by Spotify itself on 2026-04-23. Its use is governed by Spotify's and Anthropic's terms for that integration.

Requirements:

- **REQ-SPOT-01** Headphones MUST NOT include a Spotify Web API client, so the Developer Policy does not bind it as an app. Any Spotify data the agent sees comes from the Spotify connector, under that connector's terms.
- **REQ-SPOT-02** Headphones MUST NOT store data obtained from the Spotify Web API or the Spotify connector. It MAY store a Spotify track URI that the listener typed or pasted themselves, either to link an asset (§7.2.3) or to identify an external track (§7.4.3). A URI is an opaque string that Headphones never dereferences.
- **REQ-SPOT-03** Headphones MAY import the listener's Spotify extended streaming history, which the listener requests from Spotify as their own personal data. Import MUST be explicit and local and MUST be deletable as a unit.
- **REQ-SPOT-04** Whether passing the listener's own streaming history to an AI agent counts as "ingesting Spotify Content into an AI model" under the User Guidelines is unresolved (§17, OI-1). Until resolved, history import and `BEHAVIORAL` metrics MUST be off by default. Enabling them MUST show a notice that quotes the User Guidelines clause above and the listener's data portability right as the counter-argument, and MUST require explicit confirmation.
- **REQ-SPOT-05** History import MUST keep only `ts`, `ms_played`, `spotify_track_uri`, `reason_start`, `reason_end`, `skipped` and `shuffle`. It MUST discard all other fields (including `ip_addr`, `conn_country`, `platform`, `user_agent_decrypted`, `username`, `offline_timestamp`) and all podcast, audiobook and video rows before anything is written. It MUST exclude rows with `incognito_mode: true` unless the listener opts in. Stored rows follow [schemas/history-play.schema.json](schemas/history-play.schema.json).

### 6.3 Dependency and model licenses

- **REQ-LIC-01** Every runtime dependency and every model weight file MUST have a license permitted by [ADR-0003](docs/adr/0003-dependency-and-model-licenses.md). Additions require an ADR amendment.
- **REQ-LIC-02** Weights or code whose license forbids commercial use MAY be supported only as optional, separately installed plugins that are off by default and labeled.
- **REQ-LIC-03** Every release MUST include an SBOM (SPDX 2.3 or CycloneDX 1.5) covering Python packages, bundled native libraries and model weights with hashes and licenses. Native tools taken from the system (FFmpeg, mpv, fpcalc) MUST be recorded by version and build configuration, since they cannot be hashed at release time.
- **REQ-LIC-04** The repository MUST keep a [NOTICE](NOTICE) file listing every third-party component and weight with its authors, license and any attribution the license requires.
- **REQ-LIC-05** Known training-data restrictions of bundled weights (for example, research-only datasets) MUST be recorded in the SBOM and in ADR-0003.

## 7. Architecture

### 7.1 Overview

```
 Listener's machine (required, see N8)
 +---------------------------------------------------------------------+
 |                                                                     |
 |  Terminal A: Claude Code            Terminal B: headphones station  |
 |  +----------------------+           +-----------------------------+ |
 |  | Claude Code          |           | Station (long-lived)        | |
 |  |  + headphones plugin |           |  - owns mpv (playback)      | |
 |  |    (skill, MCP cfg)  |           |  - reads tap keys on its    | |
 |  +----------+-----------+           |    own terminal             | |
 |             | stdio (JSON-RPC)      |  - ear form queue           | |
 |  +----------v-----------+  0600     |  - analysis job queue       | |
 |  | headphones mcp       |  socket   |  - sole writer of EAR rows  | |
 |  | (thin client,        +---------->|                             | |
 |  |  never spawns)       | requests  +--------------+--------------+ |
 |  +----------------------+                          |                |
 |                                         spawns sandboxed children   |
 |                      +-------------------+---------+---------+      |
 |                      | ffmpeg decode     | analyzers         |      |
 |                      | (stdin pipe only) | (no network)      |      |
 |                      +-------------------+-------------------+      |
 |                                          |                          |
 |                      +-------------------v-------------------+      |
 |                      | Evidence store: SQLite (0600) + CAS   |      |
 |                      +---------------------------------------+      |
 |   Owned audio files (library roots)                                 |
 +---------------------------------------------------------------------+
   Network: model download at init, optional AcoustID lookup (opt-in)
```

Implementation language: Python 3.12 or later. Distribution: one Python package `headphones`, installable with `uv` or with `pip` plus a published hash-pinned constraints file. Native tools: FFmpeg 6 or later, mpv 0.37 or later, Chromaprint `fpcalc`.

### 7.2 Library, ingest and identity

#### 7.2.1 Ingest

- **REQ-ING-01** `headphones library add <path>` MUST scan for FLAC, WAV, AIFF, ALAC, MP3, AAC/M4A, Ogg Vorbis and Opus.
- **REQ-ING-02** Decoding MUST run in a sandboxed child process (§10.4), never in the MCP server. FFmpeg MUST read the file's bytes from a pipe on stdin, with `-protocol_whitelist pipe`, an explicit input format chosen by the harness from the file's magic bytes, and a demuxer whitelist limited to the formats in REQ-ING-01. Files whose magic bytes match none of them MUST be rejected.
- **REQ-ING-03** Each asset MUST be identified by `asset_id`, the lowercase hex SHA-256 of the file bytes. Moving or renaming a file MUST NOT change its identity. When re-tagging changes the bytes, the library MUST detect it by matching `pcm_sha256` (SHA-256 of the decoded 32-bit float PCM at the native rate) and MUST carry existing evaluations across.
- **REQ-ING-04** Ingest MUST record sample rate, bit depth where defined, channels, duration, codec and whether the codec is lossy.
- **REQ-ING-05** Mono assets MUST be accepted. Metrics needing two channels MUST abstain with `mono_source`.
- **REQ-ING-06** Assets over 20 minutes MUST be accepted for the library, and analysis MUST either window them or abstain with `too_long`. The limit is configurable.
- **REQ-ING-07** Library roots MUST be canonicalized at configuration time. Every later open of an asset MUST use `O_NOFOLLOW` (or the platform equivalent), MUST confirm that the device and inode match those recorded at ingest and that the path still resolves inside a root, and MUST stream bytes whose SHA-256 equals `asset_id` before they are used. A mismatch MUST stop the operation with `asset_changed`.

#### 7.2.2 Identity

- **REQ-ID-01** The harness MUST compute a Chromaprint fingerprint for every asset. `fpcalc` MUST run in a sandboxed child (§10.4) and MUST receive decoded PCM from the decoder over a pipe, never the original file.
- **REQ-ID-02** The harness MAY look up fingerprints on AcoustID to get MusicBrainz recording MBIDs and core metadata (`meta=recordings`). The lookup MUST be off until the listener enables it, and `headphones init` MUST ask with the default answer "no". The prompt MUST say what is sent: fingerprint, duration, the project's registered AcoustID client key, a User-Agent string, and the listener's IP address. It MUST NOT send file names, paths, tags or listening data.
- **REQ-ID-03** Without a lookup, identity MUST fall back to embedded tags and MUST be marked `identity_confidence: "tags_only"`.
- **REQ-ID-04** Metadata MUST come only through the AcoustID lookup in REQ-ID-02. Headphones MUST NOT call the MusicBrainz API directly. It MUST store only MBIDs, ISRCs, recording length and the artist, title and album strings, and MUST attribute AcoustID data as its CC BY-SA license requires.
- **REQ-ID-05** The listener MAY link an asset to a Spotify track URI with `headphones link <asset> <uri>`. Linking MUST be done by the listener. The agent MAY suggest a URI it found through the Spotify connector, but only the listener's command stores it.
- **REQ-ID-06** The harness MUST NOT assume a linked Spotify track uses the same master as the owned asset, and MUST tell the agent that values describe the owned asset.
- **REQ-ID-07** AcoustID is free for non-commercial use only and allows at most 3 requests per second. The client MUST stay under that rate, MUST look each asset up at most once (results cached), and the documentation MUST state the non-commercial condition.

### 7.3 Analysis engine

#### 7.3.1 Pipeline

```
decode -> resample(44.1k, float32) -> loudness (libebur128)
       \-> separate(stems) -> per-stem onsets -> drum transcription
       \-> beat & downbeat grid -> swing and meter estimate -> reference pulse
       \-> structure segmentation <- stem activity
       \-> pitch tracks (bass f0, vocal f0, polyphonic notes)
                         |
                         v
                metric analyzers -> composites (BUILD, FEEL) -> evaluation record
```

- **REQ-ENG-01** Every stage and analyzer MUST declare a name, a SemVer version, inputs, outputs, and the weights it uses with SHA-256 hashes.
- **REQ-ENG-02** An artifact's cache key MUST be the hash of its inputs' keys, the stage version and its effective configuration. A change to any of these MUST invalidate downstream artifacts and no others.
- **REQ-ENG-03** The engine MUST resample to 44.1 kHz float32 for analysis while keeping the channel layout. Analyzers that need the native rate (true peak) MUST read the decoded original.
- **REQ-ENG-04** A failing analyzer MUST NOT fail the run. Its metrics MUST be recorded with `status: "error"` and an error code, and the run MUST continue.

#### 7.3.2 Source separation

- **REQ-SEP-01** The reference separator MUST be Demucs `htdemucs_6s` (MIT), producing drums, bass, vocals, guitar, piano and other. Other separators MAY be used through the stage contract.
- **REQ-SEP-02** The engine MUST compute a per-stem separation quality `sepq` as defined in METRICS.md §2.1, calibrated against measured separation quality on a licensed multitrack validation set. Metrics that depend on a stem MUST declare a floor and abstain below it.
- **REQ-SEP-03** Stems MUST be cached, MUST be deletable with `headphones cache prune`, and MUST NOT leave the machine through any Headphones interface. The MCP server MUST NOT return audio.

#### 7.3.3 Beat grid and reference pulse

- **REQ-BEAT-01** The reference beat and downbeat tracker MUST be `beat_this` (MIT, code and weights). Alternatives MAY be used through the stage contract.
- **REQ-BEAT-02** The grid MUST be stored as beat times and downbeat flags, not a single tempo.
- **REQ-BEAT-03** Microtiming analyzers MUST measure against the reference pulse defined in METRICS.md §2.3 (leave-one-out consensus, swing-aware, locally fitted), never against raw tracker output.

#### 7.3.4 Weight handling

- **REQ-WGT-01** Weights MUST be converted to `safetensors` (or verified ONNX or TFLite files for models distributed that way) at pinning time by the project, hashed, and published in the release manifest. Headphones MUST load weights only through its own loaders. Calls to library "pretrained" or hub loaders (for example `torch.hub`, Demucs `get_model`, Hugging Face `from_pretrained`) are forbidden at run time.
- **REQ-WGT-02** Analyzer child processes MUST run with `TORCH_HOME` and `HF_HOME` pointing at an empty read-only directory and with `HF_HUB_OFFLINE=1`, so a lazy download fails instead of reaching the network.
- **REQ-WGT-03** `headphones init` MUST download weights over HTTPS and verify each SHA-256 against the release manifest before writing it to the weights directory.

#### 7.3.5 Shared primitives

Onsets, swing and meter, drum transcription, pitch, loudness, structure, stem activity, stereo, envelopes and event tagging are specified once in METRICS.md §2.

### 7.4 Listening station

The station is a long-lived process the listener starts in its own terminal with `headphones station`. It owns playback, tap capture, ear forms and the analysis job queue. All `EAR` evidence is born here. See [ADR-0005](docs/adr/0005-local-station-architecture.md).

#### 7.4.1 Process model

- **REQ-LS-12** The station MUST listen only on a Unix domain socket (mode 0600, in a 0700 directory) or a Windows named pipe restricted to the current user. The station MUST refuse to start if the socket directory already exists and is not owned by the current user with mode 0700. Every message on the socket MUST be validated against a published JSON Schema and rejected otherwise. The MCP server MUST be a client of that socket and MUST NOT spawn mpv, the station or analyzers itself.
- **REQ-LS-13** If the station is not running, MCP tools that need it MUST return the error code `station_not_running` and the exact command to start it.
- **REQ-LS-14** Only one station may run per user. A second instance MUST exit with an error naming the first.
- **REQ-LS-15** Child processes MUST have stdout and stderr redirected to the station's log, never to an inherited terminal or protocol channel.

#### 7.4.2 Playback and taps

- **REQ-LS-01** Playback MUST use mpv controlled over a JSON IPC socket in a per-session 0700 directory. mpv MUST be launched with `--no-config --load-scripts=no --ytdl=no --load-auto-profiles=no --no-input-default-bindings --input-conf=<station-supplied>` and with playlist parsing disabled. mpv MUST NOT parse the original container. The station MUST give mpv the asset as decoded PCM in a WAV container, produced by the sandboxed decoder from hash-verified bytes (REQ-ING-07), written to a 0600 temporary file in the cache and passed as an already-open file descriptor so seeking works. mpv MUST NOT be given a path or URL.
- **REQ-LS-16** Taps MUST be read from the station's own terminal. mpv IPC events MUST NOT be accepted as taps. Tap time is mpv's reported `audio-pts` at the key event, minus the device output latency (REQ-LS-08).
- **REQ-LS-02** After latency calibration, tap timestamps MUST be within 100 ms of the audio actually reaching the listener's ears at the 95th percentile, verified by the procedure in [docs/evaluation-plan.md](docs/evaluation-plan.md) §8. Bluetooth output MUST trigger a warning that latency can drift.
- **REQ-LS-03** The station MUST offer a terminal interface. A local browser interface MAY be added. If added it MUST bind to 127.0.0.1 only, MUST reject any request whose `Host` header is not exactly `127.0.0.1:<port>`, MUST check `Origin`, MUST use a per-session token that never appears in a URL after the first exchange, and MUST NOT enable CORS.
- **REQ-LS-04** Default tap keys MUST be: `c` chill, `n` head or body starts moving, `h` hook lands, `m` kept mistake, `g` gap that hit you, `t` tap along with the felt beat (8 or more), `space` generic mark, `u` undo last tap. Bindings are configurable.
- **REQ-LS-05** After playback the station MUST present the **Quick Ear** form (METRICS.md §4.1) plus up to three rotating extra questions, unless the listener chose the full form. For benchmark tracks the station MUST present the benchmark ear set defined in [docs/evaluation-plan.md](docs/evaluation-plan.md) §2. Every question MUST allow "not sure" and "skip".
- **REQ-LS-06** The station MUST NOT play files outside the library.
- **REQ-LS-07** The station MUST offer loudness-normalized playback at -14 LUFS integrated (default on) and MUST record the mode with every ear judgment.
- **REQ-LS-17** At the start of each listen the station MUST ask "Have you heard this before?" (yes, no, not sure) and record `familiar` and `first_listen` (§4) with every ear judgment from that listen.
- **REQ-LS-18** Text from tags, file names or metadata MUST have C0 and C1 control characters and Unicode bidirectional override characters removed before the station displays it.
- **REQ-LS-19** A question the agent queued with `hp_request_ear` MUST be shown labeled "Question from Claude", with the agent's wording, and the wording MUST be stored with the answer (`capture.agent_prompt`).
- **REQ-LS-20** When an ear form is queued while the station is idle, the station MUST show it at the top of its screen and SHOULD send a desktop notification (`notify-send`, `osascript` or the Windows equivalent).

#### 7.4.3 Latency calibration

- **REQ-LS-08** `headphones station --calibrate` MUST measure output latency for the current device: by acoustic loopback through a microphone where available, otherwise by asking the listener to tap along with a 100 BPM click train for at least 16 clicks. The method used, the median correction and the interquartile range MUST be stored per listener-assigned device label and shown with every tap on that device. Device labels are chosen by the listener and MUST NOT be taken from OS or Bluetooth device names. Loopback recordings MUST be held in memory only and discarded once the latency is measured.

#### 7.4.4 External playback mode

For listening on Spotify or any other player without owning the file. It replaces the 0.1.0 "companion mode".

- **REQ-LS-09** *Withdrawn in 0.2.0.* Reading playback position through the Spotify connector contradicted REQ-SPOT-02 and REQ-EVID-03 and was unreliable.
- **REQ-LS-10** *Withdrawn in 0.2.0.* Replaced by REQ-LS-11 and REQ-LS-21.
- **REQ-LS-11** `headphones station --external <spotify-uri>` MUST run the station without playing audio. The listener pastes the URI and the track's artist and title themselves. The listener presses `s` at the moment the track starts on their player (or enters a start offset by hand after pausing). Taps are timed by the station's local monotonic clock relative to that sync. Nothing is read from Spotify or the connector.
- **REQ-LS-21** External-mode ear values MUST be `EAR` with `capture.method: "external"`, MUST carry a timing uncertainty of at least 1.0 s, MUST be stored in a record whose subject is the external track (schema `external`), and MUST NOT be used to validate analyzer timing (§11).

### 7.5 Evidence store

#### 7.5.1 Storage

- **REQ-STORE-01** Structured data MUST be stored in SQLite under the platform user-data directory (for example `~/.local/share/headphones` on Linux).
- **REQ-STORE-02** Large artifacts (stems, feature arrays, renders) MUST be stored in a content-addressed directory keyed by SHA-256.
- **REQ-STORE-03** Evaluation records MUST be exportable as JSON that validates against [schemas/evaluation-record.schema.json](schemas/evaluation-record.schema.json).
- **REQ-STORE-04** Values MUST be append-only during normal operation. A re-analysis MUST add new values and set `superseded_by` on earlier ones. Analysis MUST NOT supersede ear judgments. Only a later ear judgment from the listener may. `headphones forget` is the only permitted hard delete (REQ-STORE-07).
- **REQ-STORE-05** The store MUST support `headphones export` and `headphones forget` exactly as [docs/privacy.md](docs/privacy.md) defines, covering every data class in its inventory.
- **REQ-STORE-06** Database migrations MUST be versioned and reversible for at least one minor version. Pre-migration backups MUST be deleted once the migration is confirmed, and `forget` MUST also remove matching rows from any backup that still exists.
- **REQ-STORE-08** The data, cache, log and socket directories MUST be created with mode 0700 and their files with mode 0600, or an equivalent current-user-only ACL on Windows.

#### 7.5.2 Forget

- **REQ-STORE-07** `headphones forget <asset>` MUST delete, for every asset sharing the target's `pcm_sha256`: library entries and paths, fingerprints and identity, links, values including superseded ones, ear judgments, calibration events, renders, stems and features, run manifests, queued jobs and ear requests, and log lines that name the asset. It MUST add the asset to an exclusion list so the next scan does not re-ingest it, unless the listener passes `--allow-rescan`. After deletion it MUST checkpoint the WAL and run `VACUUM`, and the database MUST run with `PRAGMA secure_delete=ON`.

#### 7.5.3 Evidence integrity

The agent's MCP tools cannot write evidence. Claude Code's other tools (shell, file edits) run as the listener and could. Headphones detects tampering but cannot prevent a process with the listener's privileges from writing files.

- **REQ-STORE-09** `EAR` and `STATED` rows MUST be chained with HMAC-SHA256 under a key held in the OS keychain (macOS Keychain, Windows Credential Manager, Secret Service on Linux). The current chain head MUST also be stored outside the database in a 0600 file. `headphones doctor` MUST verify both. `forget` MUST write a redaction entry to the chain (rows removed, count, time, no content) so that a forget is distinguishable from tampering.
- **REQ-STORE-10** The MCP server MUST open the store read-only (SQLite `mode=ro`). Only the station and the CLI write.
- **REQ-STORE-11** The plugin (§7.6.4) MUST ship recommended Claude Code permission deny rules for `headphones station`, `headphones ear`, `headphones stated`, `headphones link`, `headphones forget`, `sqlite3`, and file writes under the Headphones data and config directories. `headphones init --claude-permissions` MAY install them into the listener's Claude Code settings after showing them and asking. The skill MUST tell the agent never to run these commands or touch those directories.

### 7.6 Claude Code integration

#### 7.6.1 MCP server

- **REQ-MCP-01** The MCP server MUST use the stdio transport only and MUST NOT write anything to stdout except protocol messages.
- **REQ-MCP-02** The server MUST NOT expose any tool that writes `EAR` or `STATED` evidence, links URIs, deletes data or changes configuration.
- **REQ-MCP-03** Text derived from tags, file names or AcoustID MUST appear only inside `untrusted_metadata` fields, stripped of control and bidi characters, at most 512 characters each. The skill tells the agent to treat it as data.
- **REQ-MCP-04** Analysis MUST be asynchronous. `hp_analyze` returns a `job_id` and an `eta_s`. `hp_job_status` MUST accept `wait_s` (0 to 25) and hold the call until the job's state changes or the wait ends, and MUST return `state`, `progress`, `eta_s` and `next_poll_after_s`. The server SHOULD send MCP progress notifications. No call may block longer than 30 s.
- **REQ-MCP-05** Tool inputs MUST be validated against JSON Schema. Track references MUST be an `asset_id`, a library search string or a linked Spotify URI. Tools MUST NOT accept file paths. A search string matching more than one asset MUST return `ambiguous` with up to 10 candidates instead of picking one.
- **REQ-MCP-06** The server MUST support a blind mode, configured by the station for benchmark runs, in which no tool returns `EAR` values, calibration events or calibration reports for the listed assets.
- **REQ-MCP-07** Errors MUST be returned as MCP tool results with `isError: true` and a code from a fixed enum (for example `station_not_running`, `not_in_library`, `ambiguous`, `asset_changed`, `job_failed`, `invalid_input`). Messages MUST NOT include file paths, stderr from child processes, or tag text outside `untrusted_metadata`.
- **REQ-MCP-08** Every tool MUST declare MCP annotations. Read tools MUST set `readOnlyHint: true`. `hp_listen` and `hp_request_ear` MUST set `readOnlyHint: false` and the skill MUST only call them when the listener asked.
- **REQ-MCP-09** `hp_get_evaluation` MUST return a compact summary by default: per metric the ID, status, evidence class, confidence, category or main scalar, and at most 5 timestamps. `detail: "full"` MUST require a `metrics` list of at most 8 IDs. `capture.note` and `capture.device` MUST be omitted unless asked for by name. Full records stay available through the CLI and `export`.

| Tool | Input | Output | Read only |
|---|---|---|---|
| `hp_library_search` | `query`, `limit` | Matching assets with `asset_id`, `untrusted_metadata`, duration, analysis status, or `ambiguous` | yes |
| `hp_analyze` | `track`, optional `metrics[]`, optional `force` | `job_id`, `eta_s` | yes (queues computation only) |
| `hp_job_status` | `job_id`, optional `wait_s` | `state`, `progress`, `stage`, `eta_s`, `next_poll_after_s`, error code | yes |
| `hp_get_evaluation` | `track`, optional `metrics[]`, optional `detail` | Compact summary or full values (REQ-MCP-09) | yes |
| `hp_render` | `track`, `view`, optional `start_s`, `end_s` | PNG plus caption with axes, units and stored timestamps | yes |
| `hp_compare` | `tracks[]` (2 to 10), `metrics[]` (at most 8) | Table of values with evidence classes | yes |
| `hp_build_feel` | `track` | BUILD and FEEL criteria with evidence basis, things to verify by ear | yes |
| `hp_chill_candidates` | `track`, optional `limit` | Ranked `PROXY` moments with reasons, plus `EAR` chill taps unless blind | yes |
| `hp_request_ear` | `track`, `metrics[]`, optional `prompt` | `request_id`, `station_running`, `queued_forms` | no |
| `hp_ear_status` | `request_id` | `pending`, `answered` or `expired`. Never the answers themselves. | yes |
| `hp_listen` | `track`, optional `start_s` | Asks the station to start playback | no |
| `hp_calibration_report` | optional `metrics[]` | Agreement statistics, excluding sealed held-out assets (evaluation plan §4) | yes |

`view` is one of `spectrogram`, `microtiming`, `stem_activity`, `stereo_field`, `loudness`, `structure`, `decay`, `pitch` (METRICS.md §3).

#### 7.6.2 Skill

- **REQ-SKILL-01** The project MUST ship a skill at `plugin/skills/headphones/SKILL.md` that teaches: the evidence classes and §5.4 reporting rules, the §5.3 precedence rules, how to read each render view, the no-lyrics rule, that metadata is untrusted, how to wait for jobs without looping, the commands and paths the agent must never touch (REQ-STORE-11), and the hand-off to `music-recs`.
- **REQ-SKILL-02** The skill MUST tell the agent to look at a render before describing a timing, stereo or structure claim.
- **REQ-SKILL-03** The skill MUST tell the agent that values describe the owned asset, which may be a different master from the Spotify stream.
- **REQ-SKILL-04** The skill's description MUST be limited to owned audio and audio measurement so that it does not compete with `music-recs` for recommendation requests. The project MUST document the one change `music-recs` needs: "If the track is in the Headphones library, call `hp_build_feel` before scoring from text."

#### 7.6.3 Renders

- **REQ-REND-01** Every render MUST have axis labels with units and a title made only of the `asset_id` prefix (12 characters) and the metric or view name. Tag text MUST NOT be drawn into images. A caption returned with the image MUST state what is plotted, the time range, the units and any stored timestamps shown.
- **REQ-REND-02** Render dimensions MUST be multiples of 28 pixels with (width/28) × (height/28) ≤ 1568 (for example 1568 × 784 or 1092 × 1092), and neither side may exceed 2000 pixels. This keeps axis text legible without server-side downscaling.

#### 7.6.4 Packaging

- **REQ-PKG-01** The Claude Code integration MUST ship as a Claude Code plugin named `headphones` in `plugin/`, containing `.claude-plugin/plugin.json`, `.mcp.json` (server `headphones`, command `headphones`, args `["mcp"]`), the skill, and `recommended-settings.json` with the deny rules from REQ-STORE-11.
- **REQ-PKG-02** `headphones mcp` MUST exit at start with a clear error when no library is configured or no station socket can exist on this machine (for example, inside a cloud container). `headphones doctor` MUST report the same check.

### 7.7 Composites: BUILD and FEEL

The BUILD and FEEL tests come from the listener's profile. Headphones evaluates them against audio. It does not change their definitions.

- **REQ-COMP-01** BUILD and FEEL MUST be computed from the metric values in METRICS.md §5, with evidence carried as REQ-EVID-15 requires.
- **REQ-COMP-02** A criterion that depends on an abstained or errored value, or on a missing ear value, MUST be `unknown`, not `fail`. BUILD MUST be reported as "n of 5 known pass, m unknown".
- **REQ-COMP-03** The 100 to 126 BPM range in BUILD criterion 1 is `STATED`. Headphones MUST report the measured tempo and whether it is inside the range, and MUST NOT fail criterion 1 on tempo.
- **REQ-COMP-04** FEEL detections MUST be reported with timestamps. The agent MUST NOT present the FEEL count as a prediction of chills unless evaluation Study C supports it. BUILD MUST be described as "claimed by the profile to predict replays, not tested forward" until Study D supports it.
- **REQ-COMP-05** Routing MUST follow the profile's artist-level rules (METRICS.md §5.3). For a single track Headphones MUST report only the BUILD and FEEL results and MUST NOT route.

## 8. Interfaces

### 8.1 Command line

| Command | Purpose |
|---|---|
| `headphones init [--claude-permissions]` | Create directories, check native tools, download and verify weights, ask about online lookup (default no), optionally install deny rules |
| `headphones doctor [--json] [--unredacted]` | Versions, weight hashes, calibration, disk use, evidence chain check, local-machine check. Redacts paths, device labels and identity unless `--unredacted`. |
| `headphones library add <path>` / `list` / `remove <asset>` | Manage the library |
| `headphones link <asset> <spotify-uri>` | Link an asset to a Spotify URI |
| `headphones analyze <track> [--metrics ...] [--force]` | Queue analysis on the station |
| `headphones show <track> [--metrics ...] [--json]` | Print an evaluation |
| `headphones render <track> <view> [--out <file>]` | Write a render |
| `headphones station` / `--calibrate` / `--external <uri>` | Run the station, calibrate latency, or run external playback mode |
| `headphones listen <track>` | Ask the running station to play a track |
| `headphones ear import <file>` | Interactive import of past ear judgments |
| `headphones stated add` / `list` | Record and list stated preferences, verbatim |
| `headphones history import <dir>` | Import extended streaming history (off unless enabled, REQ-SPOT-04) |
| `headphones calibrate report` | Analyzer versus ear agreement |
| `headphones bench run <plan>` | Run the evaluation benchmark |
| `headphones export` | Export everything in the privacy inventory |
| `headphones forget <asset> [--allow-rescan]` / `forget --history` / `forget --stated <id>` / `forget --external <uri>` / `forget all` | Hard delete (REQ-STORE-07, docs/privacy.md) |
| `headphones stated retract <id>` | Mark a stated preference as no longer true, keeping the record (`retracted_at`) |
| `headphones cache prune` | Remove stems and feature arrays |
| `headphones mcp` | Run the MCP server on stdio |

- **REQ-CLI-01** Every command that prints results MUST support `--json`. The schemas for those outputs MUST be published in `schemas/cli/` before milestone M1 ends.
- **REQ-CLI-02** Exit codes MUST be: 0 success, 1 usage error, 2 partial success, 3 dependency missing, 4 data error, 5 internal error, 6 station not running.

### 8.2 Analyzer plugin contract

Analyzers are Python entry points in the group `headphones.analyzers`.

```python
class Analyzer(Protocol):
    name: str                      # e.g. "groove.pocket" (version is separate)
    version: str                   # SemVer of the method
    metrics: tuple[str, ...]       # metric IDs produced, including ".proxy" IDs
    requires: tuple[str, ...]      # artifact types, e.g. ("stems", "reference_pulse")
    weights: tuple[WeightRef, ...] # name, sha256, license, training_data_notes

    def analyze(self, ctx: AnalysisContext) -> list[MetricResult]: ...
```

- **REQ-PLUG-01** `analyze` MUST be a pure function of `ctx` and configuration. It MUST NOT perform network I/O, read outside `ctx`, or write outside its scratch directory. The engine enforces this where the platform allows (REQ-RES-03) and otherwise relies on review of enabled plugins.
- **REQ-PLUG-02** Each result MUST validate against the schema's `value` definition.
- **REQ-PLUG-03** Discovery MUST read entry-point metadata without importing the module. Only analyzers named in configuration may be imported, and only inside the sandboxed analyzer child, never in the CLI, station or MCP server process.

### 8.3 Configuration

A TOML file in the platform config directory. Unknown keys MUST cause a warning. Every threshold used to map a measurement to a category MUST be configurable and MUST be recorded in each record's `engine.thresholds`, with its digest in `engine.config_digest`.

## 9. Data model

Normative schemas (JSON Schema draft 2020-12):

| Schema | Content |
|---|---|
| [evaluation-record.schema.json](schemas/evaluation-record.schema.json) | One subject (asset or external track) with its values and composites |
| [stated.schema.json](schemas/stated.schema.json) | Stated preferences, verbatim |
| [calibration-event.schema.json](schemas/calibration-event.schema.json) | Analyzer versus ear disagreements |
| [history-play.schema.json](schemas/history-play.schema.json) | Imported streaming-history rows after minimization |

An evaluation record contains `schema_version`, `record_id` (UUIDv7), `created_at` (RFC 3339, UTC, `Z` suffix), and exactly one subject: `asset` (owned file with identity) or `external` (listener-entered Spotify URI and metadata). Asset records also contain `engine` (version, platform, config digest, thresholds, components with weight hashes) and `separation_quality`. Every record contains `values[]` and MAY contain `composites`.

Each value contains `value_id` (UUID), `metric_id`, `status`, `reason` when not `ok`, `evidence_class`, `confidence`, `value` when `ok`, optional `category`, optional `timestamps[]` (at most 200), `proxy_for` for proxies, `method` and `maturity` for analysis values, `capture` for ear values (method, captured time, device label, latency correction and spread, normalization, listen index, familiar, first listen, optional note, optional agent prompt), and `superseded_by` when superseded.

- **REQ-DATA-01** Each schema MUST carry its own SemVer (§0.2) in `$comment` and in the records it validates.
- **REQ-DATA-02** Readers MUST ignore unknown fields in a record whose major schema version they support.
- **REQ-DATA-03** Producers MUST ensure `known_pass` and `unknown` match the BUILD criteria array and `count` matches the FEEL moves, which JSON Schema cannot check. Consumers SHOULD verify.

## 10. Processing requirements

### 10.1 Determinism

- **REQ-DET-01** Given the same asset, configuration, software version and weights, analysis on the same platform MUST produce identical categories and numeric outputs within each metric's tolerance (METRICS.md §1).
- **REQ-DET-02** All randomness MUST be seeded from `pcm_sha256`. The default separator configuration MUST disable random shifts.
- **REQ-DET-03** Differences across platforms (CPU versus GPU, different BLAS) MUST stay within tolerance. The conformance suite MUST run on Linux x86_64 CPU and at least one GPU backend.

### 10.2 Performance targets *(informative)*

On an 8-core x86_64 CPU with 16 GB RAM and no GPU, for a 4-minute stereo track: ingest and fingerprint under 5 s, separation under 6 min, all analyzers after separation under 90 s, cached `hp_get_evaluation` under 300 ms. With a supported GPU, total analysis under 90 s. These are roadmap targets, not conformance requirements.

### 10.3 Caching

- **REQ-CACHE-01** Re-requesting analysis with unchanged inputs MUST return cached results without recomputation.
- **REQ-CACHE-02** The cache MUST have a configurable size limit (default 20 GB) with least-recently-used eviction of stems first, then feature arrays. Evaluation records MUST NOT be evicted.

### 10.4 Sandboxing and resource limits

- **REQ-RES-01** Decoder, analyzer and mpv child processes MUST run with a memory limit (default 8 GB for analyzers, 1 GB for decode and playback), a CPU time limit proportional to duration, and no network access where the platform allows it. On Linux this MUST use a network namespace or seccomp filter. On macOS and Windows, where no supported per-process network block exists for unprivileged software, the documentation MUST say that network isolation is not provided.
- **REQ-RES-03** On Linux, analyzer children MUST be confined to read-only access to the job's artifact directory and write access to their scratch directory (Landlock or a mount namespace). On macOS and Windows the documentation MUST say that filesystem confinement is not provided.
- **REQ-RES-02** Analysis jobs MUST run one at a time by default. The station MUST stay responsive to taps while analysis runs.

## 11. Validation and quality

### 11.1 Principle *(informative)*

No metric is trusted because its algorithm sounds right. Each analyzer earns its evidence class through measured agreement with known answers. [docs/evaluation-plan.md](docs/evaluation-plan.md) is normative for procedures.

### 11.2 Conformance suite

- **REQ-VAL-01** The project MUST maintain a synthetic corpus generated by code in the repository: multitracks rendered from MIDI with permissively licensed real-instrument samples and impulse responses, with exactly known ground truth (pan, onset offsets, swing ratio, ghost velocities, fade shapes, reverb decay, doubling, harmony counts, gaps, compression settings). Stems MUST also be passed through the separator so tests measure end-to-end error, not just clean-stem error.
- **REQ-VAL-02** Every analyzer MUST have conformance tests with the accuracy targets in its METRICS.md entry. CI MUST run them on every change to an analyzer, stage or weight file.
- **REQ-VAL-03** Passing the synthetic suite is necessary but not sufficient for `beta` or `stable`.

### 11.3 Metric maturity

| Level | Entry criteria | Effect |
|---|---|---|
| `experimental` | Analyzer exists and passes unit tests. | Hidden from the agent unless asked for by metric ID. Max class `ESTIMATED` or `PROXY`. |
| `beta` | Meets synthetic targets. One sealed held-out look (evaluation plan §4) meets the `beta` agreement rule in METRICS.md §4.2 with coverage of at least 70%. | Shown to the agent. Max class `ESTIMATED`. |
| `stable` | Meets the `stable` agreement rule on the sealed held-out set and again on a fresh confirmation set of tracks never used before (evaluation plan §4). No open correctness bugs. | May be labeled `MEASURED` if the ceiling allows. |

- **REQ-VAL-04** Maturity MUST be recorded per metric and per analyzer version in `metrics-maturity.toml` and MUST change only through a reviewed pull request that links the validation report.
- **REQ-VAL-05** A metric whose ceiling is `ESTIMATED`, `PROXY` or `EAR` MUST NOT be labeled `MEASURED`, whatever its maturity.

### 11.4 Regression

- **REQ-VAL-06** A golden set of at least 20 real tracks, owned and run by a maintainer (REQ-SRC-06) and referenced by `pcm_sha256`, MUST be re-run before each release. Any category change, or numeric change beyond tolerance, MUST be explained in the release notes.

### 11.5 Calibration events

- **REQ-VAL-07** When an `EAR` value and an analyzer value for the same metric and asset differ beyond the metric's agreement band, the store MUST record a calibration event. `headphones calibrate report` MUST summarize them per metric using METRICS.md §4.2 statistics and MUST exclude sealed held-out assets until their study closes.

## 12. Evaluation of harness lift

Summary of [docs/evaluation-plan.md](docs/evaluation-plan.md) Study B:

- Two arms on the same held-out tracks: Claude Code without Headphones (web search and the Spotify connector allowed) and with Headphones.
- Ground truth is the listener's ear, captured blind on the station before any analyzer output or agent answer is shown for any study track.
- Primary outcome: balanced accuracy over the benchmark ear set's metrics whose ceiling is `MEASURED` or `ESTIMATED`, each metric weighted equally, harness minus baseline, one-sided 95% lower bound above 10 percentage points. Per-metric results are secondary with Holm correction.
- Secondary: coverage, calibration, rule compliance, invented timestamps, results by text-availability stratum.
- The plan is committed before data collection.

## 13. Security and privacy

Details are in [docs/security-self-assessment.md](docs/security-self-assessment.md) and [docs/privacy.md](docs/privacy.md).

- **REQ-SEC-01** No component may listen on a network interface other than loopback. The only loopback listener permitted is the optional browser UI (REQ-LS-03). The station socket is a user-only local socket (REQ-LS-12).
- **REQ-SEC-02** Text from tags, file names and AcoustID MUST be treated as untrusted (REQ-MCP-03, REQ-LS-18, REQ-REND-01).
- **REQ-SEC-03** Weights MUST be verified by SHA-256 before load and loaded only from `safetensors`, or from verified ONNX or TFLite files through their runtimes (REQ-WGT-01 to 03). Pickle-based formats MUST NOT be loaded.
- **REQ-SEC-04** Media decoding MUST follow REQ-ING-02 and REQ-RES-01.
- **REQ-SEC-05** Headphones MUST NOT include telemetry or crash reporting that sends data off the machine.
- **REQ-SEC-06** Releases MUST be signed with Sigstore and carry SLSA provenance at build level 2 or higher and an SBOM (REQ-LIC-03). `headphones init` and upgrade instructions MUST verify the signature.
- **REQ-SEC-07** Logs MUST NOT contain tag text, ear notes, stated text, history fields or device labels at any verbosity. Paths MAY appear only at debug verbosity, and `doctor` MUST flag when debug logs exist. Logs MUST rotate, keeping 30 days by default.

## 14. Observability

- **REQ-OBS-01** Every analysis run MUST produce a run manifest: inputs, stages run or cached, timings, analyzer versions, weight hashes, warnings and errors.
- **REQ-OBS-02** Logs MUST be structured (JSON Lines), local, and follow REQ-SEC-07.
- **REQ-OBS-03** `headphones doctor` MUST report everything needed to reproduce a run elsewhere except the audio, with paths, device labels and asset identity redacted unless `--unredacted` is given.

## 15. Versioning, compatibility and release

### 15.1 Software

Semantic Versioning 2.0.0.

### 15.2 Schemas

Each schema has its own SemVer. Adding optional fields is minor. Removing a field or changing its meaning is major (minor before 1.0).

### 15.3 Metric methods

Each analyzer has its own SemVer. A change that can alter outputs on the conformance or golden sets is at least a minor bump. A change of what a metric means requires a new metric ID or a METRICS.md major revision.

### 15.4 Release process

1. Conformance suite and golden set pass, with changes explained.
2. Every term in §6 re-checked, with the date in the release notes.
3. SBOM generated and licenses checked against ADR-0003. NOTICE updated.
4. Artifacts signed, provenance attached.
5. CHANGELOG updated.
6. Approval from a second maintainer once there are two.

Target cadence: a minor release at most every three months before 1.0, or when a milestone completes.

### 15.5 Deprecation and support

- Before 1.0: a deprecated interface, metric ID or schema field MUST keep working for at least one minor release with a warning.
- From 1.0: at least two minor releases or six months, whichever is longer.
- From 1.0, the latest minor release receives fixes, and the previous minor receives security fixes for six months.

## 16. Governance

Governance is in [GOVERNANCE.md](GOVERNANCE.md). Headphones borrows the shape of CNCF project governance and documentation. It is not a CNCF project, does not use CNCF maturity labels for its milestones, and makes no claim to meet CNCF criteria. [ROADMAP.md](ROADMAP.md) lists what would be missing if that ever changed.

## 17. Open issues

| ID | Issue | Current handling |
|---|---|---|
| OI-1 | Whether passing the listener's own streaming history to an AI agent breaches the User Guidelines' ban on "ingesting Spotify Content into a machine learning or AI model". The Developer Terms define Spotify Content broadly, including user data. The counter-argument is the listener's data portability right (GDPR Article 20 where it applies). | History and BEHAVIORAL off by default, with a notice quoting the clause (REQ-SPOT-04). Seek clarification from Spotify. |
| OI-2 | Whether the Spotify connector's terms allow its output to sit in the same agent context as Headphones output. | Headphones stores nothing from the connector (REQ-SPOT-02). Re-check at each minor release. |
| OI-3 | Drum transcription model with an allowed license and acceptable accuracy on real recordings. | Selection in M1. Dependent metrics stay `experimental` until resolved. |
| OI-4 | Whether separation biases microtiming beyond the perceptual threshold (about 10 ms). | Measured end to end in the synthetic suite (REQ-VAL-01). |
| OI-5 | Perceptual metrics may have no valid audio proxy. | Ceilings `EAR` or `PROXY`. Study B and C report whether proxies beat chance. |
| OI-6 | Two metric definitions need the listener's confirmation: what "cold end" and "hard stop" mean, and what "chopped" hi-hats mean. | METRICS.md uses working definitions marked *pending listener confirmation*. |
| OI-7 | Whether `htdemucs_6s` separates fiddle, banjo, dobro and mandolin into sensible stems. | Voice gating and timbre novelty across stems (METRICS.md §2.1, F6). Measured in M2. |

## 18. References

- RFC 2119, RFC 8174.
- Spotify Developer Policy, https://developer.spotify.com/policy/ (checked 2026-10-05).
- Spotify Developer Terms, https://developer.spotify.com/terms (checked 2026-10-05).
- Spotify User Guidelines, https://www.spotify.com/us/legal/user-guidelines/ (checked 2026-10-05).
- Spotify Web API February 2026 migration guide and March 2026 changelog, https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide and https://developer.spotify.com/documentation/web-api/references/changes/march-2026 (checked 2026-10-05).
- Spotify newsroom, "Spotify in Claude", 2026-04-23, https://newsroom.spotify.com/2026-04-23/claude-integration/.
- AcoustID web service terms, https://acoustid.org/webservice (checked 2026-10-05).
- Bandcamp terms of use, https://bandcamp.com/terms_of_use.
- ITU-R BS.1770-5, EBU R 128, EBU Tech 3341 and 3342.
- Rouard, Massa, Défossez, "Hybrid Transformers for Music Source Separation", ICASSP 2023.
- Foscarin, Schlüter, Widmer, "Beat this! Accurate beat tracking without DBN postprocessing", ISMIR 2024.
- Bittner et al., "A Lightweight Instrument-Agnostic Model for Polyphonic Note Transcription and Multipitch Estimation", ICASSP 2022.
- Kim et al., "CREPE: A Convolutional Representation for Pitch Estimation", ICASSP 2018.
- Avendano and Jot, "A frequency-domain approach to multichannel upmix", JAES 2004.
- Model Context Protocol specification 2025-11-25, https://modelcontextprotocol.io/specification.
- Claude Code plugins reference, https://code.claude.com/docs/en/plugins-reference.
- Claude vision documentation, https://platform.claude.com/docs/en/build-with-claude/vision.
- CNCF TAG Security self-assessment template (archived 2025-12-18), https://github.com/cncf/tag-security/blob/main/community/assessments/guide/self-assessment.md.
- CNCF TOC process, https://github.com/cncf/toc/tree/main/process.

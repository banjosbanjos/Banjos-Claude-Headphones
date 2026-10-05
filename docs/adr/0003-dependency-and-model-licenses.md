# ADR-0003: Dependency and model license allowlist

- Status: Accepted, amended in 0.2.0
- Date: 2026-10-05

## Context

Headphones is Apache-2.0. Many music information retrieval tools carry licenses that conflict with that or forbid commercial use. Essentia is AGPL-3.0. madmom's code is BSD but its pretrained models are CC BY-NC-SA 4.0. Some reference packages pull in LGPL libraries: librosa needs `soundfile`, whose wheels bundle libsndfile (LGPL-2.1+), and Demucs imports `lameenc` (LGPL-3.0+).

## Decision

### Allowed without review

Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, PSF-2.0, Zlib, Unlicense, CC0-1.0. For model weights and data also CC-BY-4.0.

### Allowed as dynamically loaded, unmodified, user-replaceable libraries

LGPL-2.1-or-later and LGPL-3.0-or-later shared libraries (for example libsndfile through `soundfile`, `lameenc`). Static linking is not allowed. The NOTICE file names them and where their source is.

### Allowed as separate executables only (invoked as a process over command line or IPC)

GPL-2.0-or-later, GPL-3.0-or-later, LGPL, MPL-2.0. This covers FFmpeg (LGPL or GPL builds, including `--enable-version3`), mpv, and Chromaprint's `fpcalc` (LGPL-2.1 because it includes FFmpeg code, or GPL when built with FFTW3). FFmpeg builds with `--enable-nonfree` are not allowed. Headphones uses the system's copies. If the project ever bundles these binaries, it takes on the source-offer duties of their licenses.

### Allowed only as optional, off-by-default plugins (SPEC REQ-LIC-02)

Non-commercial licenses, for example CC BY-NC and CC BY-NC-SA weights.

### Not allowed

AGPL-3.0, licenses without an OSI or Creative Commons approved text, and unlicensed weights.

### Reference components

| Component | Use | License | Training data notes | Status |
|---|---|---|---|---|
| Demucs, `htdemucs_6s` | Separation | MIT | MUSDB18-HQ (non-commercial research license) plus about 800 internal songs | Allowed. Data restriction recorded in the SBOM. |
| beat_this | Beat grid | MIT | The authors note some training files are fully copyrighted | Allowed. Note recorded. |
| Basic Pitch | Polyphonic notes | Apache-2.0 | | Allowed |
| torchcrepe | f0 | MIT (weights converted from marl/crepe, MIT) | | Allowed |
| librosa | Features | ISC (pulls in libsndfile, LGPL, dynamic) | | Allowed |
| pyebur128 / libebur128 | Loudness | MIT | | Allowed |
| PANNs CNN14 | Event tags, voice gating | Code MIT, weights CC BY 4.0 | AudioSet (YouTube audio) | Allowed with attribution |
| AcoustID data | Identity | MusicBrainz ID mapping public domain, database CC BY-SA 3.0 | | Store IDs and core strings only, with attribution |
| MoisesDB | Separation-quality calibration (validation only) | Check license terms before use | | Validation only, never shipped |
| Dagstuhl ChoirSet | Harmony validation | Check license terms before use | | Validation only, never shipped |
| Drum transcription model | Drums | To be chosen (SPEC OI-3) | | Pending |
| madmom models, All-In-One | Beats, structure | CC BY-NC-SA weights | | Optional plugin only |
| Essentia | Features | AGPL-3.0 | | Not allowed |

### Attribution

Every component that requires attribution (Apache-2.0 NOTICE content, CC BY, CC BY-SA) is listed in the repository's NOTICE file (SPEC REQ-LIC-04).

## Consequences

Some strong MIR models are excluded from the core. Where that costs accuracy, the gap is documented in METRICS.md and the evaluation reports.

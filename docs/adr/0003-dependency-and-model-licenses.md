# ADR-0003: Dependency and model license allowlist

- Status: Accepted
- Date: 2026-10-05

## Context

Headphones is Apache-2.0. Many music information retrieval tools carry licenses that conflict with that or forbid commercial use. Examples: Essentia is AGPL-3.0. madmom's code is BSD but its pretrained models are CC BY-NC-SA 4.0. Some datasets used to train models are research-only. A personal project still benefits from staying clean, because it keeps the option of others using it.

## Decision

### Allowed without review

Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, PSF-2.0, Zlib, Unlicense, CC0-1.0. For model weights also CC-BY-4.0.

### Allowed as separate executables only (invoked as a process, not linked or imported)

LGPL-2.1-or-later, LGPL-3.0, GPL-2.0-or-later (FFmpeg in a GPL build, mpv), MPL-2.0. Chromaprint's `fpcalc` (LGPL-2.1) falls here.

### Allowed only as optional, off-by-default plugins (SPEC REQ-LIC-02)

Non-commercial licenses, for example CC BY-NC and CC BY-NC-SA weights. They MUST be installed separately and labeled.

### Not allowed

AGPL-3.0 and any license without an OSI or Creative Commons approved text. Unlicensed weights.

### Reference components and their status

| Component | Use | License | Status |
|---|---|---|---|
| Demucs (code and htdemucs_6s weights) | Separation | MIT | Allowed |
| beat_this (code and weights) | Beat grid | MIT | Allowed |
| Basic Pitch | Polyphonic notes | Apache-2.0 | Allowed |
| torchcrepe | f0 | MIT | Allowed. Weight license to be confirmed at pinning. |
| librosa | Features | ISC | Allowed |
| pyloudnorm | Loudness | MIT | Allowed |
| PANNs | Event tags | Code MIT. Weights to be confirmed at pinning. | Pending |
| Drum transcription model | Drums | To be chosen (SPEC OI-3) | Pending |
| madmom models, All-In-One (depends on madmom models) | Beats, structure | CC BY-NC-SA weights | Optional plugin only |
| Essentia | Features | AGPL-3.0 | Not allowed |

Training data licenses are recorded in the SBOM where known. Weights trained on research-only datasets are flagged in the SBOM so users can judge for themselves.

## Consequences

Some of the best available MIR models are excluded from the core. Where that costs accuracy, the gap is documented in METRICS.md and the evaluation reports.

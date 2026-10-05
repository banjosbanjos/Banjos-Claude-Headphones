# Roadmap

Each milestone ends with something the listener can use. Project-hygiene items (signing, SBOM, fuzzing) are tracked separately so they never hold back a useful release.

## M0 Specification (this release)

- [x] SPEC, METRICS, schemas with examples and checker, evaluation plan, security self-assessment, privacy, ADRs, governance.
- [x] Ten adversarial reviews, findings fixed ([docs/reviews/adversarial-reviews.md](docs/reviews/adversarial-reviews.md)).
- [ ] Listener confirms the two open definitions (SPEC OI-6): cold end versus hard stop, and chopped hi-hats.
- [ ] Listener approves the spec.
- [x] Sourcing helper `tools/find_sources.py` and [sourcing guide](docs/sourcing-guide.md), usable today.
- [ ] Listener decides on [HEP-0001](docs/heps/0001-sourcing.md) (built-in `headphones want`). If accepted, it lands in M1.

## M1 First useful version

Exit: the listener can listen, mark moments, and ask Claude about owned tracks with real measurements.

- Ingest, identity (opt-in lookup), evidence store, run manifests, `doctor`.
- Station with latency calibration, taps, Quick Ear form, external playback mode.
- Separation, beat grid, swing and meter, loudness, stereo, stem activity.
- Signal metrics: `space.width`, `structure.ending`, `attack.air`, `feel.space_before_drop`, `feel.dynamic_breathing`.
- **Partial BUILD and FEEL report**: duration and measured tempo against the stated range (B5, B1), vocal pan (part of B4), Quick Ear answers for B1, B3, B4 and B5, and FEEL F1, F2, F6 and F7 from the stem timeline. Everything else shows as `unknown`.
- **Control-group study, ear part** (evaluation plan §7.3), which needs no purchases.
- MCP server read tools, the plugin and skill, CLI JSON schemas (SPEC REQ-CLI-01).
- Synthetic corpus generator. Drum transcription model chosen (SPEC OI-3).
- Tap accuracy shown to meet SPEC REQ-LS-02 by the evaluation plan §8 procedure.

## M2 Groove and texture

- Reference pulse and microtiming, with the separation-bias study (SPEC OI-4).
- All groove and attack metrics, `space.room_sound`, `space.stereo_placement`, `space.clarity_under_load`, `space.compression_pumping`.
- Renders: microtiming, stem_activity, stereo_field, decay.
- Exit: synthetic targets met and ear capture for Study A complete. First held-out look happens here (evaluation plan §4), never on the calibration split.

## M3 Vocal and structure

- Vocal metrics with voice gating, structure metrics, all proxies.
- Full BUILD and FEEL, artist-level routing.
- Exit: Study A held-out report published.

## M4 Evidence of value

- Study B (harness lift), Study C (chills, including detectors on the control group), Study D if history is enabled.
- Exit: reports published, positive or negative.

## 1.0

- Stable MCP tool surface and schema 1.0.
- Every metric at its achievable maturity, gaps documented.

## Project hygiene track (alongside, never blocking)

- Signed releases with SLSA provenance and SBOM from the first tagged release.
- OpenSSF Best Practices badge (passing) and Scorecard.
- Ingest fuzzing before 1.0.
- Security self-assessment refreshed at 1.0.

## Listener actions (need repository owner rights)

- Turn on GitHub private vulnerability reporting (currently off).
- Turn on GitHub Discussions (currently off) as the public channel.
- Add a security contact email to SECURITY.md and a conduct contact to CODE_OF_CONDUCT.md before outside contributions.
- Merge to `main` so GitHub can see LICENSE, SECURITY and CODE_OF_CONDUCT.
- Register an AcoustID application key for the project.

## If this were ever proposed to the CNCF

Headphones does not use CNCF maturity labels. A Sandbox application would also need a reusable project with working code, an organization column in MAINTAINERS, and acknowledgment of the CNCF IP and trademark policies. Incubation would add independent adopters with interviews, the OpenSSF Best Practices passing badge, a public channel and contributor ladder in active use, and maintainer affiliations. Graduation would add maintainers from at least two organizations, a third-party security audit and a record of governance in practice. Sources: https://github.com/cncf/toc/tree/main/process.

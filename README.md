# Headphones

**A listening harness that lets Claude Code measure music by its sound, not by what's written about it.**

Status: **Specification draft 0.1.0** (pre-implementation). Nothing in this repository is runnable yet. The documents here define what will be built, how it will be checked, and how the project will be run.

## The problem

Ask a chatbot about a song and it answers from text: reviews, credits, Wikipedia, its own memory of those. It cannot tell you whether the snare sits behind the beat, whether the vocal is double-tracked, how wide the mix is, or the exact second a song gives you chills. None of that is written down anywhere. You only know it by listening.

Spotify used to expose a few computed audio numbers (tempo, "energy", "danceability"). Those endpoints were closed to new apps in November 2024, and the February 2026 changes removed more, including the ISRC codes that identify recordings. Spotify's developer policy also forbids feeding Spotify content into an AI model or analyzing it. So the harness cannot get its ears from Spotify.

## What Headphones does

1. **Listens to audio you own.** DRM-free files you bought (Bandcamp, Qobuz, 7digital and similar stores) or other copies you have the right to use. Spotify audio is never captured. See [ADR-0001](docs/adr/0001-owned-audio-only.md).
2. **Measures what can be measured.** Separates each track into stems (drums, bass, vocals, guitar, piano, other), finds the beat grid, and runs analyzers for 35 listening metrics: pocket, ghost notes, kick and bass lock, stereo placement, width, compression pumping, decay, the half-second of silence before a drop, how the song ends, and more. See [METRICS.md](METRICS.md).
3. **Is honest about how it knows.** Every value carries an evidence class: `MEASURED`, `ESTIMATED`, `PROXY`, `EAR`, `BEHAVIORAL`, `STATED` or `TEXTUAL`. Claude must say which one it is relying on.
4. **Keeps your ears as the final word.** Some things only a person can judge: whether your head moves in the first ten seconds, whether you want it again the moment it ends, the second the chill hits. The harness has a listening station that captures those by key-press, timed to the audio. Claude can ask for an ear score but can never write one.
5. **Connects to Claude Code** through a local MCP server, a skill, and rendered images (spectrograms, timing plots, stereo maps) Claude can look at.
6. **Plugs into the existing BUILD and FEEL tests** from the music profile, so "does this clear 4 of 5" stops being a guess from reviews and becomes a check against the audio.
7. **Proves its own value.** A pre-registered benchmark compares Claude with the harness against Claude without it, using your ear scores as ground truth. See [docs/evaluation-plan.md](docs/evaluation-plan.md).

## Document map

| Document | What it covers |
|---|---|
| [SPEC.md](SPEC.md) | Normative technical specification: architecture, interfaces, evidence model, processing, versioning |
| [METRICS.md](METRICS.md) | Normative catalog of all 35 metrics plus the BUILD and FEEL composites |
| [schemas/evaluation-record.schema.json](schemas/evaluation-record.schema.json) | JSON Schema for the stored result of an analysis |
| [docs/evaluation-plan.md](docs/evaluation-plan.md) | How metrics are validated and how harness lift is measured |
| [docs/security-self-assessment.md](docs/security-self-assessment.md) | Security self-assessment in the CNCF TAG Security format |
| [docs/privacy.md](docs/privacy.md) | What personal data exists, where it lives, how to remove it |
| [docs/adr/](docs/adr/) | Architecture decision records |
| [GOVERNANCE.md](GOVERNANCE.md), [MAINTAINERS.md](MAINTAINERS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) | How the project is run |
| [ROADMAP.md](ROADMAP.md) | Milestones and exit criteria |
| [docs/reviews/adversarial-reviews.md](docs/reviews/adversarial-reviews.md) | The ten adversarial reviews of this spec and what changed because of them |

## License

Apache License 2.0. See [LICENSE](LICENSE).

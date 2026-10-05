# Headphones

**A listening harness that lets Claude Code measure music by its sound, not by what's written about it.**

Status: **Specification draft 0.2.0** (pre-implementation). Nothing here runs yet. These documents define what will be built, how it will be checked, and how the project is run. The draft has been through ten adversarial reviews ([what they found](docs/reviews/adversarial-reviews.md)).

## The problem

Ask a chatbot about a song and it answers from text: reviews, credits, Wikipedia, its own memory of those. It cannot tell you whether the snare sits behind the beat, whether the vocal is double-tracked, how wide the mix is, or the exact second a song gives you chills. None of that is written down. You only know it by listening.

Spotify can't supply the ears either. Its computed audio numbers (tempo, "energy" and the like) were closed to new apps in November 2024, and its terms forbid recording its audio or feeding Spotify content into an AI model.

## What Headphones does

1. **Listens to audio you own.** Files you already have, DRM-free downloads (iTunes Store, Amazon, Bandcamp, Qobuz), or CDs you've ripped. Spotify audio is never captured.
2. **Measures what can be measured.** It splits each track into separate instrument tracks (drums, bass, vocals, guitar, piano, other), finds the beat, and checks 35 listening metrics: pocket, ghost notes, kick and bass lock, stereo placement, width, compression pumping, decay, the half-second of silence before a drop, how the song ends, and the rest. See [METRICS.md](METRICS.md).
3. **Says how it knows.** Every answer is labeled: measured, estimated, a rough proxy, your ear, your play history, something you said, or something reviews say.
4. **Keeps your ears as the final word.** Some things only you can judge: whether your head moves in the first ten seconds, whether you want it again the moment it ends, the second the chill hits. You mark those with single key presses while you listen. Claude can ask you a question but can never fill in your answer.
5. **Runs your BUILD and FEEL tests on the audio,** so "does this clear 4 of 5" stops being a guess from reviews.
6. **Proves whether it helps.** A test compares Claude with Headphones against Claude without it, using your ear as the answer key. See [docs/evaluation-plan.md](docs/evaluation-plan.md).

## What you'll do

1. **Install it on your own computer** (Mac, Linux or Windows). It has to run where your music files and headphones are, not in a cloud session. You can still drive it from your phone with Claude Code Remote Control.
2. **Point it at your music.** `headphones library add ~/Music`. It uses what you already own first.
3. **Buy a few tracks if needed.** The evaluation needs about 120 tracks plus about 40 you've never heard. Expect roughly $150 to $300 if you own none of them already, much less if you do.
4. **Listen in a second terminal.** `headphones station`, then play a track. Tap `c` at a chill, `n` when your head or body moves, `h` when the hook lands, `g` at a gap that hits you, `m` at a kept mistake.
5. **Answer the Quick Ear form** after each track. Eight questions, mostly yes or no, about two minutes.
6. **Ask Claude.** "Is the drummer behind the beat on this?" "Run BUILD and FEEL on this album." Claude shows you what was measured and tells you what to check by ear.

You can also mark chills and answer ear questions while listening on Spotify, without buying anything. Headphones just won't measure that audio.

## A few words used here

| Word | Meaning |
|---|---|
| Stem | One instrument's part, separated out of the finished mix by software |
| Beat grid | Where each beat falls, worked out from the audio |
| Station | The small program in its own terminal that plays music and catches your key presses |
| MCP server | The connector that lets Claude Code ask Headphones for results |
| Ground truth | Your ear answers, used as the answer key when testing whether Headphones is right |
| Pre-registered | The test plan is written and committed before any results exist, so it can't be bent to fit them |

## Document map

| Document | What it covers |
|---|---|
| [SPEC.md](SPEC.md) | The technical specification |
| [METRICS.md](METRICS.md) | All 35 metrics, how each is measured, and the BUILD and FEEL tests |
| [schemas/](schemas/) | Data formats, with examples and a checker (`python3 tools/check_schemas.py`) |
| [docs/evaluation-plan.md](docs/evaluation-plan.md) | How metrics are validated and how the harness's value is measured |
| [docs/security-self-assessment.md](docs/security-self-assessment.md) | Security review in the CNCF TAG Security format |
| [docs/privacy.md](docs/privacy.md) | What personal data exists, where it lives, how to remove it |
| [docs/adr/](docs/adr/) | Decision records |
| [plugin/](plugin/) | The Claude Code plugin (skill, MCP config, recommended permission rules) |
| [GOVERNANCE.md](GOVERNANCE.md), [MAINTAINERS.md](MAINTAINERS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md), [ADOPTERS.md](ADOPTERS.md) | How the project is run |
| [ROADMAP.md](ROADMAP.md), [CHANGELOG.md](CHANGELOG.md) | Milestones and changes |
| [docs/reviews/adversarial-reviews.md](docs/reviews/adversarial-reviews.md) | The ten adversarial reviews and what changed because of them |

## License and trademarks

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Claude is a trademark of Anthropic, PBC. Spotify is a trademark of Spotify AB. This project is independent and is not affiliated with or endorsed by either. The names are used only to describe what the software works with.

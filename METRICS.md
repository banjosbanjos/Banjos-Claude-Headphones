# Headphones Metric Catalog

| Field | Value |
|---|---|
| Document | METRICS.md |
| Version | 0.1.0-draft |
| Status | Normative companion to [SPEC.md](SPEC.md) |
| Date | 2026-10-05 |

BCP 14 key words apply as in SPEC.md §0.

These are the things a spec sheet or streaming metadata cannot tell you. The listener wrote the list. This document says, for each one, what Headphones can measure, how, how well, and what has to come from the listener's ears.

## 1. How to read an entry

Every metric has a stable ID (`area.name`) and these fields:

| Field | Meaning |
|---|---|
| **Question** | The listener's own wording of what the metric asks. |
| **Ceiling** | The strongest evidence class the metric can ever reach (SPEC §5.1, REQ-VAL-05). `MEASURED` means fully computable from the signal. `ESTIMATED` means computable with model error or separation dependence. `PROXY` means only a correlate is computable. `EAR` means only the listener can supply the value, though a proxy may be offered. |
| **Output** | The typed value stored in `value`, and the `category` vocabulary if any. |
| **Method** | How the value is computed, referring to the shared primitives in §2. |
| **Abstain** | Conditions under which the analyzer MUST abstain (SPEC REQ-EVID-06), with reason codes. |
| **Confidence** | How the 0 to 1 confidence is computed. |
| **Validation** | Synthetic accuracy target (SPEC §11.2) and real-track agreement threshold (§4) required for `stable`. |
| **Ear** | The prompt and scale the listening station uses. Ear values use the same category vocabulary so agreement can be computed. |

All numeric thresholds marked *initial* are starting values. They are configuration (SPEC §8.3), are recorded in every evaluation record, and are expected to move during calibration (§4.3).

## 2. Shared primitives

Each primitive is a pipeline stage (SPEC §7.3) with its own version. Metrics refer to these definitions instead of repeating them.

### 2.1 Stems and separation quality

`stems = {drums, bass, vocals, guitar, piano, other}` from the reference separator (SPEC REQ-SEP-01), stereo, 44.1 kHz.

A stem is **active** in a frame (frame = 46.4 ms, hop 23.2 ms) when its RMS is within 30 dB of that stem's 95th-percentile frame RMS over the track and above -60 dBFS. A stem is **present** in the track when it is active in at least 5% of frames.

`sepq[stem]` in 0 to 1: 1 minus the stem's estimated leakage, where leakage is the fraction of the stem's onsets (§2.2) that coincide within 10 ms with stronger onsets in another stem and have a correlated spectral shape. `sepq_mix` is 1 minus the residual energy ratio. Each metric declares a floor. The default floor is 0.6.

Known weakness: the guitar and piano stems of `htdemucs_6s` are less reliable than drums, bass and vocals. Metrics on those stems default to a floor of 0.7.

### 2.2 Onsets

Per-stem onset times from spectral flux with adaptive peak picking, refined to the sample of maximum envelope slope within ±5 ms. Each onset carries a peak level in dBFS and a strength.

### 2.3 Reference pulse and microtiming offsets

Microtiming is meaningless without a reference. Beat trackers already lean toward where the instruments play, so measuring an instrument against the raw tracker output understates its offset.

1. Take beat times from the beat grid (SPEC §7.3.3).
2. For each beat, collect onsets from all present rhythmic stems (drums, bass, guitar, piano, other) within ±70 ms.
3. **Leave-one-out.** When measuring instrument X, exclude X's own onsets. The consensus time for the beat is the median of the remaining onsets. If fewer than two remain, use the tracker beat time and mark that beat `low_support`.
4. Fit a local linear regression of consensus time against beat index over a sliding window of 8 beats. The fitted line is the **reference pulse**. This absorbs gradual tempo drift so that a band speeding up through a chorus is not mistaken for a drummer rushing.
5. The **offset** of an onset is its time minus the nearest reference-pulse position at the relevant subdivision (beat, eighth or sixteenth, chosen by the metric), in milliseconds. Positive means late (behind), negative means early (ahead).

Perceptual note: listeners start to notice asynchrony between instruments at roughly 10 to 20 ms depending on context. Offsets below 5 ms are reported but SHOULD NOT be described to the listener as audible.

Separation and onset detection add timing error. The synthetic suite MUST measure the end-to-end offset error with known ground truth (SPEC OI-4) and every microtiming metric MUST report its value with that error as an interval.

### 2.4 Drum transcription

Kick, snare, hi-hat (closed, open), toms, cymbals, with onset time and velocity estimate, from the drums stem. The model is chosen in milestone M1 under the license allowlist (SPEC OI-3). Until a model reaches `beta`, metrics that depend on drum classes stay `experimental`.

Fallback without a transcription model: frequency-band onsets on the drums stem (kick 40 to 120 Hz, snare body 150 to 300 Hz with crack 1.5 to 5 kHz, hats above 6 kHz). The fallback MUST cap confidence at 0.5.

### 2.5 Pitch

- Monophonic f0 for bass and lead vocal: CREPE (via `torchcrepe`, MIT) with voicing threshold 0.5, 10 ms hop.
- Polyphonic notes for vocal harmony and lead melody: Basic Pitch (Apache-2.0).
- Key and chord estimate: chroma (CQT) template matching. This is coarse and MUST NOT be labeled better than `ESTIMATED`.

### 2.6 Loudness and dynamics

ITU-R BS.1770 / EBU R 128 via `pyloudnorm` (MIT) or equivalent: integrated loudness (LUFS), momentary (400 ms) and short-term (3 s) loudness, loudness range LRA (EBU Tech 3342), true peak (4x oversampled), peak-to-loudness ratio PLR = true peak minus integrated loudness. These are signal measurements and can be `MEASURED` once validated against the EBU Tech 3341 and 3342 test signals.

### 2.7 Stem activity timeline

For each stem, active spans (§2.1) merged across gaps shorter than one beat. Used for reveal, drop-out, new colour, call and response, first sound and payoff.

### 2.8 Structure

Segment boundaries from a self-similarity matrix on beat-synchronous chroma and MFCC features with checkerboard novelty, snapped to downbeats. Labels by heuristic: the most repeated segment family with above-median loudness is `chorus`, the segment immediately before a chorus that differs from the verse family is `pre_chorus`, the first segment is `intro` if it lacks vocals, and so on. Labels are `ESTIMATED` at best. Any metric that needs a label MUST abstain with `no_structure` when the labeler's confidence is below 0.5.

### 2.9 Stereo analysis

Mid M = (L+R)/2, side S = (L−R)/2. Per-band (octave bands 63 Hz to 16 kHz) side-to-mid energy ratio in dB and inter-channel correlation. Per-stem pan index p = (E_R − E_L) / (E_R + E_L) over active frames, from -1 (hard left) to +1 (hard right).

### 2.10 Note envelopes and decay

For an onset in a stem, the envelope is the RMS (5 ms window, 1 ms hop) from the onset until the next onset in that stem or 2 s. **Decay time** is the time from envelope peak to 20 dB below peak. If the next onset arrives before the envelope falls 20 dB, the decay is **censored** at that time. Decay statistics MUST use a censoring-aware estimator (Kaplan-Meier median) so that busy passages do not make long notes look short.

### 2.11 Audio event tagging

An AudioSet-trained tagger (reference: PANNs CNN14, code MIT, weights subject to ADR-0003 check) on 1 s windows for event classes: laughter, speech, cough, breathing, clapping, count-in click. Used only for proxies.

## 3. Render views

Every render follows SPEC REQ-REND-01 and 02. The caption returned with each render states the asset, the time range, axes, units, and what to look for.

| View | Content |
|---|---|
| `spectrogram` | Log-frequency spectrogram of the mix or a chosen stem, with beat grid and section boundaries overlaid. |
| `microtiming` | Per-instrument onset offsets from the reference pulse (§2.3) as strip plots per bar, with the measurement-error band shaded. |
| `stem_activity` | One lane per stem showing active spans (§2.7), with section labels and taps. |
| `stereo_field` | Pan index and loudness per stem as a left-to-right map, plus per-band side-to-mid ratio. |
| `loudness` | Momentary and short-term loudness over time, LRA band, sections, gaps found by `feel.space_before_drop`. |
| `structure` | Self-similarity matrix with segment boundaries and labels. |
| `decay` | Envelope overlays of representative hits per stem, with decay times marked. |
| `pitch` | Bass and lead f0 contours with detected harmony voices. |

## 4. Agreement, ear scales and calibration

### 4.1 Ear scales

- **Categorical metrics** use the metric's category vocabulary plus `not_sure`.
- **Yes or no metrics** use `yes`, `no`, `not_sure`.
- **Timestamp metrics** use taps (SPEC REQ-LS-04).
- **Degree metrics** use a 5-point labeled scale defined in the entry.

### 4.2 Agreement statistics

| Value type | Statistic | Stable threshold (initial) |
|---|---|---|
| Ordinal category (3 levels) | Quadratic-weighted Cohen's kappa | ≥ 0.60 |
| Nominal category | Cohen's kappa | ≥ 0.60 |
| Yes or no | Cohen's kappa and balanced accuracy | kappa ≥ 0.60 |
| Timestamp | Hit rate: analyzer event within ±1.0 s of an ear tap, and false-alarm rate per minute | hit rate ≥ 0.70 with false alarms ≤ 1 per minute |
| Numeric vs ordinal ear | Spearman rank correlation | ≥ 0.50 |

All statistics MUST be reported with bootstrap 95% confidence intervals and the sample size. A metric meets its threshold only when the lower bound of the interval clears it. With one listener and tens of tracks the intervals are wide, and this rule keeps the project from promoting a metric on luck. `not_sure` answers are excluded from agreement and counted separately.

### 4.3 Calibration of thresholds

Category thresholds MAY be tuned on a calibration split of the listener's ear data and MUST then be frozen before agreement is measured on a separate held-out split ([docs/evaluation-plan.md](docs/evaluation-plan.md) §4). Tuning and testing on the same tracks is forbidden.

## 5. Composites

These come from the listener's profile (the *Two Tests* document). Headphones evaluates them. It does not redefine them.

### 5.1 BUILD (predicts replays, per the profile)

Each criterion is `pass`, `fail` or `unknown` (SPEC REQ-COMP-02), with the evidence class of its weakest input.

| # | Profile wording | Evaluated as |
|---|---|---|
| B1 | Drums dry and close-miked, at the front of the mix, strict grid around 100 to 126 BPM | `space.room_sound` = `dead_close` AND drum prominence (drums stem short-term loudness minus mix, median over drum-active frames) ≥ -6 LU *(initial)* AND `attack.hand_played_feel` timing spread ≤ 12 ms *(initial)*. Tempo reported against the stated range but not used to fail (SPEC REQ-COMP-03). |
| B2 | Sound from attack, struck and plucked, short decay, nothing built on sustained tone | `attack.decay_length` category `short` AND sustained-tone share < 25% *(initial)*, where sustained-tone share is the fraction of mix energy in frames where pitched stems are active but have had no onset in the previous 500 ms. |
| B3 | Parts separable, every instrument nameable by ear | `space.clarity_under_load` category `clear`. |
| B4 | Vocal centred, dry, unprocessed, clearly enunciated | Vocal pan \|p\| ≤ 0.15 AND `vocal.proximity` = `close` AND vocal stem reverberance low (§2.10 applied to vocal phrase ends) AND no pitch-correction signature (f0 transitions shorter than 15 ms between stable notes on more than 30% of transitions, *initial*). Diction is never computed (no-lyrics rule). B4 reports `diction: verify_by_ear` and is `pass` only if the listener's ear confirms diction, otherwise at best `unknown`. |
| B5 | Hook inside 5 seconds, total length under 4:30 | Duration < 270 s (`MEASURED`) AND hook onset ≤ 5 s, where hook onset is the listener's `h` tap on a first listen (`EAR`) or, failing that, the `structure.hook_stickiness` proxy's first-occurrence time (`PROXY`). |

### 5.2 FEEL (vocabulary for chills, untested as a predictor)

Each move is detected with timestamps. Count = number of distinct moves with at least one detection. The profile treats 3 or more as "chills territory" but notes there has been no control group. Headphones reports the count and MUST NOT call it a prediction until [docs/evaluation-plan.md](docs/evaluation-plan.md) Study C says otherwise.

| # | Move | Detector (all `ESTIMATED` unless stated) |
|---|---|---|
| F1 | Reveal: texture assembles, bare to full | Number of active stems rises from ≤ 2 to ≥ 4 within 16 bars through at least two separate entries. |
| F2 | Drop-out: everything falls away, one element exposed | At least two stems that were active go inactive for ≥ 1 bar while one or two stems continue, and at least one returns afterwards. |
| F3 | Second voice: one voice becomes two | Vocal voice count (§2.5 polyphonic on vocals stem) goes from 1 to ≥ 2 and holds for ≥ 2 beats, or a doubling onset is detected by `vocal.doubling`. |
| F4 | Lift: melody climbs and holds at the top of the range | Lead f0 enters the top 10% of its range for the track after a rise of ≥ 5 semitones over ≤ 4 bars and stays there ≥ 1 s. |
| F5 | Harmonic turn: an unexpected chord or key change | Chord estimate outside the estimated key, or a key change, held ≥ 1 beat. `PROXY`, because the chroma method (§2.5) is coarse and "unexpected" is perceptual. |
| F6 | New colour: an instrument timbre not there before | A stem becomes active for the first time after the first 20 s, or a timbre cluster (MFCC k-means within the `other` stem) appears for the first time after 20 s. |
| F7 | Surge: density and volume arrive at once | Short-term loudness rises ≥ 4 LU *(initial)* within 2 beats while onset density rises ≥ 50%. |

### 5.3 Routing

As in the profile: BUILD ≥ 4 known passes and FEEL ≥ 3 → new anchor artist. BUILD ≥ 4 only → rotation. FEEL ≥ 3 only → resonance playlist. Neither → skip. If unknown criteria could change the route, the route is reported as `undetermined` with the criteria that would decide it.

## 6. Catalog

### Groove and pocket

#### `groove.pocket` · Pocket
- **Question:** Does the drummer sit on, ahead of, or behind the beat?
- **Ceiling:** `ESTIMATED`
- **Output:** `{snare_backbeat_ms: {median, iqr, ci95}, kick_ms: {...}, hihat_ms: {...}, bass_ms: {...}, n_bars}`. Category: `ahead`, `on`, `behind`.
- **Method:** Offsets (§2.3, beat subdivision) of snare hits on backbeats, kick hits on beats, hats on eighths, and bass onsets on beats. Category from snare backbeat median: < -8 ms `ahead`, > +8 ms `behind`, else `on` *(initial)*. If the interval from §2.3 straddles a threshold, the category is reported with confidence ≤ 0.5.
- **Abstain:** `no_drums` (drums stem not present), `low_separation` (sepq[drums] < 0.6), `no_backbeat` (fewer than 16 snare backbeats found), `low_support` (more than 30% of beats low-support).
- **Confidence:** min(sepq[drums], fraction of beats with full support), reduced by the share of the interval overlapping a threshold.
- **Validation:** synthetic offsets from -40 to +40 ms: median absolute error ≤ 3 ms. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the drummer feel like they're pushing ahead, sitting right on it, or laying back?" `ahead`, `on`, `behind`.

#### `groove.felt_tempo` · Felt tempo
- **Question:** How fast does it feel versus the actual BPM?
- **Ceiling:** `ESTIMATED` for the computed relation. The ear value is a tapped tempo.
- **Output:** `{bpm, bpm_ci95, felt_bpm_estimate, relation}`. Category (relation): `half`, `same`, `double`.
- **Method:** `bpm` is the median of 60 / inter-beat intervals of the reference pulse. Felt tempo: if the snare accents only beat 3 of 4 (half-time feel) the relation is `half`. If the dominant accented subdivision (hats or snare) runs at twice the beat rate with accents on every eighth, `double`. Otherwise `same`.
- **Abstain:** `no_pulse` (beat tracker confidence below 0.4 for more than 50% of the track).
- **Confidence:** Beat tracker confidence times accent-pattern clarity.
- **Validation:** `bpm` within 1% on synthetic. Relation: kappa ≥ 0.60 against ear.
- **Ear:** "Tap along with the beat you feel." The station records at least 8 taps and stores the tapped BPM. The relation is computed from tapped BPM / measured BPM (≈0.5, ≈1, ≈2).

#### `groove.ghost_notes` · Ghost notes
- **Question:** Are there quiet snare taps between the main hits?
- **Ceiling:** `ESTIMATED`
- **Output:** `{ghosts_per_bar, ghost_level_db_below_accent, n_bars, examples: [timestamps]}`. Category: `none`, `some`, `lots`.
- **Method:** Snare onsets (§2.4) whose peak level is 10 to 35 dB below the median backbeat level and that fall on non-backbeat sixteenth positions. Category: < 0.25 per bar `none`, 0.25 to 1.5 `some`, > 1.5 `lots` *(initial)*.
- **Abstain:** `no_drums`, `low_separation`, `no_transcription` (no drum model at `beta`, see SPEC OI-3).
- **Confidence:** sepq[drums] times transcription model's snare precision on the synthetic suite.
- **Validation:** synthetic ghost velocities 10 to 40 (MIDI): F1 ≥ 0.75 for detection. Real: weighted kappa ≥ 0.60.
- **Ear:** "Can you hear quiet snare taps between the main hits?" `none`, `some`, `lots`.

#### `groove.hihat_articulation` · Hi-hat articulation
- **Question:** Open, closed, or chopped?
- **Ceiling:** `ESTIMATED`
- **Output:** `{share_closed, share_open, share_chopped, n_hits}`. Category: the majority class, or `mixed` when none exceeds 50%.
- **Method:** For each hat hit, decay time (§2.10) on the hat band of the drums stem. `closed` < 80 ms. `open` > 250 ms with natural decay. `chopped` is an open-hat timbre (broadband wash above 6 kHz) cut off abruptly (energy falls ≥ 20 dB within 20 ms) between 80 and 250 ms *(initial)*.
- **Abstain:** `no_drums`, `low_separation`, `no_hats` (fewer than 32 hat hits).
- **Confidence:** sepq[drums] times mean classifier margin.
- **Validation:** synthetic labeled hits: macro F1 ≥ 0.75. Real: kappa ≥ 0.60.
- **Ear:** "How do the hi-hats sound?" `closed` (tight ticks), `open` (washy), `chopped` (open then cut short), `mixed`.

#### `groove.kick_bass_lock` · Kick and bass lock
- **Question:** Do they hit as one?
- **Ceiling:** `ESTIMATED`
- **Output:** `{coincidence_rate, median_abs_offset_ms, n_kicks}`. Category: `locked`, `loose`, `independent`.
- **Method:** Fraction of kick onsets with a bass onset within ±30 ms, and the median absolute offset of those pairs. `locked`: rate ≥ 0.6 and median ≤ 15 ms. `independent`: rate < 0.3. Otherwise `loose` *(initial)*.
- **Abstain:** `no_drums`, `no_bass`, `low_separation` (either stem below 0.6).
- **Confidence:** min(sepq[drums], sepq[bass]).
- **Validation:** synthetic: rate error ≤ 0.05, offset error ≤ 3 ms. Real: weighted kappa ≥ 0.60.
- **Ear:** "Do the kick drum and bass hit together like one instrument?" `locked`, `loose`, `independent`.

#### `groove.fill_restraint` · Fill restraint
- **Question:** Fills only where needed?
- **Ceiling:** `ESTIMATED`
- **Output:** `{fills_per_minute, share_at_boundaries, fills: [timestamps]}`. Category: `restrained`, `moderate`, `busy`.
- **Method:** A fill is a bar where drum onset density or tom and snare activity exceeds 1.8 times the median of the four preceding bars. Boundary fills are those in the last bar before a section boundary (§2.8). `restrained`: ≤ 1 fill per minute and ≥ 70% at boundaries. `busy`: > 3 per minute or < 40% at boundaries *(initial)*.
- **Abstain:** `no_drums`, `low_separation`. If structure is unavailable, `share_at_boundaries` is null and the category uses rate only, with confidence capped at 0.5.
- **Confidence:** sepq[drums] times structure confidence.
- **Validation:** synthetic fill placement: F1 ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the drummer only fill where it's needed?" `restrained`, `moderate`, `busy`.

#### `groove.head_nod` · Head-nod test
- **Question:** Does your body move within 10 seconds?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `{moved: yes|no, at_s}` from an `n` tap during the first play.
- **Output (proxy):** `{time_to_stable_pulse_s, pulse_clarity}` with `proxy_for: "groove.head_nod"`. Time to stable pulse is the first time from which beat tracker confidence stays above 0.6 for 4 consecutive beats and low-frequency (kick plus bass) onset strength is above its track median.
- **Abstain (proxy):** `no_pulse`.
- **Validation:** proxy: report the balanced accuracy of "stable pulse ≤ 10 s" as a predictor of ear `yes`. The proxy is never promoted above `PROXY`.
- **Ear:** First listen only. "Tap N when your head starts moving." No tap within 10 s records `no`. Repeat listens are recorded but flagged, because familiarity changes the answer.

### Attack and texture

#### `attack.snare_character` · Snare character
- **Question:** Crack, thud, or slap?
- **Ceiling:** `ESTIMATED`
- **Output:** `{centroid_hz, crack_ratio_db, body_ratio_db, decay_ms, n_hits}`. Category: `crack`, `thud`, `slap`.
- **Method:** Averaged spectrum and envelope of snare backbeat hits. Crack ratio: energy 1.5 to 5 kHz relative to 150 to 300 Hz. `crack`: crack ratio ≥ +3 dB and decay ≥ 120 ms. `thud`: crack ratio ≤ -6 dB. `slap`: decay < 120 ms with energy concentrated 400 Hz to 1.5 kHz *(initial)*. Thresholds are expected to need calibration more than most.
- **Abstain:** `no_drums`, `low_separation`, `no_backbeat`.
- **Confidence:** sepq[drums] times classifier margin.
- **Validation:** synthetic snare samples labeled by a panel of at least two people: kappa ≥ 0.6 against the panel. Real: kappa ≥ 0.60 against the listener.
- **Ear:** "What does the snare sound like?" `crack` (sharp, bright, rings), `thud` (low, dull, muffled), `slap` (short, dry, papery).

#### `attack.pick_sound` · Pick sound
- **Question:** Can you hear the pick hit the string?
- **Ceiling:** `ESTIMATED`
- **Output:** `{attack_hf_ratio_db, n_notes}`. Category: `audible`, `subtle`, `none`.
- **Method:** On guitar stem onsets, energy 2 to 8 kHz in the first 15 ms after onset relative to the next 100 ms. `audible` ≥ +6 dB, `none` ≤ 0 dB *(initial)*. Applied to the bass stem too when the bass is picked. Reported separately as `bass_attack_hf_ratio_db`.
- **Abstain:** `no_guitar`, `low_separation` (floor 0.7).
- **Confidence:** sepq[guitar].
- **Validation:** synthetic picked versus fingered samples: balanced accuracy ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "Can you hear the pick click on the strings?" `audible`, `subtle`, `none`.

#### `attack.decay_length` · Decay length
- **Question:** How fast does each note die?
- **Ceiling:** `ESTIMATED`
- **Output:** `{per_stem: {stem: {median_decay_ms, ci95, censored_share}}, mix_median_decay_ms}`. Category: `short`, `medium`, `long`.
- **Method:** §2.10 per stem. The mix category uses the energy-weighted median across present pitched stems and drums: `short` < 250 ms, `long` > 800 ms *(initial)*.
- **Abstain:** per stem when fewer than 20 uncensored notes. Whole metric abstains with `too_dense` when more than 80% of notes are censored.
- **Confidence:** mean sepq over contributing stems times (1 minus censored share).
- **Validation:** synthetic tones with known decay 50 ms to 3 s: median error ≤ 15%. Real: weighted kappa ≥ 0.60.
- **Ear:** "Do notes stop quickly or ring on?" `short`, `medium`, `long`.

#### `attack.air` · Air between notes
- **Question:** Is there silence you can hear inside the groove?
- **Ceiling:** `MEASURED`
- **Output:** `{air_share, median_dip_depth_db, dips_per_bar}`. Category: `dense`, `some_air`, `airy`.
- **Method:** On the mix, 10 ms RMS frames. A dip is a run of frames at least 20 dB below the rolling 2 s 95th-percentile level, lasting at least 30 ms, inside an otherwise active section (not intro silence or the tail). `air_share` is the fraction of in-section time in dips. `dense` < 2%, `airy` > 10% *(initial)*.
- **Abstain:** none, apart from `too_short` (under 30 s of active audio).
- **Confidence:** 1.0 for the measurement. The category confidence falls near thresholds.
- **Validation:** synthetic gaps of known length: share error ≤ 0.5 percentage points. Real: weighted kappa ≥ 0.60.
- **Ear:** "Can you hear little gaps of silence inside the groove?" `dense`, `some_air`, `airy`.

#### `attack.hand_played_feel` · Hand-played feel
- **Question:** Small human wobble or a perfect machine grid?
- **Ceiling:** `ESTIMATED`
- **Output:** `{timing_spread_ms, tempo_drift_pct, grid_locked_share}`. Category: `machine`, `tight_human`, `loose_human`.
- **Method:** `timing_spread_ms` is the robust standard deviation (1.4826 × median absolute deviation) of drum onset offsets (§2.3, sixteenth subdivision). `tempo_drift_pct` is the standard deviation of the local tempo over 8-beat windows as a percentage of mean tempo. `grid_locked_share` is the fraction of onsets within ±2 ms of a single constant-tempo grid fitted to the whole track. `machine`: grid_locked_share ≥ 0.8 and drift < 0.2%. `loose_human`: spread > 15 ms. Else `tight_human` *(initial)*.
- **Abstain:** `no_drums` and no other rhythmic stem present, `low_separation`.
- **Confidence:** sepq of stems used, minus a penalty if spread is within the end-to-end measurement error from §2.3.
- **Validation:** synthetic quantized versus humanized (Gaussian jitter 2 to 25 ms, drift 0 to 3%): category accuracy ≥ 0.85. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does it feel played by hands or locked to a machine?" `machine`, `tight_human`, `loose_human`.

#### `attack.guitar_tone` · Guitar tone
- **Question:** Bright and thin, or warm and round?
- **Ceiling:** `ESTIMATED`
- **Output:** `{centroid_hz, body_ratio_db, tilt_db_per_octave}`. Category: `bright_thin`, `balanced`, `warm_round`.
- **Method:** On active guitar stem frames: spectral centroid, energy 100 to 400 Hz relative to 2 to 6 kHz (body ratio), and spectral tilt from a line fit over octave bands. `bright_thin`: centroid > 2.5 kHz and body ratio < -6 dB. `warm_round`: centroid < 1.2 kHz and body ratio > 0 dB *(initial)*.
- **Abstain:** `no_guitar`, `low_separation` (floor 0.7).
- **Confidence:** sepq[guitar] times classifier margin.
- **Validation:** synthetic amp and EQ settings: category accuracy ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "How does the guitar sound?" `bright_thin`, `balanced`, `warm_round`.

### Space and mix

#### `space.room_sound` · Room sound
- **Question:** Dead and close, or live and roomy?
- **Ceiling:** `ESTIMATED`
- **Output:** `{drum_c50_db, vocal_c50_db, tail_ms}`. Category: `dead_close`, `medium`, `live_roomy`.
- **Method:** On isolated snare hits (no other drum onset within 300 ms) in the drums stem, the clarity index C50 = 10·log10(energy 0 to 50 ms after onset / energy 50 to 300 ms). Same on vocal phrase ends. `dead_close`: drum C50 ≥ 10 dB. `live_roomy`: ≤ 3 dB *(initial)*. This measures reverberance, not the physical room. Artificial reverb counts.
- **Abstain:** `no_drums` and `no_vocals`, `no_isolated_hits` (fewer than 8).
- **Confidence:** sepq[drums] times share of isolated hits.
- **Validation:** synthetic convolution with impulse responses of known clarity: C50 error ≤ 2 dB. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does it sound like a small dead room, close up, or a big live room?" `dead_close`, `medium`, `live_roomy`.

#### `space.stereo_placement` · Stereo placement
- **Question:** Where does each instrument sit left to right?
- **Ceiling:** `ESTIMATED`
- **Output:** `{per_stem: {stem: {pan, spread}}}`, where `spread` is the standard deviation of frame-wise pan. No category. Rendered by `stereo_field`.
- **Method:** §2.9 per present stem. Hard-panned doubled guitars appear as a guitar stem with pan near 0 and high spread. The analyzer reports `split_pair: true` when the frame-wise pan distribution is bimodal with modes beyond ±0.5.
- **Abstain:** `mono_source`. Per stem, `low_separation`.
- **Confidence:** per stem sepq.
- **Validation:** synthetic panned stems: pan error ≤ 0.05. Real: ear placement on a 5-point scale (hard left, left, centre, right, hard right) per named instrument, Spearman ≥ 0.70.
- **Ear:** "Where is the [instrument]?" hard left, left, centre, right, hard right, both sides.

#### `space.width` · Width
- **Question:** Narrow and focused, or spread wide?
- **Ceiling:** `MEASURED`
- **Output:** `{side_to_mid_db, correlation, per_band: [...]}`. Category: `narrow`, `medium`, `wide`.
- **Method:** §2.9 on the mix, energy-weighted across bands from 125 Hz up (low bass is usually mono and would dominate). `narrow`: side-to-mid < -15 dB. `wide`: > -7 dB *(initial)*.
- **Abstain:** `mono_source`.
- **Confidence:** 1.0 for the measurement.
- **Validation:** synthetic mixes with known M/S ratios: error ≤ 0.5 dB. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the mix feel narrow and focused or spread wide?" `narrow`, `medium`, `wide`.

#### `space.clarity_under_load` · Clarity under load
- **Question:** When it's loud, can you still pick out every part?
- **Ceiling:** `ESTIMATED`
- **Output:** `{audible_share_loud, stems_active_loud, masked: [stem]}`. Category: `clear`, `partly_masked`, `smeared`.
- **Method:** Take the loudest 25% of short-term loudness frames. In each, for each active stem, compute per-band (ERB-spaced, 32 bands) excitation and call the stem audible in the frame if, in at least 3 bands, its excitation exceeds the summed excitation of the other stems minus 6 dB *(initial)*. `audible_share_loud` is the mean fraction of active stems audible. `clear` ≥ 0.85. `smeared` < 0.6 *(initial)*.
- **Abstain:** `too_few_stems` (fewer than 3 present), `low_separation` (mean sepq < 0.6).
- **Confidence:** mean sepq of active stems.
- **Validation:** synthetic mixes with controlled masking: category accuracy ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "In the loudest part, can you still pick out every instrument?" `clear`, `partly_masked`, `smeared`.

#### `space.compression_pumping` · Compression pumping
- **Question:** Does the mix breathe or squeeze?
- **Ceiling:** `ESTIMATED`
- **Output:** `{plr_db, lra_lu, kick_synced_dip_db, crest_factor_db}`. Category: `breathes`, `moderate`, `squeezes`.
- **Method:** PLR and LRA from §2.6 (signal measurements). `kick_synced_dip_db`: the average dip in the summed non-drum stems' envelope in the 50 to 250 ms after kick onsets, relative to the 50 ms before, which reveals audible pumping or sidechain ducking. `squeezes`: PLR < 8 dB or dip > 2 dB. `breathes`: PLR > 12 dB and dip < 0.5 dB *(initial)*.
- **Abstain:** `kick_synced_dip_db` null when no drums. Category still computed from PLR and LRA, with confidence capped at 0.6.
- **Confidence:** sepq[drums] for the dip, 1.0 for PLR and LRA.
- **Validation:** synthetic compressor and sidechain settings: dip error ≤ 0.5 dB. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the mix breathe, or does it feel squeezed and pumping?" `breathes`, `moderate`, `squeezes`.

### Vocal

All vocal metrics measure sound only. None of them transcribe, store or use words (SPEC N2, ADR-0004).

#### `vocal.breath` · Breath
- **Question:** Can you hear the singer inhale?
- **Ceiling:** `ESTIMATED`
- **Output:** `{breaths_per_vocal_minute, median_level_db_below_vocal, examples: [timestamps]}`. Category: `audible`, `faint`, `removed`.
- **Method:** In the vocals stem, segments of 100 to 700 ms with low harmonicity (voicing probability < 0.2), broadband noise spectrum centred 1 to 6 kHz, ending within 600 ms before a voiced phrase onset. Cross-checked against the event tagger's breathing class. `audible`: ≥ 4 per vocal minute at ≥ -30 dB relative to vocal. `removed`: < 0.5 per vocal minute *(initial)*.
- **Abstain:** `no_vocals`, `low_separation`.
- **Confidence:** sepq[vocals] times detector precision on synthetic.
- **Validation:** synthetic vocals with breaths inserted and removed: F1 ≥ 0.75. Real: weighted kappa ≥ 0.60.
- **Ear:** "Can you hear the singer breathe in?" `audible`, `faint`, `removed`.

#### `vocal.doubling` · Doubling
- **Question:** One take or stacked takes?
- **Ceiling:** `ESTIMATED`
- **Output:** `{double_share, stereo_double_share, onset_smear_ms}`. Category: `single`, `doubled`, `stacked`.
- **Method:** Over voiced vocal frames: (a) stereo doubling, where vocal stem inter-channel correlation < 0.7 while pan is centred; (b) unison doubling, where the f0 track shows beating or chorus-like jitter (short-term f0 standard deviation 5 to 25 cents beyond the single-voice baseline) and onsets smeared over 10 to 50 ms. `double_share` is the fraction of voiced frames with (a) or (b). `single` < 20%, `stacked` when (a) and (b) both hold on > 40% of frames or harmony count ≥ 3 *(initial)*.
- **Abstain:** `no_vocals`, `low_separation`.
- **Confidence:** sepq[vocals] times detector agreement between (a) and (b).
- **Validation:** synthetic single, double and quad-tracked vocals: macro F1 ≥ 0.75. Real: kappa ≥ 0.60. Starts `experimental`.
- **Ear:** "Is it one voice, a doubled voice, or a stack?" `single`, `doubled`, `stacked`.

#### `vocal.harmony_stacking` · Harmony stacking
- **Question:** How many voices, how tight?
- **Ceiling:** `ESTIMATED`
- **Output:** `{max_voices, median_voices_when_harmonizing, harmony_share, tightness_onset_spread_ms, tightness_cents}`. Category: `none`, `one_harmony`, `stack` (3 or more voices).
- **Method:** Basic Pitch on the vocals stem. A harmony frame has ≥ 2 simultaneous notes at different pitch classes held ≥ 150 ms. Tightness is the median onset spread among voices starting together and the median deviation from just or equal-tempered intervals.
- **Abstain:** `no_vocals`, `low_separation`.
- **Confidence:** sepq[vocals] times note detection confidence.
- **Validation:** synthetic 1 to 4 voice arrangements: voice count accuracy ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "How many voices do you hear singing at once?" `none` (one voice), `one_harmony`, `stack`. Optional: "How tight are they?" `tight`, `loose`.

#### `vocal.proximity` · Proximity
- **Question:** Close to the mic or set back?
- **Ceiling:** `ESTIMATED`
- **Output:** `{vocal_c50_db, proximity_bass_ratio_db, vocal_level_rel_mix_lu}`. Category: `close`, `medium`, `set_back`.
- **Method:** Vocal C50 (as in `space.room_sound`), the 100 to 300 Hz energy relative to 1 to 3 kHz on voiced frames (proximity effect), and vocal stem loudness relative to the mix. `close`: C50 ≥ 10 dB and level ≥ -4 LU. `set_back`: C50 ≤ 4 dB or level ≤ -10 LU *(initial)*.
- **Abstain:** `no_vocals`, `low_separation`.
- **Confidence:** sepq[vocals].
- **Validation:** synthetic close and distant mic simulations: category accuracy ≥ 0.8. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the singer sound right up on the mic or further back?" `close`, `medium`, `set_back`.

#### `vocal.phrasing` · Phrasing
- **Question:** On the beat or floating across it?
- **Ceiling:** `ESTIMATED`
- **Output:** `{on_grid_share, median_abs_offset_ms, n_phrases}`. Category: `on_grid`, `mixed`, `floating`.
- **Method:** Vocal phrase onsets (voiced onsets after ≥ 250 ms unvoiced). Offset to the nearest sixteenth of the reference pulse (§2.3). Also note onsets within phrases. `on_grid_share` is the fraction within ±40 ms. `on_grid` ≥ 0.75. `floating` < 0.45 *(initial)*. Consonants make vocal onsets early and smeared, so the end-to-end error from the synthetic suite MUST be shown.
- **Abstain:** `no_vocals`, `no_pulse`, `low_separation`.
- **Confidence:** sepq[vocals] times beat confidence.
- **Validation:** synthetic vocals placed with known offsets: share error ≤ 0.08. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does the singer land on the beat or float across it?" `on_grid`, `mixed`, `floating`.

### Structure and hook

#### `structure.first_sound` · First sound
- **Question:** What hits you at second one?
- **Ceiling:** `ESTIMATED`
- **Output:** `{leading_silence_s, stems_active_first_1s: [stem], first_1s_loudness_rel_lu, events: [tag]}`. Category: `full_band`, `single_instrument`, `voice`, `drums_only`, `texture_or_effect`.
- **Method:** Find the first frame above -50 dBFS (leading silence). Over the next 1 s, report active stems, the momentary loudness relative to track integrated loudness, and event tags (§2.11). Category: ≥ 3 stems `full_band`, vocals only `voice`, drums only `drums_only`, one pitched stem `single_instrument`, otherwise `texture_or_effect`.
- **Abstain:** none.
- **Confidence:** mean sepq of stems involved.
- **Validation:** synthetic intros: category accuracy ≥ 0.9. Real: kappa ≥ 0.60.
- **Ear:** "What's the first thing you hear?" same categories.

#### `structure.hook_stickiness` · Hook stickiness
- **Question:** Can you hum it after one listen?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `{hummable_after_one: yes|no, hook_at_s}` from the ear form and the `h` tap on first listen.
- **Output (proxy):** `{motif_repeats, first_occurrence_s, motif_span_s}` with `proxy_for: "structure.hook_stickiness"`. From lead vocal f0 (or the most melodic stem when there is no vocal), find the most repeated melodic motif of 1 to 4 bars by self-similarity on pitch-class sequences transposed to a common root. Report repeats and first occurrence.
- **Abstain (proxy):** `no_melody`.
- **Validation:** report correlation of `motif_repeats` with ear yes or no. Never promoted above `PROXY`.
- **Ear:** First listen: tap `h` when the hook lands. After: "Could you hum it now?" `yes`, `no`, `not_sure`. A second check 24 hours later is OPTIONAL and recorded as a separate ear value.

#### `structure.bassline_hummability` · Bassline hummability
- **Question:** Is the bass its own melody?
- **Ceiling:** `ESTIMATED` for melodic activity. The felt answer is ear.
- **Output:** `{pitch_range_semitones, distinct_pitch_classes, interval_entropy_bits, repeated_note_share, rhythmic_independence}`. Category: `root_anchor`, `moving`, `melodic`.
- **Method:** Bass f0 (§2.5) segmented into notes. Interval entropy over note-to-note intervals. Rhythmic independence is 1 minus the kick coincidence rate from `groove.kick_bass_lock`. `melodic`: range ≥ 10 semitones, ≥ 5 pitch classes, entropy ≥ 2.0 bits. `root_anchor`: repeated-note share ≥ 0.6 or ≤ 3 pitch classes *(initial)*.
- **Abstain:** `no_bass`, `low_separation`, `unpitched_bass` (voicing below 0.5 on more than 60% of bass-active frames).
- **Confidence:** sepq[bass] times mean voicing confidence.
- **Validation:** synthetic basslines: range and pitch-class accuracy ≥ 0.9. Real: weighted kappa ≥ 0.60.
- **Ear:** "Could you hum the bassline on its own, like a tune?" `root_anchor` (mostly one note), `moving`, `melodic`.

#### `structure.pre_chorus_tension` · Pre-chorus tension
- **Question:** Does it pull you toward the chorus?
- **Ceiling:** `PROXY`
- **Output:** `{per_transition: [{chorus_at_s, rising_indicators: [name], score}]}` with `proxy_for: "structure.pre_chorus_tension"`.
- **Method:** For the 4 to 8 bars before each detected chorus, slopes of short-term loudness, onset density, spectral centroid, lead pitch height, and stem count. Score is the number of indicators with a positive slope above threshold (0 to 5).
- **Abstain:** `no_structure`, `no_chorus`.
- **Validation:** report Spearman correlation of score with ear rating. Never promoted above `PROXY`.
- **Ear:** "Does the section before the chorus pull you toward it?" 5-point: 1 no pull, 3 some, 5 strong pull.

#### `structure.payoff` · Payoff
- **Question:** Does the chorus deliver what the build promised?
- **Ceiling:** `PROXY` for the computed contrast. The felt answer is ear.
- **Output:** `{per_chorus: [{at_s, loudness_delta_lu, width_delta_db, stem_count_delta, density_delta_pct}]}` with `proxy_for: "structure.payoff"`.
- **Method:** Chorus versus the preceding segment, medians over each.
- **Abstain:** `no_structure`, `no_chorus`.
- **Validation:** report correlation with ear rating. Never promoted above `PROXY`.
- **Ear:** "Did the chorus deliver?" 5-point: 1 letdown, 3 fine, 5 fully delivered.

#### `structure.ending` · Ending
- **Question:** Hard stop, cold end, or fade?
- **Ceiling:** `MEASURED`
- **Output:** `{fade_duration_s, final_drop_db_per_s, tail_ring_s, trailing_silence_s}`. Category: `fade`, `cold_end`, `hard_stop`, `other`.
- **Method:** Work back from the last frame above -60 dBFS. `fade`: short-term loudness falls ≥ 15 LU over ≥ 3 s at a roughly steady rate (linear fit in dB with R² ≥ 0.8) while onsets continue in the falling region. `cold_end`: the band plays a final hit or chord and the sound then decays naturally (no new onsets, smooth envelope decay ≥ 0.4 s). `hard_stop`: the level drops ≥ 30 dB within 50 ms with no natural decay, as from an edit or a cut. `other`: trailing noise, a hidden track, or a spoken outro *(initial thresholds)*.
- **Abstain:** none.
- **Confidence:** 1.0 for the measurements. The category confidence falls near thresholds.
- **Validation:** synthetic endings: category accuracy ≥ 0.95. Real: kappa ≥ 0.70.
- **Ear:** "How did it end?" `fade`, `cold_end` (stops on a last hit and rings out), `hard_stop` (cut off), `other`.

#### `structure.repeat_urge` · Repeat urge
- **Question:** Do you want it again the moment it ends?
- **Ceiling:** `EAR`
- **Output (ear):** `{wanted_again: yes|no}` asked when playback ends, and `replayed_within_60s: bool`, observed if the listener restarts the track on the station.
- **Output (behavioral, off by default per SPEC REQ-SPOT-04):** `{plays, replays_within_1h, skip_rate, completion_rate}` from imported history. `replays_within_1h` counts plays that start within an hour of the end of a previous play of the same recording. `skip_rate` uses the history's skip flag or plays under 30 s.
- **Validation:** none for a proxy, because there is no audio proxy. Behavioral values are reported as context, not as a measurement of the urge.
- **Ear:** "Do you want to hear it again right now?" `yes`, `no`, `not_sure`.

### Feel, deeper

#### `feel.call_and_response` · Call and response
- **Question:** Does one part answer another?
- **Ceiling:** `ESTIMATED`
- **Output:** `{pairs: [{caller, responder, exchanges, at_s: [...]}]}`. Category: `present`, `absent`.
- **Method:** From the stem activity timeline (§2.7), find stem pairs where A's active span ends and B's begins within one beat, B ends and A resumes within one beat, repeated at least 3 times within a section. Phrase lengths of A and B must be within a factor of 2.
- **Abstain:** `too_few_stems`.
- **Confidence:** mean sepq of the pair.
- **Validation:** synthetic arrangements with known exchanges: F1 ≥ 0.8. Real: kappa ≥ 0.60.
- **Ear:** "Does one part answer another?" `present`, `absent`, and optionally which parts.

#### `feel.dynamic_breathing` · Dynamic breathing
- **Question:** Do soft and loud sections trade off?
- **Ceiling:** `MEASURED`
- **Output:** `{lra_lu, transitions: [{at_s, delta_lu}], max_section_contrast_lu}`. Category: `flat`, `some`, `breathing`.
- **Method:** LRA (§2.6). Transitions where the 10 s moving median of short-term loudness changes by ≥ 6 LU *(initial)*. No structure labels needed. `flat`: LRA < 4 LU and no transitions. `breathing`: ≥ 2 transitions in each direction *(initial)*.
- **Abstain:** `too_short`.
- **Confidence:** 1.0 for the measurements.
- **Validation:** synthetic level automation: transition F1 ≥ 0.9, LRA within 0.5 LU of EBU Tech 3342 reference. Real: weighted kappa ≥ 0.60.
- **Ear:** "Does it trade between soft and loud parts?" `flat`, `some`, `breathing`.

#### `feel.kept_mistakes` · Kept mistakes
- **Question:** Is there a flub or laugh left in the take?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `m` taps with optional one-line notes.
- **Output (proxy):** `{candidates: [{at_s, kind, score}]}` with `proxy_for: "feel.kept_mistakes"`. Kinds: `laughter`, `speech`, `count_in`, `timing_outlier` (a single onset more than 3 IQR off the reference pulse while neighbours are tight), `string_noise` (broadband transient on the guitar stem with no pitched onset).
- **Validation:** report precision of the top 3 candidates against `m` taps.
- **Ear:** "Tap M on anything that sounds like a mistake or a moment left in." Free text optional.

#### `feel.space_before_drop` · Space before the drop
- **Question:** Is there a half-second of nothing before a big moment?
- **Ceiling:** `MEASURED`
- **Output:** `{gaps: [{start_s, length_ms, depth_db, rise_lu}]}`. Category: `present`, `absent`.
- **Method:** On the mix, 20 ms frames. A gap is ≥ 150 ms where level is ≥ 20 dB below the median of the previous 2 s, followed within 100 ms by an onset into a passage whose short-term loudness over the next 3 s is at least as loud as the 3 s before the gap. Gaps where one element keeps sounding at reduced level are reported with `depth_db` so near-silences are kept, not dropped.
- **Abstain:** `too_short`.
- **Confidence:** 1.0 for detection. The "big moment" judgment is the listener's.
- **Validation:** synthetic gaps 50 to 800 ms: detection F1 ≥ 0.95, length error ≤ 20 ms. Real: hit rate against listener marks ≥ 0.80.
- **Ear:** Tap `space` on any gap that hit you. Optional: "Was there a moment of silence before a big moment?" `present`, `absent`.

#### `feel.chill_timestamp` · Chill timestamp
- **Question:** The exact second it happens.
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `c` taps with time, latency correction, and listen count (first listen or repeat).
- **Output (proxy):** `{candidates: [{at_s, reasons: [feel_move or event], score}]}` with `proxy_for: "feel.chill_timestamp"`. Candidates come from FEEL move detections (§5.2), loudness surges, new stem entries and gaps from `feel.space_before_drop`, ranked by the number of coinciding reasons.
- **Validation:** Study C in [docs/evaluation-plan.md](docs/evaluation-plan.md): hit rate of top-k candidates against `c` taps, compared with randomly placed candidates at the same density.
- **Ear:** Tap `c` the moment it happens. Taps on repeat listens are kept and flagged.

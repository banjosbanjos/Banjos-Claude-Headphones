# Headphones Metric Catalog

| Field | Value |
|---|---|
| Document | METRICS.md |
| Version | 0.2.0-draft |
| Status | Normative companion to [SPEC.md](SPEC.md) |
| Date | 2026-10-05 |

BCP 14 key words apply as in SPEC.md §0.

These are the things a spec sheet or streaming metadata cannot tell you. The listener wrote the list. This document says, for each one, what Headphones can measure, how, how well, and what has to come from the listener's ears.

## 1. How to read an entry

Every metric has a stable ID (`area.name`). Proxy values use `area.name.proxy` (SPEC REQ-EVID-02). Each entry has these fields:

| Field | Meaning |
|---|---|
| **Question** | The listener's own wording. |
| **Ceiling** | The strongest evidence class the metric can ever reach (SPEC §5.1, REQ-VAL-05). `MEASURED`: fully computable from the signal. `ESTIMATED`: computable with model error or separation dependence. `PROXY`: only a correlate is computable. `EAR`: only the listener can supply it, though a proxy may be offered. |
| **Output** | The typed `value`, and the `category` vocabulary if any. |
| **Method** | How the value is computed, referring to §2. |
| **Abstain** | Reason codes for abstaining (SPEC REQ-EVID-06). |
| **Confidence** | How the 0 to 1 confidence is computed. For `EAR` values it is null (SPEC REQ-EVID-05). |
| **Validation** | Synthetic accuracy target (SPEC §11.2) and the real-track agreement statistic (§4.2). |
| **Ear** | The question, its answer scale and its ear tier (§4.1). |

Defaults that apply to every entry unless it says otherwise:

- **Tolerance** (SPEC REQ-DET-01): categories identical, numeric outputs within the larger of 1% relative or the unit floor (0.5 ms, 0.1 dB, 0.1 LU, 0.01 for ratios and shares, 0.1 BPM).
- **Agreement band** (SPEC REQ-VAL-07): for categories, any mismatch with an ear answer other than `not_sure`. For timestamps, an ear tap with no analyzer event inside the metric's timestamp window (§4.2), or the reverse.
- **Ear-primary**: a metric whose ceiling is `EAR` or `PROXY`. Its ear question is always in the Quick Ear form or the rotating extras.

All thresholds marked *initial* are configuration (SPEC §8.3), are recorded in every record, and are expected to move during calibration on the calibration split only (§4.3).

## 2. Shared primitives

Each primitive is a pipeline stage (SPEC §7.3) with its own version.

### 2.1 Stems, activity and separation quality

`stems = {drums, bass, vocals, guitar, piano, other}` from the reference separator (SPEC REQ-SEP-01), stereo, 44.1 kHz.

**Activity.** Frames are 46.4 ms with 23.2 ms hop. A stem is **active** in a frame when its RMS is within 30 dB of that stem's 95th-percentile frame RMS **and** within 30 dB of the mix RMS in the same frame **and** above -60 dBFS. A stem is **present** when it is active in at least 5% of frames **and** its 95th-percentile RMS is within 30 dB of the mix's 95th-percentile RMS. The mix-relative tests stop separator bleed in an absent stem from counting as a part.

**Voice gating.** Demucs often routes fiddle into the vocals stem and banjo, dobro or mandolin into guitar or other. Vocal metrics MUST use only frames where the event tagger (§2.11) scores the `singing` or `speech` class above 0.5 on the vocals stem. If fewer than 10% of vocals-active frames pass, vocal metrics abstain with `no_singing`.

**Separation quality `sepq`.** Separators leave almost no residual (stems sum to the mix), so a residual-energy measure says nothing. `sepq[stem]` is instead a calibrated estimate of the stem's scale-invariant signal-to-distortion ratio (SI-SDR), mapped to 0 to 1:

1. Leakage evidence: frames where the stem's spectrum is a scaled copy of another stem's spectrum (correlation of log-magnitude spectra ≥ 0.9) while at least 15 dB weaker. Simultaneous but different sounds (a kick and a bass note) do not count, because their spectra differ.
2. Features: share of leakage frames, stem-to-mix energy ratio, spectral flatness of the stem in active frames.
3. A small regression from these features to SI-SDR, fitted on a licensed multitrack validation set run through the separator (candidate: MoisesDB, which has guitar and piano stems, used for validation only and subject to its license terms in ADR-0003). The mapping and its correlation with true SI-SDR MUST be published.
4. `sepq = clip((SI-SDR_estimate − 0 dB) / 12 dB, 0, 1)` *(initial)*.

Each metric declares a floor. Floors MUST be set from the calibration in step 3. Until then the default floor is 0.5, and 0.6 for guitar and piano, which `htdemucs_6s` separates less reliably.

### 2.2 Onsets

Per-stem spectral-flux onsets with hop 128 samples (2.9 ms) and adaptive peak picking, refined to the sample of maximum envelope slope within ±1 hop. Each onset carries peak level (dBFS) and strength. Envelope-slope picking places slow-attack sounds (bowed bass, swelling pads) late. The per-instrument onset bias MUST be measured on the synthetic corpus and subtracted, and the residual error reported per instrument.

### 2.3 Swing, meter and the reference pulse

Microtiming means nothing without a reference, and the reference must know about swing.

1. **Beats** come from the beat grid (SPEC §7.3.3).
2. **Beat confidence** is the mean sigmoid beat activation of `beat_this` at the detected beats over a window, normalized so that the synthetic corpus median is 1.0 and capped at 1. It is used wherever an entry says "beat confidence".
3. **Meter.** From downbeat spacing: beats per bar and whether the meter is duple (2/4, 4/4) or not. Metrics that need a backbeat MUST abstain with `non_duple_meter` in 3/4, 6/8, 7/8 and other non-duple meters, unless the entry gives a fallback.
4. **Swing.** For each 8-bar window, build a histogram of where off-beat onsets fall within the beat (phase 0 to 1). Fit candidate grids: straight 8ths (offbeat at 0.5), swung 8ths with ratio r (offbeat at r/(1+r), r from 1.0 to 3.0), triplets, and straight or swung 16ths. Report `swing_ratio` and the chosen `grid` per window. A 2:1 shuffle has r = 2.0, offbeat at 0.667.
5. **Leave-one-out consensus.** When measuring an instrument X, X is the **transcribed drum class** for drum metrics (for example snare only) or the **stem** for others. For each beat, collect onsets from all other present rhythmic sources within ±min(70 ms, 0.4 × the grid's subdivision interval). The consensus time is their median. Fewer than two contributors marks the beat `low_support` and uses the tracker time.
6. **Reference pulse.** A local linear fit of consensus time against beat index over a sliding 8-beat window. This absorbs gradual tempo drift.
7. **Offset** of an onset is its time minus the nearest position on the chosen (swing-aware) grid of the reference pulse, in ms. Positive is late (behind), negative is early (ahead).
8. **Two views of the drums.** For pocket metrics, report both `vs_drummer` (snare against the other drum classes) and `vs_band` (snare against non-drum stems only). A laid-back drummer usually shows in both. A drummer sitting behind a rushing band shows mainly in `vs_band`.

Listeners start to notice asynchrony between instruments at roughly 10 to 20 ms depending on context. Offsets below 5 ms are reported but MUST NOT be described to the listener as audible. Every microtiming value MUST carry the end-to-end error interval measured on the synthetic corpus (SPEC REQ-VAL-01, OI-4).

### 2.4 Drum transcription

Kick, snare, hi-hat (closed, half-open, open), ride, toms, crash, with time and velocity, from the drums stem. The model is chosen in M1 under ADR-0003 (SPEC OI-3). Until it reaches `beta`, dependent metrics stay `experimental`.

Fallback without a model: band onsets on the drums stem (kick 40 to 120 Hz, snare body 150 to 300 Hz with crack 1.5 to 5 kHz, hats and ride above 6 kHz, ride distinguished by longer decay). Fallback confidence MUST be capped at 0.5. Brushes produce weak, smeared onsets. When the snare band shows sustained broadband energy without clear onsets for more than 50% of snare-active frames, drum-class metrics abstain with `brushes`.

### 2.5 Pitch

- Monophonic f0 for bass and lead vocal: CREPE via `torchcrepe` (MIT) with 2.5 ms hop and weighted-argmax decoding (no Viterbi smoothing where transitions matter), voicing threshold 0.5. Bass octave errors: remove 12-semitone jumps shorter than 100 ms.
- Polyphonic notes: Basic Pitch (Apache-2.0). Its pitch-bend resolution is about a third of a semitone, so it MUST NOT be used for cent-level measurements.
- Key and chords: CQT chroma template matching. Coarse, never better than `ESTIMATED`.

### 2.6 Loudness and dynamics

ITU-R BS.1770 / EBU R 128 via `libebur128` (through `pyebur128`, MIT) or FFmpeg's `ebur128` filter: integrated loudness, momentary (400 ms) and short-term (3 s) loudness, LRA (EBU Tech 3342), true peak (4x oversampling), PLR = true peak minus integrated. BS.1770-4 and -5 give identical results for stereo, and the version used MUST be recorded. These can reach `MEASURED` once validated on EBU Tech 3341 and 3342 test signals.

### 2.7 Stem activity timeline

For each present stem, active spans (§2.1) merged across gaps shorter than one beat.

### 2.8 Structure

Segment boundaries from a self-similarity matrix on beat-synchronous chroma and MFCC with checkerboard novelty, snapped to downbeats. Labels by heuristic: the most repeated segment family with above-median loudness is `chorus`, the distinct segment immediately before a chorus is `pre_chorus`, and so on. `ESTIMATED` at best. A metric needing labels abstains with `no_structure` when labeler confidence is below 0.5.

### 2.9 Stereo analysis

Mid M = (L+R)/2, side S = (L−R)/2. Per-band (octave bands 63 Hz to 16 kHz) side-to-mid energy ratio and inter-channel coherence. Averages across bands are taken over **energies**, then converted to dB.

**Per-bin panning.** Frame-wise energy pan cannot see two hard-panned guitars playing at once, because their energies balance in every frame. Placement therefore uses a per-bin STFT panning index (Avendano and Jot 2004): for each time-frequency bin, the similarity of left and right magnitudes gives a pan position from -1 (hard left) to +1 (hard right). For each stem, the energy-weighted histogram of bin pans gives its position and spread. A stem whose histogram has modes beyond ±0.6 on both sides with balanced energy is a **split pair**.

### 2.10 Note envelopes and decay

For each onset, the envelope is the Hilbert magnitude low-passed at 20 Hz (or an RMS window of at least two periods of the stem's lowest f0), from onset to the next onset **of the same stem or drum class**, or 2 s. **Decay time** is from envelope peak to the first point where the envelope falls 20 dB below peak **and stays below for 20 ms**. If the next same-class onset comes first, the note is **censored**. Medians use the Kaplan-Meier estimator. When more than 50% of notes are censored the median is not identified, so the value reported is its lower bound with `median_identified: false`.

### 2.11 Audio event tagging

PANNs CNN14 (code MIT, weights CC BY 4.0, trained on AudioSet) on 1 s windows for: singing, speech, laughter, cough, breathing, clapping, count-in click. Used for voice gating (§2.1) and proxies. Never used to recognize words.

### 2.12 Reverberance

For isolated hits (no other snare or tom onset within 400 ms, hats allowed), band-limited to 150 Hz to 5 kHz on the relevant stem:

- **Late decay:** Schroeder backward integration of the tail after the first 50 ms, fitted from -5 to -25 dB, giving a decay rate in dB/s and an equivalent T60. This separates the room or reverb tail from the drum's own shell ring, which dominates the first 50 ms.
- **Early reflections:** density of discrete peaks in the envelope 5 to 80 ms after onset.

Artificial reverb and real rooms both produce tails. Headphones reports what the listener hears and does not claim to know which it is.

## 3. Render views

Every render follows SPEC REQ-REND-01 and 02.

| View | Content |
|---|---|
| `spectrogram` | Log-frequency spectrogram of the mix or a stem, with beat grid and section boundaries. |
| `microtiming` | Onset offsets per instrument against the swing-aware reference pulse, per bar, with the error band shaded and the grid type labeled. |
| `stem_activity` | One lane per present stem with active spans, section labels and taps. |
| `stereo_field` | Per-stem pan histograms left to right, split pairs marked, plus per-band side-to-mid ratio. |
| `loudness` | Momentary and short-term loudness, LRA band, sections, detected gaps and transitions. |
| `structure` | Self-similarity matrix with boundaries and labels. |
| `decay` | Envelopes of representative hits per stem with decay times, censored notes marked. |
| `pitch` | Bass and lead f0 contours with detected harmony voices. |

## 4. Ear forms, agreement and calibration

### 4.1 Ear forms and tiers

The listener has to be able to keep this up. Three tiers:

**Quick Ear** (default after every listen, about two minutes, mostly yes or no):

| # | Question | Feeds |
|---|---|---|
| Q1 | Taps during the listen: `n` head or body moves, `h` hook lands, `c` chills, `g` a gap that hit you, `m` a kept mistake | head_nod, hook_stickiness, chill_timestamp, space_before_drop, kept_mistakes |
| Q2 | Do you want to hear it again right now? yes / no | repeat_urge |
| Q3 | Could you hum the hook now? yes / no | hook_stickiness |
| Q4 | Did the chorus deliver? yes / no | payoff |
| Q5 | Are the drums dry, close and up front? yes / no | B1, room_sound |
| Q6 | Could you name every instrument by ear? yes / no | B3, clarity_under_load |
| Q7 | Is the vocal centred, dry and clearly sung? yes / no | B4 (including diction, which only the ear can judge) |
| Q8 | Which of these happened? (tick any) reveal, drop-out, second voice, lift, harmonic turn, new colour, surge | FEEL F1 to F7 |

**Rotating extras:** up to three more questions per listen, drawn from the remaining metrics in turn so each gets coverage over time. Each uses the scale in its entry.

**Full form:** every metric's ear question, available on request. Benchmark tracks use the smaller benchmark ear set defined in [docs/evaluation-plan.md](docs/evaluation-plan.md) §2.

Every question allows `not_sure` and `skip`. `not_sure` is excluded from agreement and counted separately.

### 4.2 Agreement statistics

| Value type | Primary statistic | Also reported |
|---|---|---|
| Ordinal category (3 levels) | Linearly weighted Cohen's kappa | Category prevalence, balanced accuracy, Gwet's AC1, exact agreement |
| Nominal category | Cohen's kappa | Prevalence, balanced accuracy, AC1 |
| Yes or no | Balanced accuracy | Kappa, AC1, prevalence |
| Timestamp | Hit rate within the metric's window, and false alarms per minute | Median signed lag |
| 5-point degree scale | Spearman rank correlation | Exact and within-one agreement |

**Timestamp windows.** Taps follow what triggered them. Windows are asymmetric, from 0.5 s before to 3.0 s after the analyzer event for chills, and 0.5 s before to 2.0 s after for gaps, hooks and kept mistakes *(initial)*.

**Intervals.** BCa bootstrap 95% intervals, 10,000 resamples, **clustered by artist**.

**Promotion rules** (SPEC §11.3):

- `beta`: point estimate ≥ 0.40 and lower bound ≥ 0.20, coverage (share of tracks not abstained) ≥ 70%.
- `stable`: lower bound ≥ 0.40 **and** point estimate ≥ 0.8 × the listener's own test-retest value for that metric (evaluation plan §2), on the sealed held-out set and again on a fresh confirmation set. Where no test-retest value exists (first-listen metrics), point estimate ≥ 0.60.
- Each category of a metric MUST have at least 10 held-out items for the rule to apply. Otherwise the metric stays at its current level and the shortfall is reported.

### 4.3 Calibration of thresholds

Category thresholds MAY be tuned on the calibration split only and MUST be frozen in a tagged commit before any held-out look ([docs/evaluation-plan.md](docs/evaluation-plan.md) §4).

## 5. Composites

These come from the listener's profile (the *Two Tests* document). Headphones evaluates them and does not redefine them. Each criterion carries `evidence_basis` and `basis_summary` (SPEC REQ-EVID-15).

### 5.1 BUILD (claimed by the profile to predict replays, not tested forward)

Each criterion is `pass`, `fail` or `unknown`.

| # | Profile wording | Evaluated as |
|---|---|---|
| B1 | Drums dry and close-miked, at the front of the mix, strict grid around 100 to 126 BPM | Passes when the ear answers Q5 yes, or when all of: `space.room_sound` = `dead_close`, drum prominence (drums stem short-term loudness minus mix, median over drum-active frames) ≥ -6 LU *(initial)*, and `attack.hand_played_feel` timing spread ≤ 12 ms measured against the swing-aware grid *(initial)*. Tempo is reported against the stated range and never used to fail (SPEC REQ-COMP-03). |
| B2 | Sound from attack, struck and plucked, short decay, nothing built on sustained tone | `attack.decay_length` category `short` for the instrumental bed (vocals excluded) AND sustained-tone share < 25% *(initial)*: the share of non-vocal energy in frames where pitched non-vocal stems are active with no same-stem onset in the previous 500 ms. |
| B3 | Parts separable, every instrument nameable by ear | Ear answer to Q6, or `space.clarity_under_load` = `clear`. |
| B4 | Vocal centred, dry, unprocessed, clearly enunciated | Diction is never computed (no-lyrics rule), so B4 can only `pass` with an ear yes on Q7. Without it, B4 is `unknown`, reported with its measured parts: vocal pan \|p\| ≤ 0.15, `vocal.proximity` = `close`, vocal late decay below the `dead_close` threshold, and no pitch-correction signature (on 2.5 ms f0, within-note standard deviation under 5 cents over 100 ms on more than 30% of held notes, or note transitions under 15 ms on more than 30% of transitions, *initial*). Any measured part failing makes B4 `fail` only if the ear has not said yes. |
| B5 | Hook inside 5 seconds, total length under 4:30 | Duration < 270 s (`MEASURED`) AND an `h` tap within 5 s on a first listen. With no such tap, the hook part is `unknown`, and Headphones offers the `structure.hook_stickiness.proxy` earliest-motif time as a timestamp to check. A proxy never passes or fails B5. |

### 5.2 FEEL (vocabulary for chills, untested as a predictor)

Count = distinct moves with at least one detection. The profile treats 3 or more as "chills territory" and notes there has been no control group. Headphones MUST NOT call it a prediction until evaluation Study C supports it. Ear answers to Q8 are stored alongside detections, never merged into them.

| # | Move | Detector (`ESTIMATED` unless stated) |
|---|---|---|
| F1 | Reveal: texture assembles, bare to full | Present stems active rise from ≤ 2 to ≥ 4 within 16 bars through at least two separate entries. |
| F2 | Drop-out: everything falls away, one element exposed | At least two active stems go inactive for ≥ 1 bar while one or two continue, and at least one returns. |
| F3 | Second voice: one voice becomes two | Voice-gated vocal voice count goes from 1 to ≥ 2 for ≥ 2 beats, or `vocal.doubling` reports a double starting. |
| F4 | Lift: melody climbs and holds at the top of the range | Lead f0 enters the top 10% of its track range after a rise of ≥ 5 semitones over ≤ 4 bars and stays ≥ 1 s. |
| F5 | Harmonic turn: an unexpected chord or key change | Chord outside the estimated key, or a key change, held ≥ 1 beat. `PROXY`, because chroma chords are coarse and "unexpected" is perceptual. |
| F6 | New colour: an instrument timbre not there before | A stem present for the first time after 20 s, or a new timbre cluster (MFCC k-means within any pitched stem, so a banjo entering the guitar stem counts) first appearing after 20 s. |
| F7 | Surge: density and volume arrive at once | Momentary loudness rises ≥ 4 LU within 2 beats *(initial)* while onset density rises ≥ 50%. |

### 5.3 Routing

The profile routes **artists**, not single tracks:

- **New anchor artist**: BUILD 4+ known passes and FEEL 3+ on tracks from the artist. Recommend the whole catalogue.
- **Rotation**: an artist clearing BUILD on three tracks from different records.
- **Resonance**: individual songs firing FEEL 3+. "Do not judge it by play count." (profile wording)
- **Skip**: neither.

For one track Headphones reports BUILD and FEEL only (SPEC REQ-COMP-05). Artist routing is computed when at least three tracks from at least two different records have been evaluated, and reports `undetermined` with the deciding criteria if unknowns could change the route.

## 6. Catalog

### Groove and pocket

#### `groove.pocket` · Pocket
- **Question:** Does the drummer sit on, ahead of, or behind the beat?
- **Ceiling:** `ESTIMATED`
- **Output:** `{pocket_source, vs_drummer: {median_ms, iqr_ms, ci95}, vs_band: {...}, kick_ms, hihat_ms, bass_ms, swing_ratio, grid, n_bars}`. Category: `ahead`, `on`, `behind`.
- **Method:** Offsets (§2.3) of the pocket source against the swing-aware reference pulse. `pocket_source` is the snare on backbeats in duple meter, or, when there is no backbeat (jazz, brushes, many acoustic records), the ride or hi-hat on quarter notes, or failing that the bass on beats. Category from `vs_band` median: < -8 ms `ahead`, > +8 ms `behind`, else `on` *(initial)*. If the interval straddles a threshold, confidence ≤ 0.5.
- **Abstain:** `no_pulse_source` (no snare, ride, hat or bass onsets on at least 16 beats), `low_separation`, `low_support` (over 30% of beats low-support).
- **Confidence:** min(sepq of sources, share of fully supported beats), reduced by the share of the interval overlapping a threshold.
- **Validation:** synthetic offsets -40 to +40 ms through the separator, straight and swung: median absolute error ≤ 3 ms for snare and ride, ≤ 6 ms for bass. Real: linear-weighted kappa.
- **Ear (extra):** "Does the drummer feel like they're pushing ahead, sitting right on it, or laying back?" `ahead`, `on`, `behind`.

#### `groove.felt_tempo` · Felt tempo
- **Question:** How fast does it feel versus the actual BPM?
- **Ceiling:** `ESTIMATED`
- **Output:** `{bpm, bpm_ci95, felt_bpm, relation, shuffle}`. Category (relation): `half`, `same`, `double`.
- **Method:** `bpm` is the median of 60 / inter-beat interval of the reference pulse, first normalized to the metrical level where the backbeat falls on beats 2 and 4. Relation from the snare backbeat period: snare every 2 beats `same`, every 4 beats `half`, every beat `double`. Without a backbeat, `same` with confidence ≤ 0.5. `shuffle` is true when the swing ratio is ≥ 1.6 on more than half the windows.
- **Abstain:** `no_pulse` (beat confidence below 0.4 on more than half the track).
- **Confidence:** beat confidence times backbeat clarity.
- **Validation:** `bpm` within 1% on synthetic. Real: kappa between analyzer relation and the ear relation.
- **Ear (extra):** Tap `t` along with the beat you feel, at least 8 times. The ear relation is tapped BPM / normalized `bpm`, binned to 0.5, 1 or 2.

#### `groove.ghost_notes` · Ghost notes
- **Question:** Quiet snare taps between the main hits?
- **Ceiling:** `ESTIMATED`
- **Output:** `{ghosts_per_bar, ghost_level_db_below_accent, n_bars, examples: [timestamps]}`. Category: `none`, `some`, `lots`.
- **Method:** The accent reference is the top-decile snare hit level (so it works with or without a backbeat). Ghosts are snare onsets 10 to 35 dB below that, not on the accented positions. Category: < 0.25 per bar `none`, 0.25 to 1.5 `some`, > 1.5 `lots` *(initial)*.
- **Abstain:** `no_drums`, `low_separation`, `no_transcription` (SPEC OI-3), `brushes`.
- **Confidence:** sepq[drums] times the transcription model's snare precision on synthetic.
- **Validation:** synthetic ghost velocities 10 to 40 (MIDI): detection F1 ≥ 0.75. Real: linear-weighted kappa.
- **Ear (extra):** "Can you hear quiet snare taps between the main hits?" `none`, `some`, `lots`.

#### `groove.hihat_articulation` · Hi-hat articulation
- **Question:** Open, closed, or chopped?
- **Ceiling:** `ESTIMATED`
- **Output:** `{share_closed, share_half_open, share_open, share_chopped, n_hits}`. Category: majority class, or `mixed` when none exceeds 50%.
- **Method:** For each hat hit, decay (§2.10) on the hat band, measured relative to the time until the next hat or kick onset (IOI). `closed`: decays below -20 dB within 80 ms. `half_open`: sustained sizzle that decays naturally before the next onset. `open`: still ringing when the next onset arrives at ≥ 60% of the IOI. `chopped` *(pending listener confirmation, SPEC OI-6)*: open-hat timbre stopped abruptly (≥ 20 dB within 20 ms) before 60% of the IOI. Relative timing keeps the same pattern from flipping class across tempos.
- **Abstain:** `no_drums`, `low_separation`, `no_hats` (fewer than 32 hat hits).
- **Confidence:** sepq[drums] times classifier margin.
- **Validation:** synthetic labeled hits: macro F1 ≥ 0.75. Real: kappa.
- **Ear (extra):** "How do the hi-hats sound?" `closed`, `half_open`, `open`, `chopped`, `mixed`.

#### `groove.kick_bass_lock` · Kick and bass lock
- **Question:** Do they hit as one?
- **Ceiling:** `ESTIMATED`
- **Output:** `{coincidence_rate, median_abs_offset_ms, n_kicks}`. Category: `locked`, `loose`, `independent`.
- **Method:** Only bass onsets that are pitched (CREPE voiced within 30 ms) count, so kick bleed in the bass stem cannot inflate the lock. Rate is the share of kicks with a pitched bass onset within ±30 ms. `locked`: rate ≥ 0.6 and median ≤ 15 ms. `independent`: rate < 0.3. Else `loose` *(initial)*.
- **Abstain:** `no_drums`, `no_bass`, `low_separation`.
- **Confidence:** min(sepq[drums], sepq[bass]).
- **Validation:** synthetic: rate error ≤ 0.05, offset error ≤ 6 ms. Real: linear-weighted kappa.
- **Ear (extra):** "Do the kick drum and bass hit together like one instrument?" `locked`, `loose`, `independent`.

#### `groove.fill_restraint` · Fill restraint
- **Question:** Fills only where needed?
- **Ceiling:** `ESTIMATED`
- **Output:** `{fills_per_minute, share_at_boundaries, fills: [timestamps]}`. Category: `restrained`, `moderate`, `busy`.
- **Method:** At beat resolution, a fill is a run of 1 to 8 beats where tom and snare onset density exceeds both 1.8 times the median of the previous 4 bars and an absolute minimum of 3 onsets per beat. Boundary fills end within one beat of a section boundary (§2.8). The first bar after a boundary is excluded. `restrained`: ≤ 1 per minute and ≥ 70% at boundaries. `busy`: > 3 per minute or < 40% at boundaries *(initial)*.
- **Abstain:** `no_drums`, `low_separation`. Without structure, `share_at_boundaries` is null and confidence is capped at 0.5.
- **Confidence:** sepq[drums] times structure confidence.
- **Validation:** synthetic fills: F1 ≥ 0.8. Real: linear-weighted kappa.
- **Ear (extra):** "Does the drummer only fill where it's needed?" `restrained`, `moderate`, `busy`.

#### `groove.head_nod` · Head-nod test
- **Question:** Does your body move within 10 seconds?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `{moved: yes|no, at_s}` from the `n` tap on a first listen.
- **Output (`groove.head_nod.proxy`):** `{time_to_stable_pulse_s, pulse_clarity}`. Stable pulse is the first time from which beat confidence stays ≥ 0.6 for 4 beats with kick-plus-bass onset strength above its track median.
- **Abstain (proxy):** `no_pulse`.
- **Confidence:** ear null. Proxy: beat confidence.
- **Validation:** proxy balanced accuracy of "stable pulse ≤ 10 s" against ear yes. Never above `PROXY`.
- **Ear (quick, Q1):** First listen only. "Tap N when your head or body starts moving." No tap within 10 s records `no`. Taps on repeat listens are kept and flagged.

### Attack and texture

#### `attack.snare_character` · Snare character
- **Question:** Crack, thud, or slap?
- **Ceiling:** `ESTIMATED`
- **Output:** `{attack_hf_ratio_db, body_ratio_db, decay_ms, centroid_hz, n_hits}`. Category: `crack`, `thud`, `slap`, `mixed`.
- **Method:** On accented snare hits. Crack is attack brightness: energy 1.5 to 5 kHz in the first 20 ms relative to 150 to 300 Hz. Decay is a separate axis. `crack`: attack HF ratio ≥ +3 dB. `thud`: attack HF ratio ≤ -6 dB with energy mostly below 300 Hz. `slap`: decay < 120 ms with energy concentrated 400 Hz to 1.5 kHz. Otherwise `mixed` *(initial)*. Crack and slap can both apply. Ties go to the larger margin.
- **Abstain:** `no_drums`, `low_separation`, `no_snare` (fewer than 16 accented hits).
- **Confidence:** sepq[drums] times margin.
- **Validation:** synthetic samples labeled by at least two people: kappa against the panel ≥ 0.6. Real: kappa.
- **Ear (extra):** "What does the snare sound like?" `crack` (sharp, bright), `thud` (low, dull), `slap` (short, dry, papery), `mixed`.

#### `attack.pick_sound` · Pick sound
- **Question:** Can you hear the pick hit the string?
- **Ceiling:** `ESTIMATED`
- **Output:** `{guitar_attack_ratio_db, bass_attack_ratio_db, n_notes}`. Category: `audible`, `subtle`, `none`.
- **Method:** Demucs tends to move pick transients into the drums stem, so this is measured on the **mix** at guitar-stem onsets that have no drum onset within ±30 ms. Ratio: energy 2 to 8 kHz in the first 15 ms after onset relative to the same band's level in the 100 ms before the onset (the sustain baseline), which keeps distortion's steady high end from hiding the pick. `audible` ≥ +6 dB, `none` ≤ +1 dB *(initial)*. The bass ratio is always reported.
- **Abstain:** `no_guitar`, `low_separation`, `too_few_clean_onsets` (fewer than 20).
- **Confidence:** sepq[guitar] times share of clean onsets.
- **Validation:** synthetic picked and fingered samples, distorted and clean: balanced accuracy ≥ 0.8. Real: linear-weighted kappa.
- **Ear (extra):** "Can you hear the pick click on the strings?" `audible`, `subtle`, `none`.

#### `attack.decay_length` · Decay length
- **Question:** How fast does each note die?
- **Ceiling:** `ESTIMATED`
- **Output:** `{per_stem: {stem: {median_decay_ms, median_identified, ci95, censored_share}}, bed_median_decay_ms}`. Category: `short`, `medium`, `long`.
- **Method:** §2.10 per stem. The category uses the energy-weighted median across present non-vocal pitched stems and drums (the instrumental bed): `short` < 250 ms, `long` > 800 ms *(initial)*. A bed median that is not identified is categorized `long` only if its lower bound exceeds 800 ms, otherwise `unknown`. Vocals are reported separately and never set the category.
- **Abstain:** per stem below 20 notes. Whole metric `too_dense` when every bed stem is unidentified and no lower bound exceeds 800 ms.
- **Confidence:** mean sepq of contributing stems times (1 − censored share).
- **Validation:** synthetic tones and plucks with known decay 50 ms to 3 s: median error ≤ 15%. Real: linear-weighted kappa.
- **Ear (extra):** "Do notes stop quickly or ring on?" `short`, `medium`, `long`.

#### `attack.air` · Air between notes
- **Question:** Silence you can hear inside the groove?
- **Ceiling:** `MEASURED`
- **Output:** `{air_share, median_dip_depth_db, dips_per_bar}`. Category: `dense`, `some_air`, `airy`.
- **Method:** Mix, 10 ms RMS frames. A dip is ≥ 30 ms at least 20 dB below the rolling 2 s 95th-percentile level inside an active section (not the intro, not the tail from `structure.ending`). `air_share` is the share of in-section time in dips. `dense` < 2%, `airy` > 10% *(initial)*.
- **Abstain:** `too_short` (under 30 s of active audio).
- **Confidence:** 1.0 for the measurement, lower near category thresholds.
- **Validation:** synthetic gaps: share error ≤ 0.5 points. Real: linear-weighted kappa.
- **Ear (extra):** "Can you hear little gaps of silence inside the groove?" `dense`, `some_air`, `airy`.

#### `attack.hand_played_feel` · Hand-played feel
- **Question:** Small human wobble, or a perfect machine grid?
- **Ceiling:** `ESTIMATED`
- **Output:** `{timing_spread_ms, tempo_drift_pct, grid_locked_share, lag1_autocorr, position_dependence, swing_ratio}`. Category: `machine`, `humanized_programmed`, `tight_human`, `loose_human`.
- **Method:** All offsets against the swing-aware grid (§2.3), so swing is never mistaken for sloppiness. `timing_spread_ms` = 1.4826 × median absolute deviation of drum offsets. `tempo_drift_pct` = standard deviation of 8-beat local tempo over mean tempo. `grid_locked_share` = share of onsets within ±max(5 ms, the 80th-percentile end-to-end error from §2.3) of one constant-tempo grid. `lag1_autocorr` of successive deviations and `position_dependence` (variance explained by position in the bar) separate human playing, which is autocorrelated and position-dependent, from random humanization, which is neither. `machine`: grid_locked_share ≥ 0.8 and drift < 0.2%. `humanized_programmed`: drift < 0.2%, spread ≥ 4 ms, lag-1 autocorrelation within ±0.1. `loose_human`: spread > 15 ms. Else `tight_human` *(initial)*.
- **Abstain:** `no_rhythm_source`, `low_separation`.
- **Confidence:** sepq of stems used, reduced when spread is within the measurement error.
- **Validation:** synthetic quantized, randomly humanized, and human-style (autocorrelated, drifting) timing, straight and swung: category accuracy ≥ 0.8. Real: kappa.
- **Ear (extra):** "Does it feel played by hands or locked to a machine?" `machine`, `tight_human`, `loose_human`, `not_sure`.

#### `attack.guitar_tone` · Guitar tone
- **Question:** Bright and thin, or warm and round?
- **Ceiling:** `ESTIMATED`
- **Output:** `{centroid_hz, body_ratio_db, tilt_db_per_octave, timbre_clusters}`. Category: `bright_thin`, `balanced`, `warm_round`.
- **Method:** On active guitar-stem frames: centroid, 100 to 400 Hz versus 2 to 6 kHz energy (body ratio), and spectral tilt. Frames are clustered by MFCC first, and the largest cluster sets the category, so a banjo sharing the stem does not average into the guitar. `bright_thin`: centroid > 2.5 kHz and body ratio < -6 dB. `warm_round`: centroid < 1.2 kHz and body ratio > 0 dB *(initial)*.
- **Abstain:** `no_guitar`, `low_separation`.
- **Confidence:** sepq[guitar] times margin times the largest cluster's share.
- **Validation:** synthetic amp and EQ settings: accuracy ≥ 0.8. Real: linear-weighted kappa.
- **Ear (extra):** "How does the guitar sound?" `bright_thin`, `balanced`, `warm_round`.

### Space and mix

#### `space.room_sound` · Room sound
- **Question:** Dead and close, or live and roomy?
- **Ceiling:** `ESTIMATED`
- **Output:** `{drum_late_t60_s, drum_early_density, vocal_late_t60_s, n_hits}`. Category: `dead_close`, `medium`, `live_roomy`.
- **Method:** Reverberance (§2.12) on isolated snare and tom hits and on vocal phrase ends. `dead_close`: drum late T60 < 0.3 s and low early-reflection density. `live_roomy`: late T60 > 0.8 s or high early density *(initial)*. Real rooms and added reverb are not distinguished. The category describes what is heard.
- **Abstain:** `no_drums` and `no_singing`, `no_isolated_hits` (fewer than 8).
- **Confidence:** sepq[drums] times share of isolated hits.
- **Validation:** synthetic convolution with impulse responses of known T60, through the separator: T60 error ≤ 25%. Real: linear-weighted kappa.
- **Ear (quick via Q5, extra for the full scale):** "Does it sound dry and close, or roomy with space around it?" `dead_close`, `medium`, `live_roomy`.

#### `space.stereo_placement` · Stereo placement
- **Question:** Where does each instrument sit left to right?
- **Ceiling:** `ESTIMATED`
- **Output:** `{per_stem: {stem: {pan, spread, split_pair}}, per_drum_class: {class: pan}}`. Per-stem category: `hard_left`, `left`, `centre`, `right`, `hard_right`, `both_sides`.
- **Method:** Per-bin panning (§2.9). `both_sides` when `split_pair` is true (the classic double-tracked guitars). Drum kit spread from per-class pans of transcribed hits.
- **Abstain:** `mono_source`. Per stem, `low_separation`.
- **Confidence:** per stem sepq.
- **Validation:** synthetic panned stems including hard-panned doubles: pan error ≤ 0.05, split-pair F1 ≥ 0.9. Real: kappa per named instrument.
- **Ear (extra):** "Where is the [instrument]?" hard left, left, centre, right, hard right, both sides.

#### `space.width` · Width
- **Question:** Narrow and focused, or spread wide?
- **Ceiling:** `MEASURED`
- **Output:** `{side_to_mid_db, coherence, per_band: [...]}`. Category: `narrow`, `medium`, `wide`.
- **Method:** §2.9 on the mix, energy-averaged over bands from 125 Hz up. `narrow` < -15 dB, `wide` > -7 dB *(initial)*.
- **Abstain:** `mono_source`.
- **Confidence:** 1.0 for the measurement.
- **Validation:** synthetic M/S ratios: error ≤ 0.5 dB. Real: linear-weighted kappa.
- **Ear (extra):** "Does the mix feel narrow and focused or spread wide?" `narrow`, `medium`, `wide`.

#### `space.clarity_under_load` · Clarity under load
- **Question:** When it's loud, can you still pick out every part?
- **Ceiling:** `ESTIMATED`
- **Output:** `{audible_share_loud, stems_active_loud, masked: [stem]}`. Category: `clear`, `partly_masked`, `smeared`.
- **Method:** In the loudest 25% of short-term loudness frames, for each active stem, per-band excitation on 32 ERB bands. A stem is audible in a frame if in at least 3 bands its excitation exceeds the others' summed excitation minus 6 dB *(initial)*. `clear` ≥ 0.85, `smeared` < 0.6 *(initial)*.
- **Abstain:** `too_few_stems` (fewer than 3 present), `low_separation`.
- **Confidence:** mean sepq of active stems.
- **Validation:** synthetic mixes with controlled masking: accuracy ≥ 0.8. Real: linear-weighted kappa, and balanced accuracy against Q6.
- **Ear (quick via Q6, extra for the full scale):** "In the loudest part, can you still pick out every instrument?" `clear`, `partly_masked`, `smeared`.

#### `space.compression_pumping` · Compression pumping
- **Question:** Does the mix breathe or squeeze?
- **Ceiling:** `ESTIMATED`
- **Output:** `{plr_db, lra_lu, kick_dip_db, snare_dip_db, control_dip_db, signature}`. Category: `breathes`, `moderate`, `squeezes`. `signature`: `none`, `sidechain`, `bus_pump`, `both`.
- **Method:** Measured on sustained elements only (cymbal wash, pads, held guitar, reverb tails: frames with no same-stem onset in the previous 150 ms). Dip = level drop 50 to 250 ms after kick onsets (`kick_dip_db`) and after snare onsets (`snare_dip_db`), each minus the same statistic at beat positions with no drum hit (`control_dip_db`), which removes separator artifacts and natural decay. `sidechain`: kick dip ≥ 2 dB with recovery shape repeating at the beat period. `bus_pump`: dips ≥ 1.5 dB after both kick and snare. Category: `squeezes` when signature is not `none` or PLR < 8 dB. `breathes` when signature is `none` and PLR > 12 dB *(initial)*. PLR and LRA are reported as their own "loud versus dynamic" fields.
- **Abstain:** dips null when no drums. Category then from PLR and LRA alone, confidence capped at 0.6.
- **Confidence:** sepq[drums] for dips, 1.0 for PLR and LRA.
- **Validation:** synthetic compressor, bus and sidechain settings, plus uncompressed controls: dip error ≤ 0.5 dB, signature F1 ≥ 0.8. Real: linear-weighted kappa.
- **Ear (extra):** "Does the mix breathe, or does it feel squeezed and pumping?" `breathes`, `moderate`, `squeezes`.

### Vocal

All vocal metrics measure sound only. None of them transcribe, store or use words (SPEC N2, ADR-0004). All use voice-gated frames (§2.1).

#### `vocal.breath` · Breath
- **Question:** Can you hear the singer inhale?
- **Ceiling:** `ESTIMATED`
- **Output:** `{breaths_per_vocal_minute, median_level_db_below_vocal, examples: [timestamps]}`. Category: `audible`, `faint`, `removed`.
- **Method:** Vocals-stem segments of 100 to 700 ms with voicing probability < 0.2, broadband noise centred 1 to 6 kHz, ending within 600 ms before a voiced phrase onset, confirmed by the tagger's breathing class. Segments overlapping a hat or cymbal onset in the drums stem are rejected. `audible`: ≥ 4 per vocal minute at ≥ -30 dB relative to vocal. `removed`: < 0.5 per vocal minute *(initial)*.
- **Abstain:** `no_singing`, `low_separation`.
- **Confidence:** sepq[vocals] times detector precision on synthetic.
- **Validation:** synthetic vocals with breaths inserted and removed: F1 ≥ 0.75. Real: linear-weighted kappa.
- **Ear (extra):** "Can you hear the singer breathe in?" `audible`, `faint`, `removed`.

#### `vocal.doubling` · Doubling
- **Question:** One take or stacked takes?
- **Ceiling:** `ESTIMATED`
- **Output:** `{double_share, stereo_double_share, adt_or_chorus_share, onset_offset_variability_ms}`. Category: `single`, `doubled`, `stacked`, `adt_or_chorus`.
- **Method:** Inter-channel coherence measured on the first 50 ms of each phrase (direct sound, before reverb tails). A **true double** shows independent f0 micro-variation between components and onset offsets that change phrase to phrase (variability ≥ 5 ms). **ADT** shows an identical f0 contour with a constant or slowly swept delay. A **chorus effect** shows periodic pitch modulation at 0.3 to 5 Hz. `single` when doubled frames < 20%. `stacked` when true doubles plus harmonies give ≥ 3 voices *(initial)*.
- **Abstain:** `no_singing`, `low_separation`.
- **Confidence:** sepq[vocals] times agreement between coherence and f0 evidence.
- **Validation:** real-singer multitracks (single, double, quad) and ADT and chorus processing of single takes: macro F1 ≥ 0.7. Real: kappa. Starts `experimental`.
- **Ear (extra):** "Is it one voice, a doubled voice, a stack, or an effect?" `single`, `doubled`, `stacked`, `adt_or_chorus`.

#### `vocal.harmony_stacking` · Harmony stacking
- **Question:** How many voices, how tight?
- **Ceiling:** `ESTIMATED`
- **Output:** `{max_voices, median_voices_when_harmonizing, harmony_share, onset_spread_ms}`. Category: `none`, `one_harmony`, `stack`. Tightness category: `tight`, `loose`.
- **Method:** Basic Pitch on voice-gated vocals. A harmony frame has ≥ 2 simultaneous notes at least 2 semitones apart held ≥ 150 ms (vibrato crossing a semitone is not a second voice). Tightness from the median onset spread of voices starting together: `tight` ≤ 30 ms *(initial)*. No cent-level tuning claim is made (§2.5).
- **Abstain:** `no_singing`, `low_separation`.
- **Confidence:** sepq[vocals] times note confidence.
- **Validation:** real-singer ensemble recordings (for example Dagstuhl ChoirSet, license permitting) and synthetic arrangements: voice-count accuracy ≥ 0.8. Real: linear-weighted kappa.
- **Ear (extra):** "How many voices at once?" `none` (one voice), `one_harmony`, `stack`. When harmony is present, REQUIRED follow-up: "How tight are they?" `tight`, `loose`.

#### `vocal.proximity` · Proximity
- **Question:** Close to the mic, or set back?
- **Ceiling:** `ESTIMATED`
- **Output:** `{vocal_late_t60_s, proximity_bass_ratio_db, hf_detail_db, mouth_noise_rate}`. Category: `close`, `medium`, `set_back`.
- **Method:** Vocal reverberance (§2.12 on phrase ends), proximity-effect bass (100 to 300 Hz versus 1 to 3 kHz on voiced frames), 6 to 12 kHz detail, and the rate of small mouth-noise transients. Mix level is not used, so an intimate vocal mixed low still reads close. `close`: late T60 < 0.3 s and proximity bass ratio ≥ -6 dB. `set_back`: late T60 > 0.8 s or proximity bass ratio < -15 dB *(initial)*.
- **Abstain:** `no_singing`, `low_separation`.
- **Confidence:** sepq[vocals].
- **Validation:** synthetic close and distant mic simulations: accuracy ≥ 0.8. Real: linear-weighted kappa.
- **Ear (quick via Q7, extra for the full scale):** "Does the singer sound right up on the mic or further back?" `close`, `medium`, `set_back`.

#### `vocal.phrasing` · Phrasing
- **Question:** On the beat, or floating across it?
- **Ceiling:** `ESTIMATED`
- **Output:** `{on_grid_share, chance_share, mean_signed_phrase_offset_ms, median_abs_offset_ms, n_phrases}`. Category: `on_grid`, `mixed`, `floating`.
- **Method:** Phrase onsets (voiced after ≥ 250 ms unvoiced) against the swing-aware 8th grid. `on_grid_share` is the share within ±20 ms. `chance_share` is what uniformly random onsets would give at this tempo, reported alongside. "Floating" is a sustained lag or anticipation against strong beats, so `mean_signed_phrase_offset_ms` is reported too. `on_grid`: share ≥ chance + 0.35. `floating`: share < chance + 0.10 or |mean signed offset| ≥ 60 ms *(initial)*. Consonants make onsets early and smeared, so the end-to-end error MUST be shown.
- **Abstain:** `no_singing`, `no_pulse`, `low_separation`.
- **Confidence:** sepq[vocals] times beat confidence.
- **Validation:** synthetic vocals at known offsets: share error ≤ 0.08. Real: linear-weighted kappa.
- **Ear (extra):** "Does the singer land on the beat or float across it?" `on_grid`, `mixed`, `floating`.

### Structure and hook

#### `structure.first_sound` · First sound
- **Question:** What hits you at second one?
- **Ceiling:** `ESTIMATED`
- **Output:** `{leading_silence_s, stems_active_first_1s, first_1s_loudness_rel_lu, events}`. Category: `full_band`, `small_group`, `single_instrument`, `voice`, `drums_only`, `texture_or_effect`.
- **Method:** First frame above max(noise floor + 6 dB, integrated loudness − 45 LU) marks the start. Over the next 1 s: present stems active, momentary loudness relative to integrated, event tags. ≥ 3 stems `full_band`, exactly 2 `small_group`, voice-gated vocals only `voice`, drums only `drums_only`, one pitched stem `single_instrument`, else `texture_or_effect`.
- **Abstain:** none.
- **Confidence:** mean sepq of stems involved.
- **Validation:** synthetic intros: accuracy ≥ 0.9. Real: kappa.
- **Ear (extra):** "What's the first thing you hear?" same categories.

#### `structure.hook_stickiness` · Hook stickiness
- **Question:** Can you hum it after one listen?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `{hummable_after_one: yes|no, hook_at_s}` from Q3 and the `h` tap on a first listen.
- **Output (`structure.hook_stickiness.proxy`):** `{motif_repeats, first_occurrence_s, source, motif_span_s}`. The most repeated motif of 1 to 4 bars found by self-similarity over **every** pitched stem's pitch-class sequence (transposed to a common root) and over drum rhythm patterns. The earliest strong candidate wins, so an intro riff counts.
- **Abstain (proxy):** `no_motif`.
- **Confidence:** ear null. Proxy: self-similarity peak strength.
- **Validation:** proxy correlation with ear yes and with `h` tap times. Never above `PROXY`.
- **Ear (quick, Q1 and Q3):** First listen: tap `h` when the hook lands. After: "Could you hum the hook now?" `yes`, `no`, `not_sure`. An OPTIONAL second check 24 hours later is stored separately.

#### `structure.bassline_hummability` · Bassline hummability
- **Question:** Is the bass its own melody?
- **Ceiling:** `ESTIMATED` for melodic identity. The felt answer is ear.
- **Output:** `{motif_distinctness, motif_repeats, pitch_range_semitones, distinct_pitch_classes, interval_entropy_bits, bass_without_kick_share}`. Category: `root_anchor`, `moving`, `melodic`.
- **Method:** Bass f0 (§2.5, octave-cleaned, range from 5th to 95th percentile) segmented into notes. The hook-motif search runs on the bass alone. `motif_distinctness` is how strongly one bass motif repeats and differs from a root pattern. `bass_without_kick_share` is the share of bass onsets with no kick within 30 ms. `melodic`: a distinct motif repeats ≥ 3 times with ≥ 3 pitch classes and is not a single repeated note. `root_anchor`: repeated-note share ≥ 0.7 and no distinct motif *(initial)*. Range is reported but does not decide the category, because famous hook basslines can be narrow.
- **Abstain:** `no_bass`, `low_separation`, `unpitched_bass`.
- **Confidence:** sepq[bass] times voicing confidence.
- **Validation:** synthetic basslines: pitch-class accuracy ≥ 0.9. Real: linear-weighted kappa.
- **Ear (extra):** "Could you hum the bassline on its own, like a tune?" `root_anchor` (mostly one note), `moving`, `melodic`.

#### `structure.pre_chorus_tension` · Pre-chorus tension
- **Question:** Does it pull you toward the chorus?
- **Ceiling:** `PROXY`
- **Output (`structure.pre_chorus_tension.proxy`):** `{per_transition: [{chorus_at_s, rising_indicators, score}]}`.
- **Method:** Over the 4 to 8 bars before each detected chorus, slopes of momentary loudness, onset density, centroid, lead pitch height and active stem count. Score = indicators rising above threshold (0 to 5).
- **Abstain:** `no_structure`, `no_chorus`.
- **Confidence:** structure confidence.
- **Validation:** Spearman with the ear rating. Never above `PROXY`.
- **Ear (extra):** "Does the section before the chorus pull you toward it?" 1 no pull, 2, 3 some, 4, 5 strong pull.

#### `structure.payoff` · Payoff
- **Question:** Does the chorus deliver what the build promised?
- **Ceiling:** `PROXY` for the contrast. The felt answer is ear.
- **Output (`structure.payoff.proxy`):** `{per_chorus: [{at_s, loudness_delta_lu, width_delta_db, stem_count_delta, density_delta_pct}]}`.
- **Method:** Chorus versus the preceding segment, medians of each.
- **Abstain:** `no_structure`, `no_chorus`.
- **Confidence:** ear null. Proxy: structure confidence.
- **Validation:** balanced accuracy against Q4. Never above `PROXY`.
- **Ear (quick, Q4):** "Did the chorus deliver?" `yes`, `no`, `not_sure`.

#### `structure.ending` · Ending
- **Question:** Hard stop, cold end, or fade?
- **Ceiling:** `ESTIMATED` (the `other` class depends on the event tagger).
- **Output:** `{fade_duration_s, drop_db_in_20ms, drop_db_in_300ms, tail_ring_s, trailing_silence_s}`. Category: `fade`, `ring_out`, `dead_stop`, `cut`, `other`.
- **Method:** The end gate is max(noise floor + 6 dB, integrated loudness − 45 LU), so tape hiss does not hide the ending. `fade`: short-term loudness falls ≥ 15 LU over ≥ 3 s, monotonically (Spearman ρ ≤ -0.9 on 1 s medians), while onsets continue. `ring_out`: a final hit or chord, no new onsets, natural decay ≥ 0.4 s. `dead_stop`: the band stops together, level falls ≥ 30 dB within 300 ms, a reverb tail is allowed. `cut`: level falls ≥ 30 dB within 20 ms including any tail, as from an edit. `other`: trailing noise, hidden track, spoken outro *(initial)*. Mapping to the listener's words *(pending listener confirmation, SPEC OI-6)*: "fade" = `fade`, "cold end" = `ring_out` or `dead_stop`, "hard stop" = `cut` or `dead_stop`.
- **Abstain:** none.
- **Confidence:** 1.0 for the measurements, lower near thresholds.
- **Validation:** synthetic endings of every class: accuracy ≥ 0.95. Real: kappa.
- **Ear (extra):** "How did it end?" `fade`, `ring_out` (last hit rings on), `dead_stop` (band stops together), `cut` (sounds edited off), `other`.

#### `structure.repeat_urge` · Repeat urge
- **Question:** Do you want it again the moment it ends?
- **Ceiling:** `EAR`
- **Output (ear):** `{wanted_again: yes|no}` from Q2, and `replayed_within_60s` when the listener restarts it on the station.
- **Output (behavioral, off by default, SPEC REQ-SPOT-04):** `{plays, replays_within_1h, skip_rate, completion_rate}` from imported history.
- **Abstain:** not applicable. There is no audio proxy.
- **Confidence:** null.
- **Validation:** none. Behavioral values are context, not a measurement of the urge.
- **Ear (quick, Q2):** "Do you want to hear it again right now?" `yes`, `no`, `not_sure`.

### Feel, deeper

#### `feel.call_and_response` · Call and response
- **Question:** Does one part answer another?
- **Ceiling:** `ESTIMATED`
- **Output:** `{exchanges: [{caller, responder, count, at_s}]}`. Category: `present`, `absent`.
- **Method:** At phrase level, which source is in the **foreground**: the stem (or, within the vocals stem, the lead versus backing voices from the voice count) with the highest loudness-weighted salience in each beat. An exchange is foreground passing A to B to A within a section, each turn 1 to 8 bars, at least 3 turns, turn lengths within a factor of 2. Background parts may keep playing, which catches guitar fills over rhythm playing and jazz drummers trading fours.
- **Abstain:** `too_few_stems`.
- **Confidence:** mean sepq of the pair.
- **Validation:** synthetic arrangements with exchanges over continuous backing: F1 ≥ 0.8. Real: kappa.
- **Ear (extra):** "Does one part answer another?" `present`, `absent`.

#### `feel.dynamic_breathing` · Dynamic breathing
- **Question:** Do soft and loud sections trade off?
- **Ceiling:** `MEASURED`
- **Output:** `{lra_lu, plateaus: [{start_s, end_s, level_lu}], transitions: [{at_s, delta_lu}]}`. Category: `flat`, `some`, `breathing`.
- **Method:** Plateaus are spans of at least 8 s where the 3 s short-term loudness stays within ±2 LU of its median (2 LU hysteresis). A transition is a change of ≥ 4 LU between adjacent plateaus *(initial)*. The first 10 s and any fade region found by `structure.ending` are excluded. `flat`: no transitions. `breathing`: ≥ 2 transitions in each direction *(initial)*.
- **Abstain:** `too_short`.
- **Confidence:** 1.0 for the measurements.
- **Validation:** synthetic level automation: transition F1 ≥ 0.9, LRA within 0.5 LU of EBU Tech 3342. Real: linear-weighted kappa.
- **Ear (extra):** "Does it trade between soft and loud parts?" `flat`, `some`, `breathing`.

#### `feel.kept_mistakes` · Kept mistakes
- **Question:** A flub or laugh left in the take?
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `m` taps with optional one-line notes.
- **Output (`feel.kept_mistakes.proxy`):** `{candidates: [{at_s, kind, score}]}`. Kinds: `laughter`, `speech`, `count_in`, `timing_outlier` (one onset more than 3 IQR off the reference pulse while neighbours are tight), `string_noise` (broadband transient on the guitar stem with no pitched onset).
- **Abstain (proxy):** `too_short`.
- **Confidence:** ear null. Proxy: tagger or outlier score.
- **Validation:** precision of the top 3 candidates against `m` taps within the timestamp window.
- **Ear (quick, Q1):** "Tap M on anything that sounds like a mistake or a moment left in."

#### `feel.space_before_drop` · Space before the drop
- **Question:** The half-second of nothing before a big moment?
- **Ceiling:** `MEASURED`
- **Output:** `{gaps: [{start_s, length_ms, depth_db, rise_lu, kind}]}`. `kind`: `gap` (≥ 400 ms) or `near_gap` (150 to 400 ms). Category: `present` when at least one `gap`, else `absent`.
- **Method:** Mix, 20 ms frames. A candidate is ≥ 150 ms at least 10 dB below the median of the previous 2 s (depth reported, so near-silences with one element still sounding are kept). It counts only if within 100 ms an onset leads into a passage that is ≥ 2 LU louder (momentary, next 3 s versus previous 3 s) or starts a new section or a rise in active stem count, and no other candidate occurred in the previous 4 bars (so stop-time riffs do not fire every bar). `gap` needs ≥ 400 ms, matching "half-second". Shorter qualifying candidates are listed as `near_gap`.
- **Abstain:** `too_short`.
- **Confidence:** 1.0 for detection. Whether it was a big moment is the listener's call.
- **Validation:** synthetic gaps 50 to 800 ms in stop-time and drop contexts: F1 ≥ 0.95, length error ≤ 20 ms. Real: hit rate against `g` taps.
- **Ear (quick, Q1):** Tap `g` on any gap that hit you.

#### `feel.chill_timestamp` · Chill timestamp
- **Question:** The exact second it happens.
- **Ceiling:** `EAR`. Proxy offered.
- **Output (ear):** `c` taps with time, latency correction, `first_listen` and listen index.
- **Output (`feel.chill_timestamp.proxy`):** `{candidates: [{at_s, reasons, score}]}` from FEEL detections (§5.2), momentary loudness surges, new stem entries and `feel.space_before_drop` gaps, ranked by the number of coinciding reasons.
- **Abstain (proxy):** `too_short`.
- **Confidence:** ear null. Proxy: normalized rank score.
- **Validation:** Study C in [docs/evaluation-plan.md](docs/evaluation-plan.md): top-k hit rate within the chill window (0.5 s before to 3.0 s after) against `c` taps, compared with a structure-aware null.
- **Ear (quick, Q1):** "Tap C the moment you get chills." Taps on repeat listens are kept and flagged.

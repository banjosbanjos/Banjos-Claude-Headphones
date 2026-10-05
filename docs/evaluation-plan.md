# Evaluation Plan

| Field | Value |
|---|---|
| Version | 0.2.0-draft |
| Status | Normative for SPEC §11 and §12. Pre-registration document. |
| Date | 2026-10-05 |

This plan is committed before any data is collected. Changes after collection starts MUST be recorded in §12 with the date and reason, and the original text stays visible in version control.

**Conflict of interest.** The listener defines the ground truth, chose the metrics and approves this plan. Every report MUST say so. When any outside person is available, they SHOULD read and sign off this plan before data collection, and their name goes in §12.

## 1. Questions

| Study | Question |
|---|---|
| A | Does each analyzer agree with the listener's ear well enough to earn its evidence class? |
| B | Does Claude Code with Headphones agree with the listener's ear more often than Claude Code without it? |
| C | Do FEEL detectors and chill candidates find the moments the listener marks better than a fair null? Do they fire as often on music the listener dislikes? |
| D | Does BUILD, scored from audio, predict what the listener replays? |

## 2. Ground truth and the listener's time

**Blind capture.** For every track in every study (calibration, held-out and confirmation splits alike), the listener completes the ear questions before any analyzer output or agent answer about **any** study track is shown. The station enforces this with blind mode (SPEC REQ-MCP-06). Seeing analyzer outputs during calibration would teach the listener what the analyzers count as `crack` or `restrained` and inflate later agreement, so calibration-split outputs stay hidden until all ear capture is done.

**Benchmark ear set.** Asking all 35 questions per track would take 20 minutes or more and 4,000+ answers. The benchmark uses:

- the Quick Ear form (METRICS.md §4.1, about two minutes), and
- eight measurable metrics on their full scales: `groove.pocket`, `groove.kick_bass_lock`, `attack.hand_played_feel`, `attack.decay_length`, `space.room_sound`, `space.width`, `space.stereo_placement` (guitar only), `structure.ending`.

That is about 10 minutes per track. Other metrics are validated over time through rotating extras.

**First listens.** Head-nod, hook and chill need first listens. A first listen (SPEC §4) requires no plays in imported history, no prior preview, and the listener's confirmation at the station. Because a track must be owned before it can be analyzed, first-listen tracks come from an **acquisition protocol**: buy whole albums by artists the listener has not heard, and play the deep cuts on the station before anything else. The first-listen count is reported for every study.

**Listener consistency (test-retest).** At least 40 items per benchmark metric are re-scored at least two weeks after the first answer and before any unblinding. Test-retest agreement uses the METRICS.md §4.2 statistics and sets the ceiling used in the `stable` rule. First-listen metrics cannot be retested and are reported with "no ceiling".

`not_sure` answers are excluded from agreement and their rate is reported.

## 3. Tracks and cost

- Only assets in the listener's library (SPEC REQ-SRC-01). First check what is already owned.
- At least 120 tracks for Studies A and B, covering the anchor artists, picked and acoustic country, small-group jazz, and records outside the profile, plus at least 40 first-listen tracks from the acquisition protocol.
- **Cost estimate.** About $1.29 per track on the iTunes Store or Amazon, or about $8 to $12 per album. 120 tracks bought as singles is roughly $155. Buying the first-listen tracks as albums adds roughly $80 to $150. Anything already owned or on CD costs nothing.
- **Split by artist**, never by track: calibration 40%, held-out 40%, confirmation 20%. The confirmation split stays untouched until a metric is a `stable` candidate.
- **Text availability strata.** Each track is tagged `well_documented` (a Wikipedia article or at least three professional reviews) or `sparse`.
- **Category balance.** Before the held-out split is sealed, the listener's calibration-split ear answers are used to estimate category prevalence. Where a category of a benchmark metric would have fewer than 10 held-out items, more tracks of that kind are added to the pool (chosen from the listener's library by ear description, not by analyzer output). A metric that still falls short is reported as underpowered, not promoted.

## 4. Sealing and looks

- The held-out split is **sealed**: its ear answers and analyzer outputs are not compared until a look is declared.
- Each analyzer major version gets **one look** at the held-out split. Every look is logged in §12 with date, analyzer versions and metrics.
- Calibration reports (SPEC REQ-VAL-07) exclude sealed assets.
- `stable` needs the same rule met on the confirmation split, which is looked at once per metric.
- Thresholds are tuned on the calibration split only and frozen in a tagged commit before any look.

## 5. Study A: analyzer validation

1. Synthetic suite first (SPEC §11.2).
2. Power analysis: before collection, a script in `tools/` simulates each benchmark metric's statistic under expected prevalence and the planned n, and the expected chance of meeting the `beta` and `stable` rules is recorded in §12. Metrics with less than 50% chance of meeting `beta` at planned n are flagged in advance.
3. Agreement on the held-out split using METRICS.md §4.2, BCa intervals clustered by artist.
4. **Coverage is reported** alongside agreement, so an analyzer cannot raise its score by abstaining on hard tracks. `beta` and `stable` need coverage ≥ 70%.

## 6. Study B: harness lift

### 6.1 Arms

| Arm | Access |
|---|---|
| Baseline | Claude Code with web search and the Spotify connector. No Headphones. |
| Harness | The same, plus the Headphones plugin (MCP server and skill), in blind mode for ear data. |

Same pinned model version and prompt apart from the skill. Each arm runs three times per track. Per-item agreement is averaged over the three runs before any comparison.

### 6.2 Questions

For each held-out track and each item in the benchmark ear set, each arm gives the category, yes or no, or timestamps, and a confidence from 0 to 1. Either arm may answer "not sure". The prompt names the track by artist and title only.

### 6.3 Primary hypothesis (pre-registered)

**H1.** Over benchmark metrics whose ceiling is `MEASURED` or `ESTIMATED`, the harness arm's balanced accuracy against the ear exceeds the baseline's by more than 10 percentage points.

- Each metric is weighted equally. Within a metric, balanced accuracy averages per-category recall, so always guessing the most common answer scores at chance.
- "Not sure" counts as wrong for H1 so abstaining cannot inflate the score. Coverage is reported separately.
- Test: one-sided 95% lower bound of the difference, cluster bootstrap by artist (10,000 resamples), must exceed 10 points.
- Timestamp items are scored as hits within the METRICS.md §4.2 windows.

### 6.4 Secondary outcomes

- Per-metric differences with Holm correction across metrics.
- Coverage and selective accuracy per arm.
- Calibration: Brier score, plus a reliability diagram with equal-mass bins (5 bins) and artist-clustered intervals. Expected calibration error is reported with its bins stated.
- Rule compliance (SPEC REQ-EVID-12) on a 20% sample, scored with the rubric in §9 by two raters. Tool traces and arm labels are removed before rating. Inter-rater kappa ≥ 0.6 is required before results are reported. The baseline cannot cite Headphones evidence by design, so compliance compares only claims both arms could make (naming `TEXTUAL` and saying when to check by ear).
- Invented timestamps (SPEC REQ-EVID-14). Target for the harness arm: zero.
- Perceptual (`EAR` and `PROXY` ceiling) items reported separately. No lift is predicted. The point is to see whether either arm pretends to know.
- All outcomes split by `well_documented` and `sparse`.

### 6.5 Threats to validity

- **One listener.** Results describe this listener only.
- **The listener has read about some records.** Text the listener has read may shape their ear answers in the same direction as the baseline's text. Reported by stratum.
- **Leakage.** Thresholds use the calibration split only. Blind mode hides ear data. Agent transcripts are checked for any access to ear data.
- **Master mismatch.** The baseline may draw on text about a different master. Accepted, because the listener hears the owned asset.
- **Model drift.** The model version is pinned and recorded. A new version is a new study.

## 7. Study C: FEEL and chills

1. **Hit rate.** For each `c` tap on a first listen, is a chill candidate in the top k (k = 3 and 5) within the chill window (0.5 s before to 3.0 s after the candidate)?
2. **Fair null.** Chills cluster at section changes and loudness changes, so a uniform random null is too easy. The null places the same number of candidates at randomly chosen section boundaries and momentary-loudness change points of the same track, 10,000 times.
3. **Control group (ear only, can start in M1).** The listener picks 20 records they dislike and 20 they love, matched as far as possible on era, tempo range and instrumentation, and ticks FEEL moves by ear (Quick Ear Q8) using external playback mode (SPEC §7.4.4). No purchase is needed. The listener cannot be blind to which group a record is in, so this part measures the listener's own vocabulary, not the detectors.
4. **Detectors on the control group.** For the subset the listener chooses to own, detectors run blind to group. The comparison uses detector counts only.
5. **Equivalence.** "Fires as often on disliked music" is tested with two one-sided tests (TOST) on the difference in mean FEEL count, margin ±0.5 moves. If equivalence holds, the agent MUST say FEEL describes music generally, not this listener. A non-significant difference test alone is not evidence of similarity.
6. FEEL is not called a predictor unless the top-5 hit rate's 95% lower bound exceeds the null's 95th percentile and the loved and disliked groups are not equivalent.

## 8. Tap accuracy (SPEC REQ-LS-02)

1. **Output latency** is measured by acoustic loopback: the station plays a click, a microphone at the headphone driver records it, and the delay from `audio-pts` to the recorded click is measured over 50 clicks. Where no microphone is available, the tap-along method is used and labeled as such.
2. **Listener motor bias** is measured separately with tap-along on a click train and stored, so it is not mistaken for device latency.
3. **Acceptance.** With latency corrected, taps on 100 audible test events (clicks embedded in music) have their 95th-percentile absolute error ≤ 100 ms.

## 9. Rule-compliance rubric

Each agent statement of a metric value scores 1 if it names its basis in plain words matching SPEC REQ-EVID-12, 0 if it states the value with no basis, and is marked N/A if no value is stated. Each felt-experience claim resting on `PROXY` or `TEXTUAL` support scores 1 if it tells the listener to check by ear (REQ-EVID-13). Each timestamp scores 1 if it matches a stored value, render caption or tap (REQ-EVID-14).

## 10. Study D: BUILD and replays

Runs only if the listener enables history (SPEC REQ-SPOT-04).

- The BUILD criteria were drawn from this listener's play history, so testing them on that same history is circular. Only plays **after** the profile date (2026-10-05) and **before** the track was bought are used.
- Replay rate is adjusted for exposure (plays per week the track was available in the listener's library or playlists).
- Unknown BUILD criteria are kept as a separate count, never treated as fails.
- Owned tracks are a restricted range (the listener liked them enough to buy). Reported as a limitation.

## 11. Reporting

Every study produces a report in `docs/reports/` with the commit hash, model versions, weight hashes, counts, all statistics with intervals, coverage, first-listen counts, the listener's test-retest ceiling, and the conflict-of-interest statement. Negative results are published the same way as positive ones.

## 12. Amendments and looks log

None yet.

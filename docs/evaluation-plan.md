# Evaluation Plan

| Field | Value |
|---|---|
| Version | 0.1.0-draft |
| Status | Normative for SPEC §11 and §12. Pre-registration document. |
| Date | 2026-10-05 |

This plan is committed before any data is collected. Changes after data collection starts MUST be recorded in §9 with the date and reason, and the original text MUST stay visible in version control.

## 1. Questions

| Study | Question |
|---|---|
| A | Does each analyzer agree with the listener's ear well enough to earn its evidence class? |
| B | Does Claude Code with Headphones agree with the listener's ear more often than Claude Code without it? |
| C | Do the FEEL detectors and chill candidates find the moments the listener marks, better than chance? Do they fire as often on music the listener dislikes? |
| D | Does BUILD, scored from audio, predict what the listener replays? |

## 2. Ground truth

The listener's ear, captured on the listening station (SPEC §7.4).

- **Blind capture.** For every track in a held-out split, the listener completes the ear form before any analyzer output or agent answer about that track is shown to them. The station MUST hide analysis results for held-out tracks until the ear form is submitted.
- **First listen matters** for head-nod, hook stickiness and chill. Tracks the listener already knows well are flagged at capture (`familiar: true`) and analyzed separately.
- **Listener consistency.** 15% of tracks, chosen at random, are re-scored at least two weeks later. Test-retest agreement (same statistics as METRICS.md §4.2) is the ceiling any analyzer or agent can be expected to reach, and every agreement number is reported next to it.
- `not_sure` answers are excluded from agreement and their rate is reported.

## 3. Track selection

- Only assets in the listener's library (SPEC REQ-SRC-01).
- At least 120 tracks for Studies A and B combined, drawn to cover the listener's range: the anchor artists, picked and acoustic country, small-group jazz, and records outside the profile.
- **Split by artist**, never by track, so an analyzer cannot be tuned on one song by a band and tested on another by the same band. Calibration split 50%, held-out split 50%.
- **Text availability strata.** Each track is tagged `well_documented` (has a Wikipedia article or at least three professional reviews) or `sparse`. The baseline arm should do better on well-documented tracks. Reporting by stratum shows whether the harness adds most where text is missing.

## 4. Study A: analyzer validation

1. Synthetic suite first (SPEC §11.2). Targets per metric in METRICS.md.
2. Thresholds tuned on the calibration split only, then frozen in a tagged commit.
3. Agreement on the held-out split using METRICS.md §4.2, with bootstrap 95% intervals (10,000 resamples, clustered by track).
4. Promotion to `beta` or `stable` uses only held-out results and the interval rule in METRICS.md §4.2.

## 5. Study B: harness lift

### 5.1 Arms

| Arm | Access |
|---|---|
| Baseline | Claude Code with web search and the official Spotify connector. No Headphones. |
| Harness | The same, plus the Headphones MCP server and skill. |

Both arms use the same pinned model version, the same system prompt apart from the skill, and the same question set. Each arm runs three times per track to measure run-to-run variance.

### 5.2 Questions

For each held-out track, each arm is asked for every metric whose ear value exists: the category (or yes or no, or timestamp) and a confidence from 0 to 1. Both arms may answer "not sure". The prompt names the track by artist and title only.

### 5.3 Outcomes

Primary (pre-registered):

- **H1.** Across metrics with ceiling `MEASURED` or `ESTIMATED`, the harness arm's agreement with the ear exceeds the baseline's by at least 10 percentage points. Test: paired difference in per-item agreement, cluster bootstrap by track, one-sided, alpha 0.05. "Not sure" counts as wrong for this test so that abstaining cannot inflate agreement.

Secondary:

- **Coverage and selective accuracy.** Share of items answered, and agreement among answered items, per arm.
- **Calibration.** Expected calibration error of stated confidence against hit rate, per arm.
- **Rule compliance.** Share of answers that name their evidence class correctly (SPEC REQ-EVID-12). Scored by a rubric on a 20% sample, double-coded by two raters, with agreement reported.
- **Invented timestamps.** Count of timestamps given that match no stored value, render or tap (SPEC REQ-EVID-14). Target for the harness arm: zero.
- **Perceptual metrics.** Agreement on `EAR`-ceiling and `PROXY`-ceiling metrics, reported separately. No lift is predicted here. The point is to see whether either arm pretends to know.
- **By stratum.** All of the above split by `well_documented` and `sparse`.

### 5.4 Threats to validity

- **One listener.** Results describe this listener. That is the purpose, but nothing here generalizes to other people.
- **Leakage.** The harness arm's analyzers are tuned on the calibration split only. The baseline cannot see the ear data. Agent transcripts are checked for any access to the ear store, which the MCP server does not expose for held-out tracks during the benchmark.
- **Master mismatch.** The baseline may draw on text about a different master. Accepted, because the listener hears the owned asset.
- **Model drift.** The model version is pinned and recorded. A rerun on a new version is a new study.

## 6. Study C: FEEL and chills

1. **Hit rate.** For each `c` tap on a first listen, is there a chill candidate within ±1.0 s in the top k (k = 3, 5)? Compare with a null model that places the same number of candidates uniformly at random within the track, repeated 10,000 times.
2. **Control group.** This is the experiment the profile already asks for. The listener chooses 20 records they actively dislike and 20 they love, scores FEEL moves by ear on each, and the harness runs the detectors. Compare FEEL counts between groups with a Mann-Whitney U test. If disliked records also fire three or more moves at a similar rate, FEEL measures something general about music, not something about this listener, and the agent MUST say so when it reports FEEL.
3. FEEL is not called a predictor anywhere in Headphones output unless the hit rate clearly beats the null model (lower bound of the 95% interval above the null's 95th percentile) and the control group separates.

## 7. Study D: BUILD and replays

Runs only if the listener enables BEHAVIORAL metrics (SPEC REQ-SPOT-04).

- For owned tracks with at least five plays in the imported history, correlate the audio-scored BUILD count with replay rate and completion rate (Spearman, cluster bootstrap by artist).
- The profile predicts Ben Folds should chart in the December 2026 Wrapped. That prediction belongs to the profile, not to Headphones, and is not used here.

## 8. Reporting

Every study produces a report in `docs/reports/` with the commit hash, model versions, weight hashes, data counts, all statistics with intervals, and the listener's test-retest ceiling. Negative results are published the same way as positive ones.

## 9. Amendments

None yet.

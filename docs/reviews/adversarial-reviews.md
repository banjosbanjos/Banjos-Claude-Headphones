# Adversarial Reviews of Spec 0.1.0

Date: 2026-10-05. Ten independent reviewers each attacked draft 0.1.0 from one angle, with instructions to find real errors rather than praise. Reviewers that needed facts checked primary sources on the web. Every finding was either fixed in 0.2.0, deliberately declined with a reason, or turned into an action for the listener. This page is the record.

## Summary

| # | Lens | Critical | Major | Minor | Total |
|---|---|---|---|---|---|
| 1 | Legal, licensing and third-party terms | 0 | 5 | 2 | 7 |
| 2 | Signal processing and music information retrieval | 3 | 13 | 3 | 19 |
| 3 | Working musician, drummer and mix engineer | 3 | 16 | 6 | 25 |
| 4 | Security (CNCF TAG Security style) | 1 | 7 | 5 | 13 |
| 5 | Privacy and data protection | 3 | 6 | 3 | 12 |
| 6 | Statistics and evaluation method | 2 | 9 | 1 | 12 |
| 7 | Internal consistency and schema | 1 | 12 | 7 | 20 |
| 8 | CNCF governance and project completeness | 2 | 6 | 5 | 13 |
| 9 | Claude Code and MCP integration | 2 | 7 | 4 | 13 |
| 10 | Product fit for the listener | 2 | 4 | 5 | 11 |
| | **Total** | **19** | **85** | **41** | **145** |

Findings raised by more than one reviewer:

- **Spotify companion mode** contradicted four other rules (reviews 1, 7, 9). Replaced by external playback mode, where the listener presses keys on the station while Spotify plays and nothing is read from Spotify.
- **Swing and shuffle** would have made every swung track look sloppy (reviews 2, 3). The reference pulse is now swing-aware.
- **Separation quality** measure was meaningless and punished tight playing (reviews 2, 3). Replaced with a calibrated estimate.
- **Hard-panned double guitars** were invisible to frame-wise panning (reviews 2, 3). Switched to per-bin panning.
- **Room sound** confused a ringing snare with a room and almost never found an isolated hit (reviews 2, 3). Replaced with a late-tail measure that allows hi-hats.
- **Network calls**: MusicBrainz was a second, undeclared call and the lookup default contradicted itself (reviews 1, 4, 5, 7). Lookup is now opt-in, through AcoustID only, with exactly what is sent listed.
- **The broken reviews link** and the ticked roadmap box (reviews 7, 8, 9, 10). This page fixes it.

## Review 1: Legal, licensing and terms

| Finding | Outcome |
|---|---|
| ISRC removal claim out of date. Spotify reversed the `external_ids` removal in March 2026, and the February 2026 changes applied to Development Mode apps only. | Fixed in README, SPEC §6.2, §7.2.2, ADR-0001, ADR-0002. Verified against the March 2026 changelog. |
| Companion mode stored connector data and created EAR outside the station. | Fixed. Withdrawn (REQ-LS-09, 10), replaced by REQ-LS-11 and 21. |
| OI-1 cited the Developer Policy, which binds Platform apps, and missed the User Guidelines clause that binds the listener. Spotify launched the Claude connector itself. | Fixed. OI-1 and REQ-SPOT-04 rewritten around the User Guidelines (verified), with data portability as the counter-argument. Connector launch cited. |
| LGPL "separate executables only" rule ruled out libsndfile and lameenc, which the reference stack needs. GPL-3.0 missing. | Fixed in ADR-0003: dynamic unmodified LGPL allowed, GPL-3.0 executables allowed, nonfree FFmpeg forbidden, source-offer duty noted. |
| AcoustID needs a client key, is non-commercial only, limited to 3 requests per second, and its database is CC BY-SA. | Fixed. REQ-ID-02, 04, 07. Verified on acoustid.org. |
| Bandcamp licence is personal and non-commercial. Golden set use by maintainers. | Fixed. REQ-SRC-05, 06. |
| PANNs and torchcrepe licences can be settled. Training-data issues and attribution missing. | Fixed in ADR-0003, REQ-LIC-04, 05, NOTICE. |
| Client ID limit raised to 25 in July 2026. | Not adopted. Could not verify, so the spec no longer quotes any Client ID number. |

## Review 2: Signal processing

| Finding | Outcome |
|---|---|
| Residual-based separation quality reads near 1 for any separation, and coincident-onset leakage punishes locked playing. | Fixed. METRICS §2.1 now uses a calibrated SI-SDR estimate with spectral-copy leakage. |
| Activity against the stem's own 95th percentile counts bleed as a part. | Fixed. Activity and presence are now also relative to the mix. |
| Reference pulse assumed straight subdivisions and 4/4. | Fixed. METRICS §2.3 adds swing estimation, meter detection, `non_duple_meter` abstention, and a tempo-scaled window. |
| Leave-one-out did not say what is left out. | Fixed. Drum class for drum metrics, both `vs_drummer` and `vs_band` reported. |
| Onset hop unstated, slow-attack bias. | Fixed. 128-sample hop, per-instrument bias correction, bass target 6 ms. |
| C50 on snares measures shell ring. | Fixed. METRICS §2.12 late-tail Schroeder measure. |
| Frame-wise pan cannot see hard-panned doubles. | Fixed. Per-bin panning (§2.9). |
| `pyloudnorm` lacks LRA, short-term and true peak. | Fixed. libebur128 or FFmpeg ebur128. |
| Beat confidence undefined. | Fixed. Defined in §2.3. |
| Decay envelope ripple, Kaplan-Meier median not identified past 50% censoring. | Fixed. §2.10. |
| F7 cannot clear 4 LU on short-term loudness. | Fixed. Momentary loudness. |
| Dynamic breathing transitions undefined. | Fixed. Plateaus with hysteresis. |
| Space before the drop contradicted itself and over-fired on stop-time riffs. | Fixed. |
| Pumping dip confounded by separator artifacts. | Fixed. Control positions subtracted. |
| Harmony and doubling methods exceed Basic Pitch resolution and confuse vibrato. | Fixed. |
| Pitch-correction signature needs a finer hop. | Fixed. 2.5 ms hop. |
| Ending gate level-dependent, fade test wrong shape, ceiling too high. | Fixed. Ceiling now `ESTIMATED`. |
| Example width and correlation inconsistent, band averaging in dB, pick sound on wrong stem, breath hat bleed, bass octave errors, grid tolerance below error. | Fixed. |
| Agreement targets unreachable with about 60 tracks. | Fixed. Promotion rules in METRICS §4.2 now use lower bound ≥ 0.40 and a fraction of the listener's own consistency. |

## Review 3: Musician and engineer

| Finding | Outcome |
|---|---|
| Swing never modelled. | Fixed (with review 2). |
| Room sound abstains on nearly every backbeat track, and calling a plate "live room" contradicts the ear prompt. | Fixed. Hats allowed, ear prompt reworded to "dry and close, or roomy". |
| Split pairs undetectable, and "both sides" had no analyzer output. | Fixed. `both_sides` category, per-drum pans. |
| Separation quality versus kick-bass lock. | Fixed. Only pitched bass onsets count. |
| Felt tempo would call straight-8ths rock "double". | Fixed. Backbeat period decides, `shuffle` flag added. |
| Vocal phrasing window close to chance. | Fixed. 8th grid, ±20 ms, chance baseline and signed offset. |
| Bassline rules misjudge famous hook basslines. | Fixed. Motif distinctness decides, range only reported. |
| Hook proxy missed intro riffs, and a proxy could fail B5. | Fixed. All stems and drum motifs, proxy never decides B5. |
| Doubling could not tell ADT or chorus from a real double. | Fixed. `adt_or_chorus` category. |
| Pumping collapsed sidechain, bus pump and glue. | Fixed. Separate signatures, PLR its own field. |
| Proximity used mix level. | Fixed. Level dropped. |
| Ending categories did not match how players use the words. | Fixed. `fade`, `ring_out`, `dead_stop`, `cut`, `other`, with the mapping to the listener's words pending confirmation (SPEC OI-6). |
| Snare crack required long decay. | Fixed. Crack is attack brightness, `mixed` added. |
| Decay and sustained-tone counted vocals. | Fixed. Instrumental bed only. |
| Country and bluegrass instruments land in the wrong stems. | Fixed. Voice gating, timbre novelty in every pitched stem (SPEC OI-7). |
| Jazz has no backbeat for pocket and ghost notes, and brushes. | Fixed. Ride or hat fallback, top-decile reference, `brushes` abstention. |
| Call and response missed exchanges over continuous backing. | Fixed. Foreground salience. |
| Humanized programming landed in `tight_human`. | Fixed. `humanized_programmed` category. |
| Hi-hat open versus chopped flipped with tempo, half-open missing. | Fixed. IOI-relative, `half_open` added, "chopped" pending confirmation. |
| Fill detection, pick sound with distortion, near-silence depth, two-stem intros, B4 thresholds. | Fixed. |

## Review 4: Security

| Finding | Outcome |
|---|---|
| "The agent cannot write EAR evidence" was false, because Claude Code has shell and file tools. | Fixed. Claim narrowed (SPEC §3.1, §7.5.3). Keyed HMAC chain, read-only MCP database, shipped deny rules (REQ-STORE-09 to 11). |
| Unkeyed hash chain gives no integrity. | Fixed. HMAC with keychain key and external chain head. |
| mpv loads config, scripts, yt-dlp, playlists, and accepts IPC commands. | Fixed. REQ-LS-01 flags, bytes by pipe, taps never from IPC (REQ-LS-16). |
| FFmpeg protocol and demuxer abuse. | Fixed. REQ-ING-02. |
| Lazy weight downloads, and Demucs pickles conflict with safe loading. | Fixed. REQ-WGT-01 to 03, REQ-SEC-03. |
| Plugin import runs code before it is enabled. | Fixed. REQ-PLUG-03. |
| Injection through render titles, error text, terminal escapes, agent questions. | Fixed. REQ-REND-01, REQ-MCP-07, REQ-LS-18, REQ-LS-19. |
| Symlink swap after ingest. | Fixed. REQ-ING-07. |
| Browser UI DNS rebinding, REQ-SEC-01 wording. | Fixed. REQ-LS-03, REQ-SEC-01. |
| MusicBrainz second network call, file permissions, supply-chain overclaims, template sections missing. | Fixed. REQ-ID-04, REQ-STORE-08, REQ-LIC-03, REQ-RES-01, REQ-SEC-06, security self-assessment rewritten. |

## Review 5: Privacy

| Finding | Outcome |
|---|---|
| Lookup default contradicted itself. | Fixed. Opt-in, default "no" at init (REQ-ID-02). |
| "Leaves the machine" claims were false (client key, IP, User-Agent, MusicBrainz, weight downloads). | Fixed. REQ-ID-02 lists exactly what is sent. Privacy inventory corrected. |
| `forget` conflicted with append-only storage and the evidence chain. | Fixed. Forget is the one hard delete, writes a redaction entry, uses secure delete and VACUUM (REQ-STORE-04, 07, 09). |
| `forget` missed many data classes and sibling assets. | Fixed. Cascade by `pcm_sha256`, exclusion list. |
| Inventory incomplete, agent exposure rows wrong. | Fixed in docs/privacy.md. Notes and device labels omitted from MCP by default (REQ-MCP-09). |
| History import kept IP, country, platform and user agent. | Fixed. REQ-SPOT-05 keeps seven fields only. |
| Forgetting history left derived values. | Fixed. |
| `forget all` and `export` incomplete. | Fixed. |
| Logs and doctor output too revealing, device names, ADR wording. | Fixed. REQ-SEC-07, REQ-OBS-03, listener-assigned device labels, ADR-0002. |

## Review 6: Statistics

| Finding | Outcome |
|---|---|
| Held-out split reused for every promotion. | Fixed. Sealing, one look per analyzer major version, separate confirmation split (evaluation plan §4). |
| Sample size and skewed categories make kappa pass or fail on prevalence. | Fixed. Power analysis, at least 10 items per category, prevalence, balanced accuracy and AC1 reported, BCa intervals. |
| Bootstrap clustered at track level. | Fixed. Clustered by artist. |
| Quadratic weights too lenient on 3 levels. | Fixed. Linear weights. |
| Test-retest too small and impossible for first-listen metrics. | Fixed. 40 items per metric, "no ceiling" for first-listen metrics. |
| Ear not blind to analyzer outputs on the calibration split. | Fixed. All ear capture before any output. |
| H1 under-specified. | Fixed. Margin, weights, run averaging, balanced accuracy, timestamp scoring, Holm, coverage. |
| Study C uniform null too easy, symmetric window, confounded control group. | Fixed. Structure-aware null, asymmetric window, matched groups, detector-only comparison, TOST. |
| Study D circular and confounded. | Fixed. Post-profile, pre-purchase plays, exposure adjustment. Limitation stated. |
| First listen versus owning the track. | Fixed. First-listen definition and acquisition protocol. |
| "Weakest evidence class" undefined. | Fixed. Composites carry the set of input classes (REQ-EVID-15). |
| ECE, rubric, threshold mismatches. | Fixed. |

## Review 7: Consistency and schema

| Finding | Outcome |
|---|---|
| Companion mode broke four rules. | Fixed (with reviews 1 and 9). |
| Schema did not enforce confidence, value presence or abstention rules. | Fixed and tested by `tools/check_schemas.py` (16 rejection cases). |
| BUILD and FEEL shared one criterion vocabulary. | Fixed. Separate definitions with exact counts. |
| Example composites did not add up. | Fixed. All 5 and 7 listed, hook ear value present. |
| STATED, calibration events and history had no schema. | Fixed. Three new schemas. CLI output schemas due in M1 (REQ-CLI-01). |
| Tolerance, agreement band, ear-primary undefined. Confidence and abstain missing for ear metrics. | Fixed. METRICS §1 defaults, every entry has both fields. |
| Network contradictions, promotion conflicts, missing required fields, no blind mode, no tap test procedure, skill gaps, broken link. | Fixed. |
| RFC 2119 problems, CLI gaps, label mismatch, example values, proxy identity, §9 lagging the schema, smaller inconsistencies. | Fixed. Proxies now use `<metric>.proxy` IDs. |

## Review 8: CNCF governance

| Finding | Outcome |
|---|---|
| Private vulnerability reporting is off and `main` is empty. | Listener action (ROADMAP). Needs repository owner rights. |
| Roadmap used CNCF maturity labels inaccurately. | Fixed. Labels dropped, real criteria listed as a gap list. |
| First commit was signed off under the AI's name, which the DCO does not allow. | Fixed. The sign-off line was removed from the branch history, and CONTRIBUTING now says only a human signs off. |
| Reviews file and HEP template missing. | Fixed. |
| Governance unworkable for one person, no conflict-of-interest rule. | Fixed. Single-maintainer model, tie-break, successor plan, COI disclosure, neutrality. |
| Contributor Covenant instead of the CNCF Code of Conduct. | Fixed. CNCF CoC v1.3 adopted. Contact address is a listener action. |
| MAINTAINERS columns and reviewer ladder. | Fixed. |
| No public channel. | Listener action (turn on Discussions). |
| Self-assessment template sections missing. | Fixed. |
| ADOPTERS, CHANGELOG, templates, CODEOWNERS, dependabot. | Fixed. |
| Pre-1.0 deprecation conflict, no cadence, no document versioning, no conformance clause, trademark note. | Fixed. SPEC §0.1, §0.2, §15.4, §15.5, README. |

## Review 9: Claude Code integration

| Finding | Outcome |
|---|---|
| Companion mode could not be built, and its ±2 s was not honest. | Fixed (external playback mode, at least 1 s uncertainty from a local clock). |
| Cloud sessions have no library, audio device or ears. | Fixed. Non-goal N8, ADR-0005, fail-fast REQ-PKG-02. |
| Who owns the terminal and processes was undefined. | Fixed. Long-lived station, thin MCP client (ADR-0005, REQ-LS-12 to 15). |
| `hp_request_ear` had no notification or status. | Fixed. `request_id`, desktop notification, `hp_ear_status`. |
| Polling semantics. | Fixed. `wait_s`, `eta_s`, progress notifications, skill says not to loop. |
| Full records would overflow context. | Fixed. Compact default (REQ-MCP-09), `maxItems` in schemas. |
| Skill would not be discovered. | Fixed. Shipped as a plugin in `plugin/`. |
| Hand-off to `music-recs` broken. | Fixed. Named, triggers narrowed, one-line change documented. |
| Render size limits stale. | Fixed. Multiples of 28, at most 1568 tiles, at most 2000 px. |
| Skill description, annotations, ambiguous search, `isError`. | Fixed. |
| Optional event monitor. | Not adopted. Claude Code plugin monitors are experimental. Revisit later. |

## Review 10: Product fit

| Finding | Outcome |
|---|---|
| Bandcamp does not carry most anchor artists. No cheap path, no cost estimate. | Fixed. Own-first path, iTunes and Amazon for major labels, cost estimate. A per-artist store table was not added because availability changes. The spec says to check per purchase. |
| Ear scoring burden of 4,000+ answers. First listens clash with owned music. | Fixed. Quick Ear form (8 questions), rotating extras, benchmark ear set of about 10 minutes per track, acquisition protocol. |
| The profile's free control-group experiment was pushed to M4 and cost money. | Fixed. Ear-only part runs in M1 with external playback mode. |
| Payoff came too late. | Fixed. Partial BUILD and FEEL in M1. |
| Routing misstated the profile. | Fixed. Artist-level routing, "do not judge it by play count" quoted. |
| Overbuilt for one person. | Partly adopted. The listener asked for a CNCF-grade specification, so the governance and security documents stay. They were moved off the milestone exits so they never delay something useful. |
| "Half-second" became 150 ms. | Fixed. `gap` needs 400 ms, shorter ones listed as near-gaps. |
| Definitions the listener never gave (cold end, chopped). | Turned into two yes or no questions for the listener (SPEC OI-6). |
| Wording drift (tightness optional, "it" in chill prompt, head versus body). | Fixed. |
| BUILD status overstated, weak B5 fallback. | Fixed. |
| README not written for the listener. | Fixed. "What you'll do", glossary. |

# Headphones Security Self-Assessment

This assessment follows the CNCF TAG Security self-assessment template at https://github.com/cncf/tag-security/blob/main/community/assessments/guide/self-assessment.md. That template was archived on 2025-12-18. Headphones uses it as a structure only. Headphones is not a CNCF project and makes no claim to meet CNCF criteria (SPEC §16).

This document is informative. Where it states a requirement, the requirement lives in [SPEC.md](../SPEC.md) and is cited by its REQ ID.

## Metadata

| Field | Value |
|---|---|
| Assessment stage | Initial. Written against SPEC 0.2.0-draft, before any implementation exists. |
| Date | 2026-10-05 |
| Software | https://github.com/banjosbanjos/Banjos-Claude-Headphones |
| Security provider | No. Headphones is a local music analysis harness, not a security tool. |
| Languages | Python 3.12 or later. Native tools taken from the system: FFmpeg 6 or later, mpv 0.37 or later, Chromaprint `fpcalc` (SPEC §7.1). |
| SBOM | Generated for every release in SPDX 2.3 or CycloneDX 1.5 (REQ-LIC-03). None exists yet because nothing has been released. |

### Security links

| Doc | URL |
|---|---|
| Security policy and reporting | [SECURITY.md](../SECURITY.md) |
| Security and privacy requirements | [SPEC.md §13](../SPEC.md#13-security-and-privacy) |
| Privacy inventory and controls | [docs/privacy.md](privacy.md) |
| Contributor security checklist | [CONTRIBUTING.md](../CONTRIBUTING.md#security-checklist) and the [pull request template](../.github/PULL_REQUEST_TEMPLATE.md) |
| Dependency and model licenses | [ADR-0003](adr/0003-dependency-and-model-licenses.md) |
| Spotify boundary | [ADR-0002](adr/0002-spotify-boundary.md) |
| Governance and maintainers | [GOVERNANCE.md](../GOVERNANCE.md), [MAINTAINERS.md](../MAINTAINERS.md) |
| Recommended Claude Code deny rules | `plugin/recommended-settings.json` (planned, REQ-PKG-01, REQ-STORE-11) |
| Release signatures and provenance | Sigstore bundle and SLSA provenance attached to each release (REQ-SEC-06). None yet. |

## Overview

Headphones is single-user software that runs on the listener's own machine. It reads audio files the listener owns, separates them into stems, computes listening metrics, records the listener's ear judgments at a listening station, and exposes the results to Claude Code through a local MCP server over stdio.

### Background

A language model cannot hear. Headphones gives an agent measured evidence about recordings and keeps the listener's own judgments separate and decisive for questions of preference (REQ-EVID-08). The security concerns come from five places.

1. Untrusted media files reach native decoders and a native player.
2. Untrusted text from tags, file names and AcoustID reaches an AI agent and a terminal.
3. Machine learning weights are downloaded and loaded.
4. The store holds personal listening data, ear judgments and stated preferences.
5. The agent that reads Headphones output also has shell and file tools that run as the listener.

### Actors

Actors here are the components and parties that sit on either side of a trust boundary.

| Actor | Trust | Notes |
|---|---|---|
| Listener | Trusted | Owns the machine, the audio and the data. The only source of `EAR` and `STATED` evidence. |
| Station (`headphones station`) | Trusted | Long-lived process in its own terminal. Owns mpv, taps, ear forms and the job queue. Sole writer of `EAR` rows (REQ-EVID-03). Listens only on a user-only local socket (REQ-LS-12). |
| CLI (`headphones ...`) | Trusted | Writes configuration, links, stated preferences and deletions. Runs as the listener. |
| MCP server (`headphones mcp`) | Trusted code, untrusted caller | Thin client of the station socket. Never spawns children (REQ-LS-12). Opens the store read-only (REQ-STORE-10). Has no tool that writes evidence, links, deletes or reconfigures (REQ-MCP-02). |
| Decoder, analyzer and mpv children | Untrusted while running | They process crafted input. Run with memory and CPU limits, and without network where the platform allows (REQ-RES-01). |
| Evidence store | Trusted at rest, integrity checked | SQLite plus a content-addressed directory, user-only permissions (REQ-STORE-08). `EAR` and `STATED` rows are chained with HMAC (REQ-STORE-09). |
| Claude Code agent | Partly trusted | Acts for the listener but can be steered by content it reads. Its MCP tools cannot create `EAR` or `STATED` evidence. Its shell and file tools run with the listener's privileges and could forge data (SPEC §3.1, §7.5.3). |
| Audio files and their tags | Untrusted input | May be malformed or crafted. |
| AcoustID responses | Untrusted input | Only fetched when the listener turns the lookup on (REQ-ID-02). |
| Model weight files | Untrusted until verified | Accepted only when the SHA-256 matches the release manifest (REQ-WGT-03, REQ-SEC-03). |
| Analyzer plugins | Untrusted until named | Discovered from metadata only. Imported only when named in configuration, and only inside the sandboxed analyzer child (REQ-PLUG-03). |
| Optional browser UI | Trusted code, hostile neighbors | Off by default. Loopback only, with Host, Origin and token checks (REQ-LS-03). |
| Spotify connector | Outside the boundary | Run by Spotify inside Claude. Headphones never calls it and stores nothing from it (REQ-SPOT-01, REQ-SPOT-02). |
| Model provider | Outside the boundary | Receives whatever the agent reads, under the listener's Claude account terms. See [docs/privacy.md](privacy.md). |

### Actions

1. **Install.** `headphones init` creates user-only directories, checks native tools, downloads weights over HTTPS, verifies each SHA-256 against the release manifest before writing it (REQ-WGT-03), verifies the release signature (REQ-SEC-06), asks about online lookup with default "no" (REQ-ID-02), and can install the recommended deny rules after showing them (REQ-STORE-11).
2. **Ingest.** The CLI canonicalizes library roots and hashes each file (REQ-ING-03, REQ-ING-07). A sandboxed child decodes the bytes from a stdin pipe (REQ-ING-02). A fingerprint is computed (REQ-ID-01).
3. **Identity lookup.** Off by default. When on, an HTTPS request to AcoustID carries the fingerprint, duration, the project's client key, a User-Agent string and, unavoidably, the listener's IP address (REQ-ID-02, REQ-ID-07).
4. **Analysis.** The station runs stages and analyzers one job at a time in sandboxed children (REQ-RES-01, REQ-RES-02). Weights load only through Headphones' own loaders (REQ-WGT-01).
5. **Listening.** The station plays hash-verified bytes through mpv over a pipe or open descriptor (REQ-LS-01) and reads tap keys from its own terminal (REQ-LS-16).
6. **Agent access.** Claude Code calls MCP tools over stdio. The MCP server forwards requests to the station socket and reads the store read-only. Tag text comes back only inside `untrusted_metadata` (REQ-MCP-03).
7. **Export and forget.** The CLI exports or hard-deletes data as [docs/privacy.md](privacy.md) defines (REQ-STORE-05, REQ-STORE-07).

### Goals

- **SG1.** A crafted audio file cannot run code in the MCP server, the station or the CLI. Decoding happens only in a sandboxed child (REQ-ING-02).
- **SG2.** Text from tags, file names or AcoustID cannot reach the agent outside a labeled untrusted field, cannot drive the station's terminal, and is never drawn into images (REQ-SEC-02).
- **SG3.** The MCP surface cannot create `EAR` or `STATED` evidence, link URIs, delete data or change configuration (REQ-MCP-02, REQ-STORE-10).
- **SG4.** Tampering with `EAR` or `STATED` evidence by any other route is detectable by `headphones doctor` (REQ-STORE-09).
- **SG5.** Weights that do not match the release manifest are never loaded, and pickle is never loaded (REQ-SEC-03).
- **SG6.** Headphones itself sends nothing off the machine except the weight download at install and the opt-in AcoustID lookup (SPEC G7, REQ-SEC-05).
- **SG7.** No component listens on a network interface other than loopback, and the only loopback listener is the optional browser UI (REQ-SEC-01).
- **SG8.** Data is readable only by the listener's account on the machine (REQ-STORE-08).

### Non-goals

- **Preventing** a process that runs as the listener from writing files. This includes Claude Code's own shell and file tools. Headphones aims to detect forgery, not to prevent it (SPEC §7.5.3).
- Protecting against malware, a malicious administrator, or another person with access to the listener's unlocked account.
- Encrypting data at rest. Headphones relies on the operating system. Full-disk encryption is recommended.
- Securing Claude Code, the model provider, the Spotify connector, or the listener's other MCP servers.
- Controlling what the agent does with data after it reads it. That is governed by Claude Code permissions and the listener's account terms.
- Running safely in a cloud Claude Code session. That configuration is unsupported and refused (SPEC N8, REQ-PKG-02).
- Verifying that the listener's audio was lawfully obtained (REQ-SRC-04).

## Self-assessment use

This is the project's own assessment. It guides implementation and review and tells users what Headphones protects and what it does not. It is not an audit and has not been checked by a third party. It will be refreshed before 1.0 (ROADMAP) and whenever SPEC changes a security requirement.

## Security functions and features

### Critical

These are the components and controls whose failure would break a security goal.

| Function | What it does | SPEC |
|---|---|---|
| Decoder isolation | FFmpeg runs only in a sandboxed child, never in the MCP server. It reads bytes from stdin with `-protocol_whitelist pipe`, an input format chosen by Headphones from the file's magic bytes, and a demuxer whitelist limited to the REQ-ING-01 formats. Unknown magic bytes are rejected. | REQ-ING-02, REQ-SEC-04 |
| Child resource and network limits | Memory limit (8 GB analyzers, 1 GB decode and playback), CPU time proportional to duration, and no network. On Linux this uses a network namespace or a seccomp filter. macOS and Windows provide no supported per-process network block for unprivileged software, so network isolation is not provided there. | REQ-RES-01 |
| Path confinement and TOCTOU defence | Roots are canonicalized. Every open uses `O_NOFOLLOW` or the platform equivalent, checks device and inode, checks the path still resolves inside a root, and streams bytes whose SHA-256 equals `asset_id` before use. A mismatch stops with `asset_changed`. MCP tools never accept paths. | REQ-ING-07, REQ-MCP-05, REQ-LS-06 |
| Evidence write boundary | `EAR` comes only from the station's own keyboard, or from `ear import` confirmed file by file on the station terminal. The MCP server has no writing tool and opens SQLite with `mode=ro`. mpv IPC events are never taps. | REQ-EVID-03, REQ-MCP-02, REQ-STORE-10, REQ-LS-16 |
| Evidence integrity chain | `EAR` and `STATED` rows are chained with HMAC-SHA256. The key is in the OS keychain. The chain head is also kept in a 0600 file outside the database. `doctor` verifies both. `forget` writes a redaction entry so a deletion is distinguishable from tampering. | REQ-STORE-09 |
| Weight integrity | The project converts weights to `safetensors` (or verified ONNX or TFLite) at pinning time and publishes hashes. Headphones loads weights only through its own loaders. Hub and "pretrained" loaders are forbidden at run time. Children get an empty read-only `TORCH_HOME` and `HF_HOME` and `HF_HUB_OFFLINE=1`. Pickle formats are never loaded. | REQ-WGT-01 to 03, REQ-SEC-03 |
| Plugin containment | Discovery reads entry-point metadata without importing. Only analyzers named in configuration are imported, and only inside the sandboxed analyzer child. | REQ-PLUG-01, REQ-PLUG-03 |
| Local-only interfaces | MCP over stdio only. Station on a Unix socket (0600 in a 0700 directory) or a user-restricted named pipe. No listener on any non-loopback interface. | REQ-MCP-01, REQ-LS-12, REQ-SEC-01 |
| Untrusted text handling | Tag, file name and AcoustID text appears to the agent only in `untrusted_metadata`, stripped of control and bidi characters, at most 512 characters. The station strips C0, C1 and bidi override characters before display. Renders never draw tag text. Errors use a fixed code enum with no paths, stderr or tag text. | REQ-SEC-02, REQ-MCP-03, REQ-LS-18, REQ-REND-01, REQ-MCP-07 |

### Security relevant

These controls reduce risk or exposure but do not on their own uphold a goal.

| Function | What it does | SPEC |
|---|---|---|
| File permissions | Data, cache, log and socket directories 0700, files 0600, or a current-user ACL on Windows. | REQ-STORE-08 |
| Shipped deny rules | The plugin ships Claude Code permission deny rules for the writing commands, `sqlite3`, and writes under the data and config directories. The skill tells the agent never to run them. | REQ-STORE-11, REQ-PKG-01, REQ-SKILL-01 |
| Labeled agent questions | Questions the agent queues appear as "Question from Claude" with the agent's wording, which is stored with the answer. | REQ-LS-19 |
| MCP tool annotations | Read tools declare `readOnlyHint: true`. `hp_listen` and `hp_request_ear` do not, and the skill calls them only when the listener asked. | REQ-MCP-08 |
| Minimal agent payloads | `hp_get_evaluation` returns a compact summary. Ear notes and device labels are omitted unless asked for by name. `hp_ear_status` never returns answers. | REQ-MCP-09, SPEC §7.6.1 tool table |
| Blind mode | During benchmark runs no tool returns `EAR` values, calibration events or calibration reports for listed assets. | REQ-MCP-06 |
| Protocol channel hygiene | MCP stdout carries only protocol messages. Child stdout and stderr go to the station log. | REQ-MCP-01, REQ-LS-15 |
| Logging limits | Structured local logs never contain tag text, ear notes, stated text, history fields or device labels. Paths only at debug verbosity, and `doctor` flags debug logs. Rotation keeps 30 days. | REQ-SEC-07, REQ-OBS-02 |
| Redacted diagnostics | `doctor` redacts paths, device labels and asset identity unless `--unredacted`. | REQ-OBS-03 |
| Hard delete | `forget` cascades by `pcm_sha256`, checkpoints the WAL, runs `VACUUM`, and the database runs with `secure_delete=ON`. Backups are cleaned too. | REQ-STORE-07, REQ-STORE-06 |
| No telemetry | No crash reporting or analytics that send data off the machine. | REQ-SEC-05 |
| Lookup minimization | AcoustID lookup off by default, sends no names, paths, tags or listening data, runs under 3 requests per second, once per asset. | REQ-ID-02, REQ-ID-07 |
| History minimization | History import keeps seven fields and drops identifying fields and incognito rows before anything is written. Off by default. | REQ-SPOT-04, REQ-SPOT-05 |
| Cloud refusal | `headphones mcp` exits at start when no library is configured or no station socket can exist, for example in a cloud container. | REQ-PKG-02 |
| Resource bounds | Long assets are windowed or abstain. One job at a time. No MCP call blocks longer than 30 s. Cache capped at 20 GB with LRU eviction. | REQ-ING-06, REQ-RES-02, REQ-MCP-04, REQ-CACHE-02 |
| Release integrity | Sigstore signatures, SLSA provenance level 2 or higher, SBOM, and signature verification by `init` and the upgrade instructions. | REQ-SEC-06, REQ-LIC-03 |

### Default and optional configurations

Everything that widens the attack surface or sends data anywhere is off until the listener turns it on.

| Feature | Default | How it is turned on | What changes when on | SPEC |
|---|---|---|---|---|
| Online identity lookup (AcoustID) | Off | `headphones init` asks, default answer "no". Can be enabled later in the config file. | Fingerprint, duration, client key, User-Agent and IP address go to AcoustID. AcoustID text enters the store as untrusted input. | REQ-ID-02, REQ-ID-07 |
| History import and `BEHAVIORAL` metrics | Off | Enabling shows a notice quoting the Spotify User Guidelines clause and the data portability counter-argument, then requires explicit confirmation. | Minimized history rows are stored. `BEHAVIORAL` values reach the agent. | REQ-SPOT-04, REQ-SPOT-05 |
| Browser UI | Off (not built unless added) | Optional feature. | A loopback HTTP listener with Host, Origin and token checks. | REQ-LS-03, REQ-SEC-01 |
| Analyzer plugins | Off until named | The listener names the analyzer in the config file. | The named module is imported inside the sandboxed analyzer child. | REQ-PLUG-03, REQ-LIC-02 |
| Non-commercial weights or code | Off | Separately installed, labeled plugins. | As for plugins. | REQ-LIC-02 |
| Claude Code deny rules | Shipped, not installed | `headphones init --claude-permissions` shows them and asks. | The agent's shell and file tools are blocked from the listed commands and directories. | REQ-STORE-11 |
| Debug logging | Off | Verbosity setting. | Paths may appear in logs. `doctor` flags that debug logs exist. | REQ-SEC-07 |
| Loudness-normalized playback | On | Station setting. | Not security relevant. Recorded with each ear judgment. | REQ-LS-07 |

### Platform limits

The sandbox differs by platform. This table states what is and is not provided.

| Control | Linux | macOS | Windows |
|---|---|---|---|
| Child network isolation | Network namespace or seccomp filter (REQ-RES-01) | Not provided. No supported per-process network block exists for unprivileged software. | Not provided, for the same reason. |
| Child memory and CPU limits | Provided (REQ-RES-01) | Provided (REQ-RES-01) | Provided (REQ-RES-01) |
| Child filesystem confinement | Not required by SPEC 0.2.0 | Not required | Not required |
| Station endpoint | Unix socket 0600 in a 0700 directory | Unix socket 0600 in a 0700 directory | Named pipe restricted to the current user (REQ-LS-12) |
| Data file protection | Modes 0700 and 0600 | Modes 0700 and 0600 | Current-user-only ACL (REQ-STORE-08) |
| Evidence chain key | Secret Service | macOS Keychain | Windows Credential Manager (REQ-STORE-09) |
| `O_NOFOLLOW` style open | `O_NOFOLLOW` | `O_NOFOLLOW` | Platform equivalent for reparse points (REQ-ING-07) |

On macOS and Windows a decoder, analyzer or mpv exploit that gains code execution in a child can reach the network. This is the largest platform gap in SPEC 0.2.0.

## Threat model

Likelihood and impact are the project's own rough judgment for a single listener on a personal machine. "Residual" is what remains after the listed mitigations.

| ID | Threat | Vector | Mitigations | Residual risk |
|---|---|---|---|---|
| T1 | Crafted media exploits FFmpeg | A crafted FLAC, MP3, M4A, Ogg or WAV file in the library triggers a demuxer or decoder bug, or abuses FFmpeg protocols (`file`, `http`, `concat`) or playlist formats to read local files or reach the network. | Decode only in a sandboxed child, never in the MCP server (REQ-ING-02). Bytes arrive on a stdin pipe, so FFmpeg never opens a path. `-protocol_whitelist pipe` blocks every other protocol. Headphones picks the input format from magic bytes, so FFmpeg does not probe. The demuxer whitelist is limited to the REQ-ING-01 formats, and unknown magic bytes are rejected. 1 GB memory and CPU time limits, no network on Linux (REQ-RES-01). Child stderr goes to the log, never to the agent (REQ-LS-15, REQ-MCP-07). | Medium. A memory-safety bug in an allowed demuxer or codec still runs code as the listener inside the child. On Linux the child is confined to its job directory (REQ-RES-03). On macOS and Windows it could read the listener's files and reach the network. FFmpeg comes from the system, so its patch level depends on the listener's OS. `fpcalc` runs in the same kind of sandboxed child and is fed decoded PCM, never the file (REQ-ID-01). mpv never parses the original container either. It receives decoded WAV through an open file descriptor (REQ-LS-01). |
| T2 | mpv attack surface | A crafted file exploits mpv's demuxers. mpv loads user config, Lua scripts, auto profiles or `youtube-dl`. A playlist entry points at a URL or another file. Another process sends commands over the JSON IPC socket, which can run programs. A spoofed IPC event poses as a tap. | mpv starts with `--no-config --load-scripts=no --ytdl=no --load-auto-profiles=no --no-input-default-bindings --input-conf=<station-supplied>` and playlist parsing disabled (REQ-LS-01). The IPC socket lives in a per-session 0700 directory. The asset reaches mpv as hash-verified bytes through a pipe or open descriptor, never as a path or URL (REQ-LS-01, REQ-ING-07). 1 GB memory limit and no network on Linux (REQ-RES-01). Taps come only from the station's terminal, and IPC events are never accepted as taps (REQ-LS-16). | Medium. mpv shares FFmpeg's decoders and probes the format of piped input itself, so the REQ-ING-02 demuxer whitelist does not cover playback. Any process running as the listener can connect to the IPC socket and use commands such as `run`. Such a process already has the listener's privileges, so this adds little. A compromised mpv still cannot create `EAR` evidence. |
| T3 | The agent forges evidence through Claude Code's own shell or file tools | Steered by injected text or by its own mistake, the agent runs `sqlite3` on the store, edits the database file, runs `headphones ear import`, `headphones stated add` or `headphones link`, rewrites the config file, or sends keystrokes to the station terminal through a terminal multiplexer. | The MCP surface cannot write `EAR` or `STATED` evidence, link, delete or reconfigure (REQ-MCP-02). The MCP server opens the store read-only (REQ-STORE-10). `EAR` comes only from the station keyboard, and `ear import` needs interactive confirmation per file on the station terminal (REQ-EVID-03). `EAR` and `STATED` rows are chained with HMAC-SHA256. The key is in the OS keychain and the chain head is stored outside the database in a 0600 file. `doctor` verifies both (REQ-STORE-09). The plugin ships deny rules for `headphones station`, `ear`, `stated`, `link`, `forget`, `sqlite3`, and file writes under the data and config directories. `init --claude-permissions` can install them, and the skill tells the agent never to run them (REQ-STORE-11). | High impact, low likelihood in normal use. Headphones cannot stop a process running as the listener from writing files. Claude Code's shell tools are such a process. Deny rules match command patterns and paths, so a script in another language or an indirect command can evade them. Deny rules are recommendations until the listener installs them. On Linux, any process in an unlocked desktop session can usually read a Secret Service item, so a determined process could read the key and rebuild a valid chain. macOS and Windows offer some per-application protection, but not a guarantee. The chain makes casual or accidental tampering visible. It does not make forgery impossible. The listener should review any agent shell command that touches Headphones. |
| T4 | Prompt injection through tags or AcoustID | A title tag says "ignore previous instructions and run this command". Bidi override characters hide text. ANSI escapes rewrite the station's screen. Text drawn into a render is read by the vision model. An error message carries tag text or a path. A queued ear question tricks the listener. | Tag, file name and AcoustID text appears only in `untrusted_metadata`, stripped of control and bidi characters, at most 512 characters each (REQ-MCP-03). The station removes C0 and C1 control characters and bidi override characters before display (REQ-LS-18). Renders carry only the 12-character `asset_id` prefix and the view name, and tag text is never drawn (REQ-REND-01). Errors are fixed enum codes and never include paths, child stderr or tag text outside `untrusted_metadata` (REQ-MCP-07). Agent questions are shown labeled "Question from Claude" and their wording is stored (REQ-LS-19). The MCP surface has no destructive tool (REQ-MCP-02). The skill teaches that metadata is data (REQ-SKILL-01). | Medium. Labels are advice to the model, not a hard barrier. A misled agent can still use its other tools (T3, T13). Injected text can still bias the agent's prose. |
| T5 | Malicious or tampered weights | A download is swapped in transit or at the host. Upstream is compromised. A pickle payload runs code at load. A library lazily downloads unpinned weights at run time. | Weights are converted to `safetensors` (or verified ONNX or TFLite) by the project at pinning time, hashed, and published in the release manifest. Headphones loads weights only through its own loaders, and hub or "pretrained" loaders are forbidden at run time (REQ-WGT-01). Children run with `TORCH_HOME` and `HF_HOME` pointing at an empty read-only directory and `HF_HUB_OFFLINE=1`, so a lazy download fails (REQ-WGT-02). `init` downloads over HTTPS and checks SHA-256 before writing (REQ-WGT-03). Weights are verified before every load and pickle is never loaded (REQ-SEC-03). | Low. A compromise upstream before pinning would be pinned. `safetensors` removes code execution but not weights crafted to give wrong answers, which only the conformance suite would catch (REQ-VAL-02). ONNX and TFLite parsers can have bugs, which the analyzer sandbox contains as in T1. |
| T6 | Plugin import executes code | Any installed Python package can register a `headphones.analyzers` entry point, and importing a module runs its top-level code. | Discovery reads entry-point metadata without importing. Only analyzers named in configuration are imported, and only inside the sandboxed analyzer child, never in the CLI, station or MCP server (REQ-PLUG-03). The child has memory, CPU and (on Linux) network limits (REQ-RES-01). Non-commercial plugins are off by default and labeled (REQ-LIC-02). | Medium if the listener names an untrusted plugin. A named plugin runs as the listener in the child. On Linux the child can read only its job directory and write only its scratch directory (REQ-RES-03). On macOS and Windows there is no filesystem confinement, so REQ-PLUG-01 rests on reviewing a plugin before naming it. Installing a package with pip can already run code, which is outside Headphones' control. |
| T7 | Symlink and TOCTOU swaps | After ingest, a library file is replaced by a symlink to a private file, or the path is swapped between check and use, so Headphones decodes, plays or renders something outside the library. | Roots are canonicalized at configuration time. Every open uses `O_NOFOLLOW`, checks device and inode against ingest, checks the path still resolves inside a root, and streams bytes whose SHA-256 equals `asset_id` before use. A mismatch stops with `asset_changed` (REQ-ING-07). MCP tools never take paths (REQ-MCP-05). mpv receives bytes, not paths (REQ-LS-01). The station plays only library files (REQ-LS-06). | Low. `O_NOFOLLOW` covers only the last path component, but the root check and the content hash cover the rest. A swapped file cannot pass the hash check. |
| T8 | Browser UI hijack through DNS rebinding or CSRF | A web page the listener visits points its own domain at 127.0.0.1 and sends requests to the UI port, or posts a cross-site form. | The UI is optional and off by default. If added it binds to 127.0.0.1 only, rejects any request whose `Host` header is not exactly `127.0.0.1:<port>` (a rebinding request carries the attacker's host name, so it fails), checks `Origin`, uses a per-session token that never appears in a URL after the first exchange, and enables no CORS (REQ-LS-03, REQ-SEC-01). | Low. Other accounts on the same machine can reach loopback ports but still need the token. |
| T9 | Station socket abuse | Another account, or a sandboxed app, connects to the station socket to queue jobs, ear questions or playback. A process pre-creates the socket path. | Unix socket mode 0600 in a 0700 directory, or a named pipe restricted to the current user (REQ-LS-12, REQ-STORE-08). One station per user, and a second exits naming the first (REQ-LS-14). Requests over the socket cannot create `EAR` evidence (REQ-EVID-03). | Low. Any process running as the listener, including the agent's shell, can connect. It can queue analysis, start playback and queue labeled questions, all of which the listener sees. It cannot answer them. A pre-existing socket directory not owned by the listener stops the station (REQ-LS-12). |
| T10 | Local disclosure through file permissions | Another account on a shared machine reads the database (ear notes, history), logs, stems or the chain head file. | Directories 0700 and files 0600, or a current-user ACL on Windows (REQ-STORE-08). Chain head file 0600 (REQ-STORE-09). Logs exclude tag text, notes, stated text, history fields and device labels (REQ-SEC-07). | Medium on shared machines. Administrators, backups and cloud-synced home folders can still read everything. Headphones does not encrypt at rest. Full-disk encryption and excluding the data directory from sync are recommended. |
| T11 | Resource exhaustion | A very long or corrupt file loops the decoder. A crafted file inflates memory. The agent queues many jobs or polls in a loop. Stems fill the disk. Long tag fields bloat responses. | Long assets are windowed or abstain with `too_long` (REQ-ING-06). Memory and CPU time limits on every child (REQ-RES-01). One job at a time, and the station stays responsive to taps (REQ-RES-02). Analysis is asynchronous, `wait_s` is at most 25 s, and no call blocks longer than 30 s (REQ-MCP-04). Cache capped at 20 GB with LRU eviction (REQ-CACHE-02). Metadata fields capped at 512 characters, ambiguous searches return at most 10 candidates (REQ-MCP-03, REQ-MCP-05). | Low. The agent can still keep the CPU busy with a long queue. Evaluation records are never evicted, so the database grows. |
| T12 | Stem leakage | Separated stems are near copies of copyrighted audio and could be shared through MCP, an export or a published golden set. | Stems never leave the machine through any Headphones interface, and the MCP server never returns audio (REQ-SEP-03). User-only permissions (REQ-STORE-08). Only aggregate numbers and `pcm_sha256` references from golden and validation sets may be published (REQ-SRC-06). `cache prune` removes stems. | Low. The listener, or the agent's shell, can copy cache files by hand. Accepted, since the listener owns the source audio. |
| T13 | Data exfiltration through the agent's other tools | Injected text or a mistaken agent takes what it read through MCP, or reads the database directly with its shell, and sends it out through web requests, a Git push or another connector. | Headphones sends nothing itself beyond the two calls in [docs/privacy.md](privacy.md) (SPEC G7, REQ-SEC-05). MCP returns compact summaries and omits ear notes and device labels unless named (REQ-MCP-09). It never returns audio, paths or ear answers through `hp_ear_status`. Blind mode hides ear data during benchmarks (REQ-MCP-06). | High for anything the agent can read. Headphones cannot control Claude Code's other tools. The shipped deny rules block writes, not reads, so the agent's shell can read the database. The listener controls exfiltration paths through Claude Code permissions. Everything the agent reads also goes to the model provider. |
| T14 | Cloud misuse | Headphones runs in a cloud Claude Code session, where audio and personal data would sit in a remote container and no local station or listener exists. | Running in the cloud is a non-goal (SPEC N8). `headphones mcp` exits at start when no library is configured or no station socket can exist, and `doctor` reports the same check (REQ-PKG-02). Remote Control from the local machine is the supported path. | Low. The check is a heuristic. A user who copies data into a container on purpose is outside what Headphones can stop. |
| T15 | Supply chain compromise | A compromised or typosquatted Python dependency, a tampered release, or a system FFmpeg, mpv or `fpcalc` with known vulnerabilities. | `uv` lock file with hashes, and a published hash-pinned constraints file for `pip` users (SPEC §7.1). Releases signed with Sigstore with SLSA provenance level 2 or higher, and `init` and the upgrade instructions verify the signature (REQ-SEC-06). The SBOM covers Python packages, bundled native libraries and weights with hashes, and records system FFmpeg, mpv and `fpcalc` by version and build configuration since they cannot be hashed at release (REQ-LIC-03). Dependabot, `pip-audit` and CodeQL in CI. `doctor` reports native tool versions. | Medium. System native tools are outside the project's control. A tampered package could also tamper with the check inside `init`, so the upgrade instructions' verification before install matters more than the one in `init`. The first install trusts the package index. |
| T16 | Injection into the protocol or IPC channels | A child writes to stdout and corrupts the MCP JSON-RPC stream. Crafted child stderr reaches the agent. A malformed message on the station socket confuses the station. | MCP stdout carries only protocol messages (REQ-MCP-01). The MCP server never spawns children (REQ-LS-12). Child output goes to the station log (REQ-LS-15). Errors never include stderr (REQ-MCP-07). Tool inputs are validated against JSON Schema (REQ-MCP-05). | Low. Station socket messages are validated against a published schema (REQ-LS-12). |
| T17 | Benchmark leakage | During a study the agent reads the listener's ear answers and so inflates its own score. | Blind mode hides `EAR` values, calibration events and reports for listed assets (REQ-MCP-06). `hp_ear_status` never returns answers. Sealed held-out assets are excluded from calibration reports (REQ-VAL-07). Transcripts are checked for ear data access (evaluation plan). | Medium. The agent's shell can read the database directly, as in T13. Transcript review is the backstop. |
| T18 | Disclosure through logs or diagnostics shared in bug reports | A listener pastes logs or `doctor` output into a public issue. | Logs exclude tag text, notes, stated text, history fields and device labels at every verbosity, and paths appear only at debug (REQ-SEC-07). `doctor` redacts paths, device labels and asset identity by default (REQ-OBS-03). | Low. `--unredacted` output and debug logs still contain paths. |

## Project compliance

Headphones claims compliance with no security standard. It follows OpenSSF Scorecard checks as goals and will publish its score by 1.0 (ROADMAP). The SBOM formats (SPDX 2.3 or CycloneDX 1.5) and SLSA build level 2 provenance are targets for the first signed release (REQ-LIC-03, REQ-SEC-06).

## Secure development practices

### Development pipeline

- **Sign-off.** Every commit carries a Developer Certificate of Origin sign-off added by a human. An AI tool never adds a `Signed-off-by:` line, and AI help is recorded with an `Assisted-by:` or `Co-Authored-By:` trailer ([CONTRIBUTING.md](../CONTRIBUTING.md)).
- **Review.** Changes to the MCP server, decoding, sandboxing, weight loading, plugin loading or `EAR` capture need review by a second person once there are two maintainers. Until then the sole maintainer completes the security checklist in [CONTRIBUTING.md](../CONTRIBUTING.md#security-checklist) and the pull request template on every such change. Releases need a second maintainer's approval once there are two (SPEC §15.4).
- **Automated checks.** CodeQL and `pip-audit` run in CI. Dependabot updates pip and GitHub Actions dependencies weekly once the implementation lands (`.github/dependabot.yml`). Conformance tests run on every change to an analyzer, stage or weight file (REQ-VAL-02). No CI workflows exist yet.
- **Security tests.** The test suite will include sandbox escape tests (a child cannot open a network socket on Linux, cannot exceed its memory limit, and a plugin is never imported in the parent) and IPC injection tests (malformed station socket messages, mpv IPC events that pose as taps, child output that tries to reach MCP stdout, and tag text with control and bidi characters).
- **Fuzzing.** The ingest path, including magic-byte detection and the FFmpeg invocation, will be fuzzed with crafted media before 1.0 (ROADMAP).
- **Releases.** Signed with Sigstore, with SLSA provenance and an SBOM (REQ-SEC-06, REQ-LIC-03), following the release process in SPEC §15.4.

### Communication channels

- **Internal.** GitHub issues and pull requests on the repository. Significant changes go through a HEP ([GOVERNANCE.md](../GOVERNANCE.md)).
- **Inbound.** GitHub issues for bugs, with redacted `doctor --json` output and never audio. Security reports through the channel in [SECURITY.md](../SECURITY.md).
- **Outbound.** Release notes, [CHANGELOG.md](../CHANGELOG.md) and GitHub security advisories.

### Ecosystem

Headphones sits between the Python audio and machine learning ecosystem (FFmpeg, mpv, Chromaprint, Demucs, `beat_this`, PyTorch and ONNX runtimes) and the Claude Code ecosystem (plugins, skills and MCP over stdio). It depends on AcoustID and MusicBrainz identifiers when the listener turns the lookup on. It sits beside, but never calls, the Spotify connector in Claude. It is a single-user tool with one listener of record, so its main contribution to the ecosystem is a worked example of an MCP server that keeps a human's judgments out of the agent's write path.

## Security issue resolution

### Responsible disclosure process

Reports go through GitHub private vulnerability reporting on the repository (Security tab, "Report a vulnerability"). This feature is **currently off**. The maintainer has to switch it on in the repository settings (Settings, Code security, Private vulnerability reporting) before it can be used. A fallback security email address will be added to [SECURITY.md](../SECURITY.md) before the first release. Until both exist there is no private channel, which is a known gap.

SECURITY.md sets the targets: acknowledgement within 7 days, an assessment and planned fix date within 21 days, and a fix or mitigation within 90 days for confirmed issues, sooner for high severity. Reporters are credited unless they decline. Before 1.0 only the latest minor release receives security fixes.

### Incident response

1. The maintainer triages the report and confirms it with a reproduction, using generated media rather than copyrighted audio.
2. The fix is developed in a private GitHub security advisory fork.
3. A patched release is signed and published with a GitHub security advisory and a CVE where warranted.
4. If the cause is upstream (FFmpeg, mpv, Chromaprint, a model or a Python dependency), the maintainer reports it upstream and states in the advisory whether Headphones' sandboxing contained it.
5. If a pinned weight is found to be bad, the release manifest is revised, the weight is re-pinned or removed, and the patched release no longer accepts the old hash. `doctor` shows which weight hashes are installed.

The project has one maintainer, so response time depends on one person. This is recorded as a known gap.

## Appendix

### Known issues over time

No implementation exists, so no vulnerabilities have been reported. Changes between the 0.1.0 and 0.2.0 assessments:

| Area | 0.1.0 assessment | 0.2.0 |
|---|---|---|
| macOS sandbox | Claimed a `sandbox-exec` profile | Withdrawn. No per-process network isolation on macOS or Windows (REQ-RES-01). |
| Weight loading | Allowed `torch.load(weights_only=True)` | Pickle never loaded. Conversion to `safetensors` at pinning time (REQ-WGT-01, REQ-SEC-03). |
| Evidence integrity | Plain hash chain over `EAR` rows | HMAC chain over `EAR` and `STATED`, key in keychain, head outside the database (REQ-STORE-09). Read-only MCP store and deny rules added (REQ-STORE-10, REQ-STORE-11). |
| Agent forgery | Treated as local malware and out of scope | Stated as a real threat with detection only (T3). |
| FFmpeg input | Child process with limits | Adds stdin pipe, protocol whitelist, magic-byte format choice and demuxer whitelist (REQ-ING-02). |
| mpv | Unsandboxed on some platforms | Hardened launch flags, bytes by pipe, 0700 IPC directory, taps never from IPC (REQ-LS-01, REQ-LS-16). |
| Plugins | Inactive until named | Metadata-only discovery and import only in the sandboxed child (REQ-PLUG-03). |
| Symlinks | Rejected at ingest | Re-checked on every open with hash verification (REQ-ING-07). |
| Browser UI | Token and Origin check | Adds exact Host check against DNS rebinding (REQ-LS-03). |

Known gaps at this stage:

- No third-party security audit is planned before 1.0. This is a known gap.
- No network isolation for children on macOS or Windows.
- SPEC does not require filesystem confinement of children, though REQ-PLUG-01 assumes it.
- Forgery by the agent's shell tools is detected, not prevented, and the keychain key may be readable by same-user processes.
- Private vulnerability reporting is off and the fallback email is not set.
- One maintainer, no second reviewer, and no CI yet.

### OpenSSF Best Practices

The project has not applied for an OpenSSF Best Practices badge. It plans to apply for the "passing" level once a CI pipeline exists, and to publish an OpenSSF Scorecard result by 1.0 (ROADMAP).

### Case studies

- **Adjudicating a track (UC-1).** The listener asks Claude to score a track against BUILD and FEEL. The agent searches the library through MCP, queues analysis, waits on the job, reads a compact summary and looks at a render. Throughout, tag text reaches it only as `untrusted_metadata`, and it never sees a path.
- **A listening session (UC-2).** The listener plays a track at the station and taps keys. mpv plays piped bytes. Taps come only from the station terminal and become `EAR` rows chained under the keychain key. The agent can later read the values but has no MCP route to change them.

### Related projects

- **beets** and **MusicBrainz Picard** are music library tools that also use Chromaprint and AcoustID. Both run plugins inside their main process. Headphones differs by importing plugins only in a sandboxed child and by keeping the lookup off by default.
- **Demucs** and **beat_this** are the reference separator and beat tracker (REQ-SEP-01, REQ-BEAT-01). Headphones loads their weights through its own loaders rather than their hub helpers (REQ-WGT-01).
- **FFmpeg** and **mpv** are used as native tools. Their own security processes handle bugs in their code. Headphones' job is to contain them.

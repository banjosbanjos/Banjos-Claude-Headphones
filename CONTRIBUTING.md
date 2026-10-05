# Contributing

Thanks for wanting to help. Headphones measures how records sound for one listener, so a few rules here are stricter than usual.

## Before you start

- Read [SPEC.md](SPEC.md) §5 (evidence model) and §6 (legal and sourcing). Pull requests that add audio capture from streaming services, lyric handling, or Spotify API clients will be closed.
- For anything that counts as significant under [GOVERNANCE.md](GOVERNANCE.md), open a HEP first.

## Developer Certificate of Origin

Every commit must be signed off (`git commit -s`), certifying the [Developer Certificate of Origin 1.1](https://developercertificate.org/).

## AI-assisted contributions

AI tools may help write changes.

- The DCO sign-off is a personal legal statement. Only a human may add a `Signed-off-by:` line. An AI tool MUST NOT add one.
- AI involvement MUST be recorded in the commit message with an `Assisted-by:` or `Co-Authored-By:` trailer naming the tool.
- The human who signs off is responsible for the change, including its license, its correctness and its security.

## Pull requests

- One logical change per pull request.
- Link the requirement IDs (`REQ-...`) or metric IDs your change touches.
- Analyzer changes must include conformance tests (SPEC §11.2) and a note of expected effect on golden-set outputs.
- New dependencies or model weights must state their license and fit the [ADR-0003](docs/adr/0003-dependency-and-model-licenses.md) allowlist.
- Do not commit audio. The golden set is referenced by hash only.

## Security checklist

The same checklist is in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md). Fill it in there.

Required for changes to the MCP server, decoding, sandboxing, weight loading, plugin loading or EAR capture:

- [ ] No new network calls or listeners.
- [ ] No path accepted from the agent.
- [ ] No new way to create EAR or STATED evidence.
- [ ] Untrusted text stays inside `untrusted_metadata` and is length-limited.
- [ ] Weights are hash-pinned and loaded safely.
- [ ] Child processes keep their resource limits.

## Reporting bugs

Open an issue with `headphones doctor --json` output. Never attach audio. For security issues see [SECURITY.md](SECURITY.md).

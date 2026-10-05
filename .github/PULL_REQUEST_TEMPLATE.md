## Summary

What this change does and why.

## Linked requirements and metrics

- Requirement IDs: `REQ-...`
- Metric IDs:
- HEP (if significant under GOVERNANCE.md):

## Checklist

- [ ] Every commit is signed off (DCO) by a human. No AI tool added a `Signed-off-by:` line.
- [ ] If an AI tool helped, the commits carry an `Assisted-by:` or `Co-Authored-By:` trailer.
- [ ] Tests and conformance tests (SPEC §11.2) are added or updated.
- [ ] The license of any new dependency or model weight fits the [ADR-0003](../docs/adr/0003-dependency-and-model-licenses.md) allowlist.
- [ ] No audio is committed.

## Security checklist

Required for changes to the MCP server, decoding, sandboxing, weight loading, plugin loading or EAR capture. Otherwise write "Not applicable".

- [ ] No new network calls or listeners.
- [ ] No path accepted from the agent.
- [ ] No new way to create EAR or STATED evidence.
- [ ] Untrusted text stays inside `untrusted_metadata` and is length-limited.
- [ ] Weights are hash-pinned and loaded safely.
- [ ] Child processes keep their resource limits.

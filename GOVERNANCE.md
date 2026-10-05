# Governance

Headphones is a small, single-listener project. This governance is sized for that and says how it grows if others join. It borrows its shape from CNCF project governance. Headphones is not a CNCF project.

## Roles

| Role | Who | Rights and duties |
|---|---|---|
| Listener of record | The person whose ears define ground truth (see MAINTAINERS.md) | Final say on metric definitions, ear scales, the BUILD and FEEL composites and anything that changes what "agreement with the ear" means. |
| Maintainer | Listed in MAINTAINERS.md | Merge rights. Review. Releases. Security response. |
| Reviewer | Listed in MAINTAINERS.md | Approving reviews count toward merge requirements in their area. |
| Contributor | Anyone | Propose changes under CONTRIBUTING.md. |

## Decisions

1. **Everyday changes** (fixes, docs, tests, analyzer improvements that do not change a metric's definition): pull request with one maintainer approval. Authors do not approve their own pull requests once there are two maintainers.
2. **Significant changes** need a Headphones Enhancement Proposal (HEP) in `docs/heps/`, open for comment at least 7 days. Significant means any of: a new or changed metric definition, a new evidence class or a change to precedence (SPEC §5), a change to the MCP tool surface, a change to the schema major version, a new network call, a new dependency outside the ADR-0003 allowlist, or any change to SPEC §6 (legal and sourcing).
3. **Lazy consensus.** A HEP is accepted when no maintainer objects within the comment period. An objection must give a reason and, where possible, an alternative.
4. **If consensus fails**, maintainers vote. Simple majority of maintainers decides, except that changes to metric definitions or ear scales also need the listener of record's agreement.
5. **SPEC §6 and ADR-0002 changes** always need the listener of record's agreement and a written note of which third-party terms were checked and when.

## Maintainers

- Added by consensus of existing maintainers after sustained contribution (as a guide, ten merged pull requests or two accepted HEPs over three months).
- Step down by notice. Become emeritus after twelve months without activity.
- Removed by a two-thirds vote of the other maintainers for a Code of Conduct violation or sustained inactivity without notice.

## Releases

Any maintainer may cut a release once SPEC §15.4 is satisfied. Once there are two maintainers, a release needs approval from a second.

## Changes to this document

By HEP with a 14-day comment period and two-thirds of maintainers in favor. While there is one maintainer, that maintainer may amend it with a 14-day public notice in an issue.

## Code of Conduct

All participants follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

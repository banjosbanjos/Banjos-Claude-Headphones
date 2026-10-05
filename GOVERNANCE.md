# Governance

Headphones is a small, pre-1.0 project built for one listener. This governance is sized for one person. It says how the project grows if others join. It borrows its shape from CNCF project governance, but Headphones is not a CNCF project.

## Single-maintainer model

While there is one maintainer, the project runs on a single-maintainer (BDFL) model. That maintainer decides. Significant changes still go through a HEP posted publicly for 7 days, so the reasoning is on record. The rest of this document applies in full once there are two or more maintainers.

## Roles

| Role | Who | Rights and duties |
|---|---|---|
| Listener of record | The person whose ears define ground truth (see [MAINTAINERS.md](MAINTAINERS.md)) | Final say on metric definitions, ear scales, the BUILD and FEEL composites and anything that changes what "agreement with the ear" means. |
| Maintainer | Listed in MAINTAINERS.md | Merge rights. Review. Releases. Security response. |
| Reviewer | Listed in MAINTAINERS.md | Approving reviews count toward merge requirements in their area. |
| Contributor | Anyone | Propose changes under [CONTRIBUTING.md](CONTRIBUTING.md). |

## Contributor ladder

1. **Contributor.** Anyone who opens an issue, a pull request or a review.
2. **Reviewer.** A contributor with 5 merged pull requests or 3 substantive reviews over 2 months, nominated by a maintainer. No maintainer objects within 7 days.
3. **Maintainer.** Added by consensus of existing maintainers after sustained contribution. As a guide, ten merged pull requests or two accepted HEPs over three months.

## Decisions

1. **Everyday changes** (fixes, docs, tests, analyzer improvements that do not change a metric's definition) need a pull request with one maintainer approval. Once there are two maintainers, authors do not approve their own pull requests.
2. **Significant changes** need a Headphones Enhancement Proposal (HEP), open for comment at least 7 days. Significant means any of these:
   - a new or changed metric definition
   - a new evidence class or a change to precedence (SPEC §5)
   - a change to the MCP tool surface
   - a change to the schema major version
   - a new network call
   - a new dependency outside the ADR-0003 allowlist
   - any change to SPEC §6 (legal and sourcing)
3. **Lazy consensus.** A HEP is accepted when no maintainer objects within the comment period. An objection gives a reason and, where possible, an alternative.
4. **If consensus fails**, maintainers vote. A simple majority of maintainers decides. Changes to metric definitions or ear scales also need the listener of record's agreement.
5. **Tie-break.** If maintainers split evenly, the listener of record decides questions about metric definitions and ear scales. On anything else, the status quo stays.
6. **SPEC §6 and ADR-0002 changes** always need the listener of record's agreement. They also need a written note of which third-party terms were checked and when.

## HEPs and ADRs

- HEPs live in `docs/heps/`. Copy [docs/heps/0000-template.md](docs/heps/0000-template.md) to start one.
- HEPs are numbered in sequence. The next HEP takes the next unused number.
- A HEP has one of these statuses:
  - **Draft.** The author is still writing it.
  - **Discussion.** Posted publicly and open for comment.
  - **Accepted.** Approved under the decision rules above.
  - **Rejected.** Not approved.
  - **Withdrawn.** The author pulled it.
  - **Implemented.** The accepted change has landed.
  - **Superseded.** Replaced by a later HEP, which it names.
- ADRs in `docs/adr/` record decisions already made about architecture. A HEP is the proposal process. An accepted HEP that changes architecture also produces a new ADR or amends an existing one.

## Public channel

The public channel is GitHub Discussions. The maintainer must enable Discussions on the repository. Until then, GitHub issues are the public channel. HEPs, governance notices and votes are posted there.

## Maintainers

- Added as described in the contributor ladder.
- Step down by notice. Become emeritus after twelve months without activity.
- Removed for a Code of Conduct violation or sustained inactivity without notice. Removal needs two-thirds of all other maintainers and at least two votes in favor. One person cannot remove another.

## Succession and archiving

If the listener of record steps away, the remaining maintainers do one of two things:

1. **Name a new listener of record.** This starts a new ground-truth dataset. Old ear data stays tied to the person who produced it. It is never reassigned to someone else.
2. **Archive the project.** The repository is marked archived and the README says why.

If there are no remaining maintainers, the project is archived.

## Conflict of interest

The listener of record defines ground truth. The same person writes and approves the pre-registered evaluation plan ([docs/evaluation-plan.md](docs/evaluation-plan.md)). That is a conflict of interest.

- Every evaluation report MUST disclose this conflict.
- When any outside person is available, they SHOULD sign off the pre-registration before data collection starts.

## Neutrality

No vendor or company controls Headphones. The project names Spotify, Claude and music stores only to describe what it works with. Naming them implies no endorsement or affiliation.

## Releases

Any maintainer may cut a release once SPEC §15.4 is satisfied. Once there are two maintainers, a release needs approval from a second.

## Changes to this document

By HEP with a 14-day comment period and two-thirds of maintainers in favor. While there is one maintainer, that maintainer may amend it after a 14-day public notice in the public channel.

## Code of Conduct

All participants follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

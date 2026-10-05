# Security Policy

## Supported versions

Before 1.0.0, only the latest minor release receives security fixes.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Do not open a public issue.

Private vulnerability reporting is currently off. The maintainer must switch it on in the repository settings (Settings, Code security, Private vulnerability reporting).

**Fallback email: not yet set.** A fallback security email address MUST be added here before the first release.

Please include affected version, platform, steps to reproduce, and impact. Do not include copyrighted audio. Describe crafted files or attach ones you generated yourself.

## What to expect

- Acknowledgement within 7 days.
- An assessment and planned fix date within 21 days.
- A fix or mitigation within 90 days for confirmed issues, sooner for high severity.
- A GitHub security advisory and CVE where warranted, with credit unless you decline it.

## Scope

In scope: the Headphones codebase, its MCP server, its listening station, its handling of media files, weights and plugins. Out of scope: Claude Code, the model provider, the Spotify connector, FFmpeg and mpv themselves (report those upstream, though we want to know if Headphones' sandboxing failed to contain them).

See [docs/security-self-assessment.md](docs/security-self-assessment.md) for the threat model.

# ADR-0005: Local station architecture

- Status: Accepted
- Date: 2026-10-05

## Context

Claude Code runs in the listener's terminal and starts MCP servers as child processes over stdio. A stdio MCP server has no terminal of its own, so it cannot draw a listening interface or read tap keys, and any child process that writes to stdout corrupts the protocol stream. A server tied to one Claude Code session also stops playback when the session ends, and two sessions would start two servers fighting over one audio device and one database.

The listener also uses Claude Code in cloud sessions. A cloud container has no audio library, no audio device and no headphones.

## Decision

1. **A long-lived station.** `headphones station` runs in its own terminal. It owns mpv, reads tap keys on its own terminal, holds the ear form queue and the analysis job queue, and is the only writer of EAR evidence. One per user.
2. **A thin MCP server.** `headphones mcp` talks to the station over a user-only local socket (Unix socket mode 0600, or a restricted Windows named pipe). It never spawns playback or analysis. When the station is not running, tools return `station_not_running` with the command to start it.
3. **Local only.** Headphones and the Claude Code session using it run on the listener's machine. To use it away from that machine, the listener runs Claude Code Remote Control there and drives it from claude.ai or the mobile app. `headphones mcp` fails fast inside a cloud container.
4. **Packaged as a Claude Code plugin** in `plugin/`, bundling the skill, the MCP server configuration and recommended permission deny rules.

## Consequences

- The listener keeps two terminals open while listening: Claude Code and the station.
- Playback and analysis survive Claude Code restarts.
- The cloud-session workflow the listener sometimes uses does not work for listening. That is a hard limit of where the audio and the ears are.

## Alternatives considered

- **Station inside the MCP server.** Rejected for the terminal and stdout reasons above.
- **A network service the cloud session can reach.** Rejected. It would expose the library and evidence store to the network and break SPEC REQ-SEC-01.

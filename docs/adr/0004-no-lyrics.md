# ADR-0004: No lyrics

- Status: Accepted
- Date: 2026-10-05

## Context

The listener's music profile says to judge sound, not subject, and never analyze or mention lyrics. When lyric criteria were removed from earlier scoring, the resonance hit rate rose from 49% to 78%. Lyrics are also separately copyrighted text.

## Decision

Headphones does not transcribe, store, score or display lyrics. No speech-to-text model is included. Vocal metrics measure acoustic properties only: placement, breath, doubling, harmony count, proximity and timing. BUILD criterion 4 asks for clear enunciation, which cannot be judged without hearing words, so that part is always left to the listener's ear (Quick Ear Q7).

## Consequences

- Diction is never computed.
- The event tagger's `singing` and `speech` classes are used only to gate vocal frames and to flag spoken passages as candidate kept moments, never to recognize words.

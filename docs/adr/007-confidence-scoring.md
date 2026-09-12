# ADR 007 — Confidence scoring

## Status

Accepted

## Context

Models often emit false precision ("87.3% certain"). Decision-makers need a transparent, conservative score.

## Decision

Compute a decision-support score from evidence quality weights, relevance, unresolved contradictions and coverage gaps. Label bands as HIGH/MEDIUM/LOW. Never present the score as a calibrated probability.

## Consequences

- Scores are deterministic and unit-tested.
- Weak blogs cannot outrank government sources when stronger evidence exists.
- The critic and HITL gates consume the same metric.

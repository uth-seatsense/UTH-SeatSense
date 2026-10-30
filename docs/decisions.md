# Architecture decisions

## Initial service boundaries

- **Status:** Accepted for the project scaffold
- **Decision:** Keep the web UI, business API, and CV processing in separate
  service directories, with PostgreSQL as the shared persistence layer.
- **Reason:** The components have distinct responsibilities and runtime needs.
- **Follow-up:** Validate deployment, authentication, and inter-service
  communication requirements with the team.

## SEAT-17 CV output and counting semantics

- **Status:** Implemented in CV, pending team review.
- **Date:** 2026-10-30.
- **Decision:** Version the transport-neutral CV output as 1.0. Keep aggregate
  count records separate from local bbox debug records. Define the output
  before Backend implements ingestion; no HTTP endpoint is assumed yet.
- **Counting:** Visible person count is independent of cumulative line IN/OUT.
  Only estimate room occupancy when an initial value is explicitly configured.
  Clamp negative estimates to zero while flagging underflow.
- **Tracking:** Bottom-center anchors cross a finite normalized segment, with
  deadband, cooldown and stale-state expiry. Counters reset for each session.
- **Follow-up:** Backend ingestion, storage and UI are separate stages.

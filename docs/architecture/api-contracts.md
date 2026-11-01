# API contracts

## Backend

- `GET /health`: service health response.
- `/api/v1/occupancy`, `/rooms`, `/reservations`, `/checkin`, `/dashboard`:
  reserved router prefixes; business operations are not implemented.

## Computer vision

- `GET /health`: CV service health response.

CV offline output schema 1.0 is documented in [CV data contract](cv-data-contract.md).
It is a file-based producer contract; no Backend ingestion endpoint is assumed.

### Local CV testing UI

- `GET /`: local HTML testing interface; `/static/` contains its assets.
- `GET /api/config`: model availability and selected device, no local path.
- `POST /api/jobs`: multipart `file` video and JSON string `options`; returns
  202 with job ID. Limit 200 MB; one job at a time (409 when busy), 503 if
  model missing, 415 unsupported extension, 422 invalid options.
- `GET /api/jobs/{id}`: status, latest record and matching JPEG base64,
  recent events, sanitized summary and error. Status progresses through
  uploading/loading/processing to completed/cancelled/failed.
- `POST /api/jobs/{id}/stop`: cooperative cancellation after current frame.
- `GET /api/jobs/{id}/preview`: latest JPEG, 404 before first frame.
- `GET /api/jobs/{id}/files/{kind}`: csv/jsonl/debug/events/summary; only after
  completed/cancelled (409 otherwise). Unknown ID or kind returns 404.

These are CV testing routes, not Backend business endpoints. Job metadata is
in memory and disappears on restart; outputs remain local until manually removed.

### Browser webcam testing

- `POST /api/webcam`: JSON options as for video; reserves the inference slot
  and starts a fresh tracking session, returning 202 with job ID.
- `POST /api/webcam/{id}/frame`: JPEG bytes, maximum 2 MB, maximum decoded
  edge 1920 px. Returns count record with source_type webcam and debug bbox.
  One frame at a time; 409 if busy/stopped, 422 invalid frame.
- Stop and exports use the same job endpoints. Webcam source timestamps use
  monotonic time since session start; recorded_at is UTC processing time.
- Browser obtains camera only after explicit Start Test and permission.
  No audio or webcam video recording. Stop before leaving the page; a crashed
  client may require restarting the local service to release an orphan session.

Define request/response schemas and error semantics for each business endpoint
before implementing clients or workflows.

# API contracts

## Backend

- `GET /health`: service health response.
- `/api/v1/occupancy`, `/rooms`, `/reservations`, `/checkin`, `/dashboard`:
  reserved router prefixes; business operations are not implemented.

## Computer vision

- `GET /health`: CV service health response.

CV offline output schema 1.0 is documented in [CV data contract](cv-data-contract.md).
It is a file-based producer contract; no Backend ingestion endpoint is assumed.

Define request/response schemas and error semantics for each business endpoint
before implementing clients or workflows.

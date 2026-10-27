# API contracts

## Backend

- `GET /health`: service health response.
- `/api/v1/occupancy`, `/rooms`, `/reservations`, `/checkin`, `/dashboard`:
  reserved router prefixes; business operations are not implemented.

## Computer vision

- `GET /health`: CV service health response.

Define request/response schemas and error semantics for each business endpoint
before implementing clients or workflows.

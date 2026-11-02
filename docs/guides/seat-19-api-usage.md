# SEAT-19 Backend API usage

This guide describes the Backend endpoints for CV ingestion and the Frontend's latest live occupancy view. Field semantics and full validation rules are in the [shared API contract](../architecture/api-contracts.md).

## Start the development services

From the repository root, configure `.env` using `.env.example`, then run:

```sh
docker compose up --build -d
```

The API is available at `http://localhost:8000`; interactive OpenAPI docs are at `http://localhost:8000/docs`. On a new PostgreSQL volume, Compose applies the SQL files in `database/init/` in order. An existing database needs the reviewed `database/init/002_cv_count_records.sql` migration applied once; the application does not run schema migrations automatically.

For existing databases that still use the legacy `rooms` schema, apply `database/init/003_sync_rooms_schema.sql` once. This migration adds the `code`, `building`, and `is_active` columns required by the current backend model. It maps room ID `1` to `FLOOR_1` and room ID `2` to `FLOOR_2`. Review existing room data before applying it, especially if the database contains a different room layout.

## CV to Backend: submit a batch

```http
POST /api/v1/cv/count-records
Content-Type: application/json
```

The batch must contain 1–1000 CV v1.0 records. Backend validates every record and saves the whole batch in one transaction. Example:

```json
{
  "records": [
    {
      "schema_version": "1.0",
      "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
      "camera_id": "cam-01",
      "room_id": "FLOOR_1",
      "source_type": "webcam",
      "frame_index": 100,
      "timestamp_ms": 10000.0,
      "recorded_at": "2026-10-30T00:00:00Z",
      "people_count": 3,
      "tracked_count": 2,
      "line_enabled": true,
      "in_count": 4,
      "out_count": 1,
      "initial_occupancy": 0,
      "estimated_occupancy": 3,
      "occupancy_underflow": false
    }
  ]
}
```

Successful response (`200 OK`):

```json
{
  "status": "accepted",
  "created_count": 1,
  "duplicate_count": 0,
  "records": [
    {
      "record_id": 8123,
      "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
      "frame_index": 100,
      "room_code": "FLOOR_1",
      "room_id": 1,
      "received_at": "2026-10-30T00:00:01Z",
      "duplicate": false
    }
  ]
}
```

For a minimal request with `curl`, save the request JSON as `count-batch.json` and run:

```sh
curl -X POST http://localhost:8000/api/v1/cv/count-records \
  -H "Content-Type: application/json" \
  --data-binary @count-batch.json
```

Backend preserves the order of records in the response. An identical retry with the same `(session_id, frame_index)` is accepted as a duplicate. Reusing that key with different CV data returns `409 cv_record_conflict` and rolls back the complete batch. Unknown room codes are preserved in `room_code` and return `room_id: null`.

## Backend to Frontend: read latest live occupancy

```http
GET /api/v1/occupancy/rooms/{room_id}/latest
```

`room_id` in the URL is the numeric Backend room ID. Only the newest mapped `webcam` record is returned; video records and other cameras are not combined.

```json
{
  "room_id": 1,
  "room_code": "FLOOR_1",
  "camera_id": "cam-01",
  "source_type": "webcam",
  "people_count": 3,
  "tracked_count": 2,
  "estimated_occupancy": 3,
  "occupancy_underflow": false,
  "recorded_at": "2026-10-30T00:00:00Z",
  "received_at": "2026-10-30T00:00:01Z",
  "is_stale": false
}
```

The `is_stale` flag becomes true when `received_at` is more than 30 seconds old. Frontend polls every 5 seconds. `estimated_occupancy: null` means unknown; zero is a valid count. `people_count` describes people visible to the camera, not necessarily the total room occupancy.

## Errors and retries

Error responses use this envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more CV records are invalid",
    "details": [
      {"field": "records[0].tracked_count", "issue": "must not exceed people_count"}
    ]
  }
}
```

| HTTP status | Code | Meaning |
| --- | --- | --- |
| `400` | `malformed_json` | Request body is not valid JSON. |
| `404` | `room_not_found` | The Backend room ID does not exist. |
| `404` | `occupancy_not_found` | The room exists but has no mapped webcam record. |
| `409` | `cv_record_conflict` | A session/frame key was reused with different CV data. |
| `422` | `validation_error` | Required data is missing or violates the contract. |
| `503` | `database_unavailable` | Database operation failed; retry the same batch keys. |

CV retries network timeouts and `503` responses up to three times, after 1, 2, and 4 seconds, using the same session/frame keys. Do not retry `400`, `409`, or `422` without correcting the cause. Keep unacknowledged records in the CV sender until they can be replayed.

## Verify

Run the Backend tests from `backend/`:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The regular API tests use isolated SQLite and do not alter the development PostgreSQL database. The opt-in PostgreSQL tests are documented in [`backend/README.md`](../../backend/README.md).
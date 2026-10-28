# UTH-SeatSense

UTH-SeatSense is a starter monorepo for a university seat and room occupancy
platform. It separates the computer-vision service, application API, web UI,
database, tests, and project documentation.

## Requirements

- Docker Desktop with Docker Compose
- Git

## Run locally

1. Copy `.env.example` to `.env` and replace `POSTGRES_PASSWORD` with a local
   development password. Do not commit `.env`.
2. Start the services:

   ```sh
   docker compose up --build
   ```

3. Open the frontend at <http://localhost:3000>, the backend API docs at
   <http://localhost:8000/docs>, and the CV API docs at
   <http://localhost:8001/docs>.

## Service status

| Service | Status | Details |
| --- | --- | --- |
| PostgreSQL | Ready | Starts from the pinned `postgres:16.6-alpine` image, waits for its healthcheck, and stores data in the `postgres_data` volume. |
| Backend | Ready to run | Builds from `backend/Dockerfile`; currently provides health checks and API scaffolding. |
| CV | Ready to run | Builds from `cv/Dockerfile`; currently provides health checks and CV scaffolding. |
| Frontend | Ready to run | Builds from `frontend/Dockerfile`; the dashboard workflow remains under development. |

Reservation, check-in, occupancy detection, authentication, and dashboard
workflows are not implemented yet.

## Repository layout

- `backend/`: FastAPI application and API/domain layers
- `cv/`: computer-vision service and detection/counting modules
- `frontend/`: React/Vite user interface
- `database/`: PostgreSQL initialization and demo seed scripts
- `tests/`: cross-service integration and end-to-end test locations
- `docs/`: requirements, architecture, decisions, and test documentation

See the component READMEs for local development details.

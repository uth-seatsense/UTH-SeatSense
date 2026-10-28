# UTH-SeatSense

UTH-SeatSense is a starter monorepo for a university seat and room occupancy
platform. It separates the computer-vision service, application API, web UI,
database, tests, and project documentation.

## Requirements

- Docker Desktop with Docker Compose
- Git


## Run locally

### Requirements

- Docker Desktop with Docker Compose
- Git

### Configure environment

1. Copy `.env.example` to `.env` in the repository root.

   On Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Open `.env` and adjust the environment variables if needed.

   - `POSTGRES_DB`: PostgreSQL database name.
   - `POSTGRES_USER`: PostgreSQL username.
   - `POSTGRES_PASSWORD`: PostgreSQL password for local development.
   - `DATABASE_URL`: Database connection URL.
   - `BACKEND_PORT`: Backend API port.
   - `CV_PORT`: Computer-vision API port.
   - `FRONTEND_PORT`: Frontend port.
   - `VITE_API_BASE_URL`: Frontend API base URL.

   The values in `.env.example` are for local development only.
   Do not commit `.env` or put real passwords, API keys, or other secrets
   in `.env.example`.

### Start services

Run the following command from the repository root:

```sh
docker compose up --build
```

Open the services:

- Frontend: <http://localhost:3000>
- Backend API docs: <http://localhost:8000/docs>
- CV API docs: <http://localhost:8001/docs>

The backend and CV services currently provide health checks and project
scaffolding only. Reservation, check-in, occupancy detection, authentication,
and dashboard workflows are not implemented yet.

## Repository layout

- `backend/`: FastAPI application and API/domain layers
- `cv/`: computer-vision service and detection/counting modules
- `frontend/`: React/Vite user interface
- `database/`: PostgreSQL initialization and demo seed scripts
- `tests/`: cross-service integration and end-to-end test locations
- `docs/`: requirements, architecture, decisions, and test documentation

See the component READMEs for local development details.

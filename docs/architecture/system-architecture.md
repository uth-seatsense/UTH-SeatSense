# System architecture

The repository is organized as a Docker Compose monorepo:

- React/Vite frontend for user workflows.
- FastAPI backend for application APIs and domain services.
- FastAPI CV service for future video analysis.
- PostgreSQL for rooms, reservations, and occupancy records.

The backend is intended to orchestrate application workflows and consume
occupancy data from the CV service. Authentication, API contracts, and service
communication are not implemented in the scaffold.

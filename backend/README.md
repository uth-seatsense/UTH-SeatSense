# Backend API

FastAPI service for rooms, reservations, check-in, and occupancy workflows.

Run locally from this directory:

```sh
python -m venv .venv
# Activate the virtual environment for your shell, then:
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API currently exposes `GET /health` and the versioned router structure.
Business endpoints and database persistence are scaffolding only.

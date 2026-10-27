# Computer vision service

This FastAPI service is the entry point for future video ingestion, object
detection, tracking, and occupancy counting work.

Run locally from this directory:

```sh
python -m venv .venv
# Activate the virtual environment for your shell, then:
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

`GET /health` reports service availability. Detection and counting modules are
scaffolds and do not process video yet. Keep model weights and test videos out of
version control.

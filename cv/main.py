from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from config.settings import settings
from app.services.jobs import Jobs


@asynccontextmanager
async def lifespan(app):
    app.state.jobs = Jobs()
    yield
    app.state.jobs.shutdown()

app = FastAPI(title=settings.service_name, version="0.3.0", lifespan=lifespan)
app.include_router(router)
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.middleware("http")
async def local_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "POST" and origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
        return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
    return await call_next(request)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")

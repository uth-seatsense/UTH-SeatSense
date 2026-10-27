from fastapi import FastAPI

from app.api.routes import router
from config.settings import settings

app = FastAPI(title=settings.service_name, version="0.1.0")
app.include_router(router)

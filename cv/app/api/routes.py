import json
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from app.counting.line_counter import LineConfig
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from app.services.webcam import WebcamSession

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "cv"}


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    confidence: float = Field(default=0.32, ge=0.1, le=1)
    camera_id: str = Field(default="camera-01", min_length=1, max_length=100)
    room_id: str | None = Field(default=None, min_length=1, max_length=100)
    line: tuple[float, float, float, float] | None = None
    in_direction: str = "negative-to-positive"
    initial_occupancy: int | None = Field(default=None, ge=0)


@router.get("/api/config")
def configuration(request: Request):
    jobs = request.app.state.jobs
    return {"model_available": jobs.model.is_file(), "device": jobs.device, "max_upload_mb": 200}


def find_job(request, identity):
    try:
        return request.app.state.jobs.snapshot(identity)
    except KeyError:
        raise HTTPException(404, "Khong tim thay phien")


@router.post("/api/jobs", status_code=202)
async def start_job(request: Request, file: UploadFile = File(...), options: str = Form("{}")):
    manager = request.app.state.jobs
    job = None
    submitted = False
    source = None
    try:
        try:
            settings = Options.model_validate_json(options)
            values = settings.model_dump(exclude={"line", "in_direction"})
            values["line_config"] = LineConfig(tuple(settings.line[:2]), tuple(settings.line[2:]), settings.in_direction) if settings.line else None
            if settings.initial_occupancy is not None and not settings.line:
                raise ValueError("So nguoi ban dau can bat duong dem")
        except ValueError:
            raise HTTPException(422, "Cau hinh khong hop le")
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
            raise HTTPException(415, "Can video MP4, AVI, MOV, MKV hoac WebM")
        try:
            job = manager.reserve(values)
        except FileNotFoundError as exc:
            raise HTTPException(503, str(exc))
        except RuntimeError as exc:
            raise HTTPException(409, str(exc))
        source = job["directory"] / ("input" + suffix)
        size = 0
        with source.open("wb") as stream:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > 200 * 1024 * 1024:
                    raise HTTPException(413, "Video vuot 200 MB")
                stream.write(chunk)
        if not size:
            raise HTTPException(400, "Video rong")
        manager.submit(job, source)
        submitted = True
        return manager.snapshot(job["id"])
    finally:
        await file.close()
        if job is not None and not submitted:
            if source:
                source.unlink(missing_ok=True)
            with manager.lock:
                job.update(status="failed", error="Tai video that bai")
            manager.slot.release()


@router.get("/api/jobs/{identity}")
def job_state(identity: str, request: Request):
    return find_job(request, identity)


@router.post("/api/jobs/{identity}/stop")
def stop_job(identity: str, request: Request):
    find_job(request, identity)
    manager = request.app.state.jobs
    job = manager.jobs[identity]
    if job.get('live'):
        with job['live'].lock:
            if job['status'] not in {'completed','failed'}:
                summary = job['live'].close()
                with manager.lock:
                    job.update(status='completed',summary=summary,output=job['directory'])
                manager.slot.release()
    else:
        job["stop"].set()
    return {"stopping": True}


@router.post('/api/webcam', status_code=202)
def start_webcam(options: Options, request: Request):
    manager = request.app.state.jobs
    try:
        values = options.model_dump(exclude={'line','in_direction'})
        values['line_config'] = LineConfig(tuple(options.line[:2]),tuple(options.line[2:]),options.in_direction) if options.line else None
        if options.initial_occupancy is not None and not options.line:
            raise ValueError('Initial occupancy requires line')
    except ValueError:
        raise HTTPException(422,'Cau hinh khong hop le')
    try:
        job = manager.reserve(values)
    except FileNotFoundError as exc:
        raise HTTPException(503,str(exc))
    except RuntimeError as exc:
        raise HTTPException(409,str(exc))
    try:
        job['live'] = WebcamSession(manager,job)
        job['status'] = 'processing'
        return manager.snapshot(job['id'])
    except Exception:
        job.update(status='failed',error='Khong tai duoc model')
        manager.slot.release()
        raise HTTPException(503,'Khong tai duoc model')


@router.post('/api/webcam/{identity}/frame')
async def webcam_frame(identity: str, request: Request):
    find_job(request,identity)
    manager = request.app.state.jobs
    job = manager.jobs[identity]
    live = job.get('live')
    if not live:
        raise HTTPException(409,'Khong phai phien webcam')
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content)>2*1024*1024:
            raise HTTPException(413,'Frame vuot 2 MB')
    def process():
        if not live.lock.acquire(blocking=False):
            raise HTTPException(409,'Frame truoc chua xu ly xong')
        try:
            if job['status'] != 'processing':
                raise HTTPException(409,'Phien da dung')
            try:
                record,events = live.process(content)
            except ValueError as exc:
                raise HTTPException(422,str(exc))
            with manager.lock:
                job.update(latest=record,frames_processed=record['frame_index']+1)
                job['events'] = (job['events']+[dict(e,timestamp_ms=record['timestamp_ms']) for e in events])[-100:]
            return record
        finally:
            live.lock.release()
    return await run_in_threadpool(process)


@router.get("/api/jobs/{identity}/preview")
def preview(identity: str, request: Request):
    find_job(request, identity)
    manager = request.app.state.jobs
    with manager.lock:
        content = manager.jobs[identity]["preview"]
    if content is None:
        raise HTTPException(404, "Chua co frame")
    return Response(content, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@router.get("/api/jobs/{identity}/files/{kind}")
def download(identity: str, kind: str, request: Request):
    state = find_job(request, identity)
    if state["status"] not in {"completed", "cancelled"}:
        raise HTTPException(409, "Chua co ket qua ket thuc")
    filenames = {"csv": "counts.csv", "jsonl": "backend_counts.jsonl", "debug": "results.jsonl", "events": "events.jsonl", "summary": "summary.json"}
    if kind not in filenames:
        raise HTTPException(404, "Khong co loai tep nay")
    path = request.app.state.jobs.jobs[identity]["output"] / filenames[kind]
    # summary on disk contains local CLI path; do not expose it through HTTP.
    if kind == "summary":
        return Response(json.dumps(state["summary"]), media_type="application/json", headers={"Content-Disposition": 'attachment; filename="summary.json"'})
    return FileResponse(path, filename=filenames[kind])

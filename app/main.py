from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import JobStatus, JobSummary
from .pipeline import run_colmap, save_json, select_frames, video_duration_seconds
from .quality import inspect_sparse_model, quality_assessment
from .telemetry import flight_path_geojson, generate_demo_track, load_csv

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "data" / "jobs"
JOBS.mkdir(parents=True, exist_ok=True)
jobs: dict[str, JobSummary] = {}

app = FastAPI(title="AerialMesh", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")


def update(job_id: str, **values: object) -> None:
    jobs[job_id] = jobs[job_id].model_copy(update=values)


def process(
    job_id: str,
    video: Path,
    telemetry: Optional[Path],
    demo_telemetry: bool = False,
    calibration: Optional[Path] = None,
) -> None:
    job_dir = JOBS / job_id
    try:
        update(job_id, status=JobStatus.processing, progress=10, message="Validating telemetry and inspecting video")
        telemetry_points = load_csv(telemetry) if telemetry else generate_demo_track(video_duration_seconds(video))
        save_json(job_dir / "flight-path.geojson", flight_path_geojson(telemetry_points))
        update(job_id, progress=30, message="Selecting sharp, overlapping frames")
        frame_data = select_frames(video, job_dir / "frames")
        warnings = []
        if demo_telemetry:
            warnings.append("Synthetic demo telemetry was used. This output is not georeferenced or suitable for measurement.")
        if not any(point.altitude is not None for point in telemetry_points):
            warnings.append("No altitude column found: output cannot be vertically georeferenced yet.")
        update(job_id, progress=70, message="Attempting sparse reconstruction", warnings=warnings)
        reconstruction = run_colmap(job_dir / "frames", job_dir / "reconstruction")
        sparse_metrics = inspect_sparse_model(Path(reconstruction["sparse_model"])) if reconstruction.get("success") else {}
        quality = quality_assessment(sparse_metrics, demo_telemetry, calibration is not None)
        warnings.extend(quality["warnings"])
        manifest = {
            "job_id": job_id,
            "telemetry_samples": len(telemetry_points),
            "telemetry_kind": "synthetic" if demo_telemetry else "supplied",
            "camera_calibration": "supplied" if calibration else "not supplied",
            **frame_data,
            "reconstruction": reconstruction,
            "quality": quality,
        }
        save_json(job_dir / "manifest.json", manifest)
        if reconstruction.get("success"):
            update(job_id, status=JobStatus.complete, progress=100, message="Sparse reconstruction complete", result=manifest)
        else:
            warnings.append(reconstruction["reason"])
            message = ("Ingestion complete; install COLMAP to produce the sparse model"
                       if not reconstruction.get("ran")
                       else "Ingestion complete; sparse reconstruction needs attention")
            update(job_id, status=JobStatus.needs_reconstruction_engine, progress=100,
                   message=message, warnings=warnings, result=manifest)
    except Exception as error:
        update(job_id, status=JobStatus.failed, progress=100, message=str(error))


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(ROOT / "web" / "index.html")


@app.post("/api/jobs", response_model=JobSummary, status_code=202)
async def create_job(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    telemetry: Optional[UploadFile] = File(None),
    calibration: Optional[UploadFile] = File(None),
    use_demo_telemetry: bool = Form(False),
) -> JobSummary:
    if Path(video.filename or "").suffix.lower() not in {".mp4", ".mov", ".avi", ".mkv"}:
        raise HTTPException(415, "Upload an MP4, MOV, AVI, or MKV video.")
    if telemetry and Path(telemetry.filename or "").suffix.lower() != ".csv":
        raise HTTPException(415, "Upload telemetry as a CSV file.")
    if not telemetry and not use_demo_telemetry:
        raise HTTPException(422, "Upload telemetry or enable synthetic demo telemetry.")
    job_id = uuid.uuid4().hex[:12]
    job_dir = JOBS / job_id
    job_dir.mkdir()
    video_path = job_dir / f"source{Path(video.filename).suffix.lower()}"
    with video_path.open("wb") as output:
        shutil.copyfileobj(video.file, output)
    telemetry_path = None
    if telemetry:
        telemetry_path = job_dir / "telemetry.csv"
        with telemetry_path.open("wb") as output:
            shutil.copyfileobj(telemetry.file, output)
    calibration_path = None
    if calibration:
        if Path(calibration.filename or "").suffix.lower() != ".json":
            raise HTTPException(415, "Upload camera calibration as JSON.")
        calibration_path = job_dir / "camera-calibration.json"
        with calibration_path.open("wb") as output:
            shutil.copyfileobj(calibration.file, output)
    summary = JobSummary(id=job_id, status=JobStatus.queued, progress=0, message="Upload received")
    jobs[job_id] = summary
    background_tasks.add_task(process, job_id, video_path, telemetry_path, use_demo_telemetry, calibration_path)
    return summary


@app.get("/api/jobs/{job_id}", response_model=JobSummary)
def get_job(job_id: str) -> JobSummary:
    if job_id not in jobs:
        raise HTTPException(404, "Job not found.")
    return jobs[job_id]


@app.get("/api/jobs/{job_id}/flight-path")
def download_flight_path(job_id: str) -> FileResponse:
    path = JOBS / job_id / "flight-path.geojson"
    if not path.exists():
        raise HTTPException(404, "Flight path is not ready.")
    return FileResponse(path, media_type="application/geo+json", filename="flight-path.geojson")

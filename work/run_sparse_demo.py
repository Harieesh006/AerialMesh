"""Build a compact, real sparse point cloud from the bundled demo video."""
from pathlib import Path
import json

from app.pipeline import run_colmap, select_frames
from app.telemetry import flight_path_geojson, generate_demo_track

root = Path(__file__).resolve().parents[1]
job = root / "data" / "jobs" / "actual-sparse-demo"
if job.exists():
    raise SystemExit(f"Refusing to overwrite existing job: {job}")
job.mkdir(parents=True)
video = Path("/Users/apple/Downloads/16621394_3840_2160_60fps.mp4")

# The compact profile is for a laptop demo, not the full-resolution production profile.
frame_data = select_frames(video, job / "frames", max_frames=45, max_dimension=1280)
duration = frame_data["source_frames"] / frame_data["fps"]
track = generate_demo_track(duration)
(job / "flight-path.geojson").write_text(json.dumps(flight_path_geojson(track), indent=2))
result = run_colmap(job / "frames", job / "reconstruction")
manifest = {
    "profile": "compact-demo",
    "telemetry": "synthetic - not georeferenced or suitable for measurement",
    "frame_selection": frame_data,
    "reconstruction": result,
}
(job / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))

"""Build a compact, real sparse point cloud from the bundled demo video."""
from pathlib import Path
import argparse
import json
import sys

root = Path(__file__).resolve().parents[1]
# Allow running as `python work/run_sparse_demo.py` from any working directory.
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.pipeline import run_colmap, select_frames
from app.telemetry import flight_path_geojson, generate_demo_track

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "video",
    nargs="?",
    type=Path,
    help="Source drone video. Defaults to data/source/demo-flight.mp4 relative to the repo root.",
)
parser.add_argument(
    "--job",
    type=Path,
    default=root / "data" / "jobs" / "actual-sparse-demo",
    help="Destination job directory (refuses to overwrite an existing one).",
)
args = parser.parse_args()

video = args.video or (root / "data" / "source" / "demo-flight.mp4")
if not video.is_file():
    raise SystemExit(
        f"Source video not found: {video}\n"
        "Pass the path explicitly, e.g. python work/run_sparse_demo.py /path/to/flight.mp4"
    )
job = args.job
if job.exists():
    raise SystemExit(f"Refusing to overwrite existing job: {job}")
job.mkdir(parents=True)

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

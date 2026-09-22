# AerialMesh

An MVP for the SIH problem statement **"Single-Pass Drone Video to Accurate 3D Model Generation System"**.

It accepts a UAV video plus flight telemetry, extracts high-quality and sufficiently separated frames, records the geographic reference, and prepares a reconstruction workspace. If [COLMAP](https://colmap.github.io/) is installed, it runs a sparse structure-from-motion reconstruction; otherwise it completes the ingestion and frame-selection stages with an explicit `needs-reconstruction-engine` result.

## What is implemented

- Browser-based upload interface and job progress polling
- Input validation for video, GeoJSON/CSV telemetry, and optional calibration/IMU files
- Video inspection and sharp-frame selection (Laplacian variance)
- Time-aligned GPS telemetry extraction and a GeoJSON flight path
- Optional camera-calibration JSON intake and illumination normalization (CLAHE)
- Reproducible job manifest and exported selected frames
- Optional COLMAP sparse reconstruction runner
- Sequential CPU matching for a single flight path, plus sparse PLY export
- Evidence-based quality gates: registered-image count, sparse-point count, reprojection error, calibration, and telemetry provenance
- Clear warnings when calibration, telemetry, coverage, or a reconstruction engine is unavailable

This is an engineering foundation, not a claim of guaranteed <=1 m absolute accuracy. Meeting that target requires calibrated camera intrinsics and accurate GPS/RTK/PPK or validated control data.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Upload an MP4/MOV/AVI and a telemetry CSV with `timestamp,latitude,longitude` columns. Optional `altitude` is used when available. For a UI-only demonstration, select **Use synthetic demo telemetry**; it produces a clearly labelled artificial flight path and must never be used as mapping or measurement output.

## Reconstruction setup

Install COLMAP and ensure `colmap` is on `PATH`. The worker uses automatic camera model selection and writes the sparse model under `data/jobs/<id>/reconstruction/`. Dense meshing is deliberately a next milestone because its GPU/CPU settings must be tuned to the deployment hardware and data quality.

## Architecture

```text
web UI -> FastAPI job API -> input validation -> frame selection -> telemetry alignment
                                                   |                    |
                                                   v                    v
                                          selected JPEG frames    GeoJSON + manifest
                                                   |
                                                   v
                                          COLMAP sparse model (optional)
```

## Project roadmap

1. Add camera calibration import and rolling-shutter compensation.
2. Add IMU/RTK fusion and local-coordinate georeferencing.
3. Run COLMAP/OpenMVS dense reconstruction and export PLY/OBJ/glTF.
4. Add QA: coverage heatmap, reprojection error, scale and GPS residual reports.
5. Benchmark against the target: under 15 minutes for a 10-minute video and <=1 m spatial error.

## Reference demo output

The tracked job `data/jobs/actual-sparse-demo/` is the committed reference result: 44 selected frames, a synthetic (clearly-labelled) flight path, and a COLMAP sparse model with its PLY export. It is versioned on purpose so a fresh clone contains the documented output without re-running anything.

To regenerate it from a video, install COLMAP on `PATH` and run:

```bash
python work/run_sparse_demo.py /path/to/flight.mp4
```

The script refuses to overwrite an existing job directory and defaults to the compact laptop profile (max 45 frames, 1280 px). Reconstruction is CPU-based, so results are equivalent but not guaranteed byte-identical across machines or COLMAP versions.

Other job directories under `data/jobs/` are machine-generated and ignored by Git.

## Input and privacy

Jobs are stored locally in `data/jobs/`; only the reference demo job is tracked by Git. Do not upload imagery you are not authorized to process.

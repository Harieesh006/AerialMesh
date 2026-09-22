# AerialMesh project handoff

## Current runnable application

The application runs from `/Users/apple/Documents/Codex/2026-09-22/sta`:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765
```

It accepts a UAV video, optional telemetry CSV, optional calibration JSON, and an explicitly labelled synthetic-telemetry demo mode.

## Implemented

- FastAPI browser UI with upload validation and polling.
- Video inspection, blur rejection, bounded sampling, and illumination normalization.
- Telemetry CSV validation and GeoJSON flight-path export.
- Clearly labelled synthetic flight path for a no-metadata demonstration.
- COLMAP CPU feature extraction, sequential matching, sparse mapping, and binary PLY export.
- Reconstruction quality checks: registered image count, sparse point count, reprojection error, calibration provenance, and telemetry provenance.
- Output package from the supplied sample video.

## Actual sample result

The compact profile sampled 44 frames at 1280 x 720. COLMAP registered 2 images and produced 32 sparse points, with a mean 0.097485-pixel reprojection error on those two views. The PLY is a genuine pipeline result, but it is **not** a complete 3D scene or measurement-grade output. The synthetic flight path is not georeferenced.

## Exact remaining work for SIH compliance

1. Parse IMU, barometric altitude, RTK/PPK, and camera calibration formats used by the target drone.
2. Inject calibrated intrinsics and GPS priors into COLMAP, then estimate an ECEF/local-ENU transform from real measurements.
3. Add dense stereo and meshing in a GPU/Linux worker, with surface coverage and mesh-quality checks.
4. Add robust dynamic-object masking and semantic layers for roads, buildings, vegetation, and obstacles.
5. Build supported format exporters from valid dense sources: OBJ, LAS, GeoTIFF, glTF/GLB, and FBX.
6. Add an interactive 3D map/viewer with measurement tools.
7. Benchmark with real ground-truth control data to demonstrate <=1 m accuracy and the 15-minute processing target.

## Important engineering constraint

No software can establish genuine spatial accuracy, reconstruct invisible surfaces, or produce authoritative georeferencing from synthetic coordinates. The code intentionally blocks those claims until real telemetry, calibration, and validation data are available.

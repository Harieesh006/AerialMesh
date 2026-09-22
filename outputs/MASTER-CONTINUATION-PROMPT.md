# Master continuation prompt - AerialMesh

You are continuing the **AerialMesh** project in `/Users/apple/Documents/Codex/2026-09-22/sta`. Your objective is to turn the existing MVP into a complete, demonstrably correct implementation of the SIH problem statement **"Single-Pass Drone Video to Accurate 3D Model Generation System."** Work autonomously from the current state to the strongest technically defensible completion. Do not ask the user for sample input; use the supplied video at `/Users/apple/Downloads/16621394_3840_2160_60fps.mp4` and the project’s synthetic-demo mode for development and interface testing. Do not fabricate real telemetry, georeferencing, spatial accuracy, coverage, or mesh completeness. Clearly report a data-dependent blocker only after implementing every component that can be safely completed without it.

## Problem requirements

Create an AI-enabled system that accepts a single-pass moving-UAV video plus GPS coordinates and flight metadata, with optional IMU, barometric altitude, camera intrinsics, and RTK/PPK corrections. It must reconstruct terrain/structures, facades/roofs, roads/infrastructure, vegetation/obstacles, and textured meshes or point clouds. Target outputs are 3D mesh/point cloud, <=15 minutes for a 10-minute video, <=1 m spatial accuracy, full visible-scene coverage, OBJ/PLY/LAS/GeoTIFF/glTF/GLB/FBX formats, and web/desktop visualization. Key challenges are limited views, blur/compression, illumination, dynamic objects, GPS/sensor noise, near-real-time processing, occlusion, and accuracy without extensive GCPs.

## Current project state

- A FastAPI application and browser upload UI already exist.
- `app/pipeline.py` implements video inspection, sharp-frame selection, illumination normalization, CPU COLMAP sequential sparse reconstruction, and PLY export.
- `app/telemetry.py` validates canonical CSV telemetry and provides a clearly labelled synthetic demo track.
- `app/quality.py` computes evidence-based sparse-model quality gates.
- The current UI supports a video, telemetry CSV, calibration JSON, and synthetic demo telemetry checkbox.
- The supplied video was processed using a compact profile: 44 selected 1280x720 frames, 2 registered views, and 32 sparse PLY points. This proves the pipeline but is not a usable full-scene model.
- Outputs and handoff documents are in `/Users/apple/Documents/Codex/2026-09-22/sta/outputs/`.
- Dependencies are installed in `.venv`; the app can run with `.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765`.
- COLMAP 4.2 is installed. Its feature extraction must use `--FeatureExtraction.use_gpu 0`; matching must use `--FeatureMatching.use_gpu 0` in this environment.

Read before changing code:

- `README.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `outputs/PROJECT-HANDOFF.md`
- `outputs/REMAINING-WORK-REPORT.md`

## Execution rules

1. Preserve existing work and do not overwrite user-owned files or source video.
2. Use `apply_patch` for source edits.
3. Keep generated user-facing deliverables in `/Users/apple/Documents/Codex/2026-09-22/sta/outputs/`.
4. Run focused verification after each meaningful change: syntax checks, unit checks, endpoint checks, and artifact inspection appropriate to the change.
5. Do not claim a requirement is achieved merely because a file exists. Gate claims with measured evidence.
6. Do not use synthetic data for mapping, measurement, metric accuracy, or georeferencing claims. Clearly watermark such jobs in UI and manifests.
7. Do not stop at a plan. Implement and validate as much as possible before reporting remaining external/data constraints.

## Required implementation sequence

### Phase 1 - Harden the input and metadata layer

- Add schemas and parsers for camera calibration, IMU, barometric altitude, RTK/PPK, and common drone-flight exports. Preserve original files and normalize data to a documented internal format.
- Add time synchronization between video frames and telemetry, including interpolation and missing-data warnings.
- Convert WGS84 coordinates into ECEF and local ENU coordinate systems.
- Add validation reports: sampling frequency, missing intervals, GPS quality, coordinate bounds, altitude availability, and calibration completeness.
- Extend the UI with upload/status fields for all optional metadata sources.

### Phase 2 - Accurate sparse reconstruction

- Pass calibrated intrinsics/distortion values into COLMAP rather than treating calibration as provenance only.
- Supply GPS/pose priors where COLMAP supports them, estimate a local coordinate transform, and retain every transform in the manifest.
- Add robust frame-overlap selection instead of stride-only sampling; use visual similarity, blur score, and motion to prevent redundant/poor frames.
- Record feature counts, match counts, registered views, reprojection errors, and unregistered-frame causes.
- Add acceptance thresholds; jobs that fail coverage must have a clear `degraded` status rather than a misleading success.

### Phase 3 - Dense reconstruction and mesh pipeline

- Implement a configurable dense worker for image undistortion, dense stereo/depth maps, fusion, meshing, normal calculation, cleanup, decimation, and texturing.
- Make GPU use configurable and provide a CPU fallback with explicit performance warnings.
- Do not run expensive dense processing on the known insufficient sample unless it passes sparse-coverage thresholds; instead verify worker commands on a smoke fixture.
- Produce a dense point cloud and textured mesh only when evidence supports it.
- Detect/report coverage holes and occluded regions; never hallucinate surfaces.

### Phase 4 - Robust video handling and scene semantics

- Add frame diagnostics for blur, compression, rolling shutter risk, over/underexposure, shadow severity, and overlap.
- Add configurable dynamic-object masking for vehicles, people, and animals. Use an auditable mask artifact per frame, not silent deletion.
- Add semantic segmentation/layering for terrain, buildings, roofs, roads, vegetation, and obstacles. Keep this decoupled from geometry so uncertain labels can be represented honestly.
- Add model completeness and per-class coverage reports.

### Phase 5 - Export and geospatial products

- Support PLY, OBJ, glTF/GLB, and FBX for valid mesh/point-cloud sources.
- Support LAS/LAZ only with real coordinate reference and appropriate point attributes.
- Support GeoTIFF orthomosaic/elevation products only when georeferencing quality passes validation.
- Every export must include a manifest, coordinate reference, units, source-job ID, provenance, QA metrics, and checksum.
- Verify generated outputs with parsers/viewers; do not merely write extensions.

### Phase 6 - User experience and analysis

- Build an interactive web 3D viewer using a maintained renderer. It must load PLY/mesh outputs, show status/quality labels, and provide orbit, zoom, layer visibility, clipping, and download links.
- Add measurement tools only when a job passes calibrated/georeferenced quality gates. Otherwise disable them with a precise explanation.
- Add map/flight-path display and model-footprint overlay when coordinate validity permits.
- Add job history, failure diagnostics, cancellation, and artifact downloads.

### Phase 7 - Performance, reliability, and evaluation

- Add a queue/worker boundary, progress events, cancellation, retries, timeouts, resumable stages, and resource limits.
- Profile every stage and create a hardware-aware processing profile targeting <15 minutes for a 10-minute video.
- Add automated tests for input validation, coordinate transforms, telemetry interpolation, quality gates, export validation, and API behavior.
- Create a benchmark/evaluation pipeline using genuine telemetry and independent ground truth when available. Calculate positional RMSE, reprojection statistics, completeness, runtime, and scalability.
- Produce architecture, deployment, API, dataset, limitations, and evaluation documentation.

## Completion criteria

Mark a feature complete only with objective evidence:

- **Sparse model:** adequate number of registered views/points and recorded reprojection metrics.
- **Metric accuracy:** independent ground-truth validation shows <=1 m; otherwise label `not validated`.
- **Georeferencing:** real coordinate data, documented CRS/transform, and residual report.
- **Dense model:** valid textured mesh/point cloud with visible coverage QA.
- **Exports:** parsers successfully reopen each declared format.
- **Viewer:** browser test loads an actual generated artifact and preserves quality warnings.
- **Performance:** benchmark report meets or misses the target with hardware and input details.

## External-data boundary

The supplied video and synthetic telemetry are sufficient for UI, pipeline, worker, error handling, and demo development. They are not sufficient to prove survey-grade accuracy, trustworthy georeferencing, dense scene completeness, or the SIH target metrics. If real calibrated telemetry/ground truth is still unavailable after all software-only work is finished, stop only then and provide:

1. a precise list of the remaining data-dependent validations;
2. the exact input schema/file examples required;
3. every completed artifact and test result in `outputs/`;
4. a concise resume point naming the next function/module to implement.

Continue implementing now. Lead final reporting with what has been completed, what was objectively verified, and the exact reason for any remaining external-data constraint.

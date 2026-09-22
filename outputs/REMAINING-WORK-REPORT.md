# AerialMesh remaining-work report

## Current estimated progress: 30%

The current work is a functioning proof-of-concept pipeline. It demonstrates video ingestion, preprocessing, telemetry workflow, sparse reconstruction, a web interface, and an exported point cloud. It does not yet satisfy the full SIH outcome because the generated model is sparse, synthetic-positioned, and not validated for measurement.

## Completed foundation

| Area | Status | Evidence |
| --- | --- | --- |
| Video ingestion | Complete | MP4/MOV/AVI/MKV validation and frame inspection |
| Frame quality | Complete | Blur rejection, bounded sampling, illumination normalization |
| Telemetry workflow | Partial | CSV + GeoJSON supported; synthetic demo mode available |
| Sparse reconstruction | Complete MVP | COLMAP sequential CPU pipeline and PLY export |
| Quality reporting | Complete MVP | Registered views, point count, reprojection error, provenance gates |
| Web interface | Complete MVP | Local upload form, progress polling, download endpoint |

## Remaining implementation work

### 1. Accurate data fusion and georeferencing - highest priority

- Parse actual drone GPS, IMU, barometric-altitude, and RTK/PPK logs.
- Parse calibrated camera intrinsics and distortion coefficients.
- Associate every selected image with interpolated flight time and pose priors.
- Convert WGS84 positions to a local ENU coordinate frame.
- Align the reconstructed model to telemetry and quantify GPS residual error.
- Reject or flag output when accuracy cannot be verified.

**Completion evidence:** an independently measured check-point report showing <=1 m error.

### 2. Dense reconstruction and textured mesh

- Add a GPU worker for image undistortion, dense stereo, depth fusion, and mesh generation.
- Generate texture atlases and textured mesh output.
- Detect holes/occlusions and report unobserved surfaces rather than inventing geometry.
- Implement mesh cleanup, decimation, normal generation, and texture QA.

**Completion evidence:** a textured mesh of buildings, roofs, roads, terrain, and visible obstacles with a coverage report.

### 3. Scene understanding and difficult-video handling

- Add dynamic-object masks for people, vehicles, and animals.
- Add exposure/shadow consistency checks and robust frame exclusion.
- Add rolling-shutter and motion-blur confidence scoring.
- Add semantic segmentation for road, structure, vegetation, terrain, and obstacle layers.

**Completion evidence:** semantic layers and a per-frame exclusion/masking audit.

### 4. Required output products

- Mesh: OBJ, glTF/GLB, FBX.
- Point cloud: PLY and LAS/LAZ.
- Orthomosaic/elevation: GeoTIFF, only after validated georeferencing.
- Project manifest, accuracy report, QA report, preview imagery, and checksums.

**Completion evidence:** each exported format opens correctly and preserves its coordinate reference and metadata.

### 5. Viewer and analysis tools

- Add interactive 3D point-cloud/mesh viewer.
- Add orbit, layer toggle, clipping, point/mesh selection, distance, area, and elevation measurements.
- Add a map panel showing the flight route and model footprint.
- Clearly watermark demo/synthetic jobs and block measurement tools when the quality gate fails.

**Completion evidence:** browser-based view of a valid exported model with validated measurement tools.

### 6. Performance and deployment

- Add job queue, GPU worker, cancellation, retries, resumable artifacts, and storage lifecycle.
- Profile frame selection, feature extraction, matching, dense stereo, and export stages.
- Tune the production profile to the target: <15 minutes for a 10-minute input video.
- Create reproducible Docker/Linux deployment instructions and benchmark hardware matrix.

**Completion evidence:** benchmark report against the target video duration and hardware.

### 7. Evaluation and demonstration package

- Collect legal, representative drone datasets with telemetry and ground truth.
- Define holdout scenes and accuracy evaluation protocol.
- Compare reconstruction coverage, accuracy, runtime, and usability against baseline tools.
- Prepare architecture diagram, workflow video, screenshots, limitations, and final presentation.

**Completion evidence:** reproducible evaluation results for the competition jury.

## Recommended build order

1. Calibration + real GPS/IMU/RTK ingestion.
2. GPS-aligned sparse reconstruction and accuracy report.
3. GPU dense mesh + PLY/OBJ/glTF outputs.
4. Viewer + measurements + quality-gated UX.
5. Segmentation/dynamic masks + GeoTIFF/LAS.
6. Performance tuning, benchmark, and competition presentation.

## Critical constraint

The supplied video is useful for proving the pipeline, but it cannot establish true spatial accuracy or fully reconstruct the scene from its limited overlap. No remaining software task should claim those properties without calibrated imagery, genuine telemetry, and independent validation data.

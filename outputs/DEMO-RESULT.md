# AerialMesh compact demo result

Source video: `16621394_3840_2160_60fps.mp4`

## Completed output

- A real COLMAP sparse point cloud exported as `aerialmesh-demo-sparse-point-cloud.ply`.
- A synthetic 17-sample flight path exported as `aerialmesh-demo-synthetic-flight-path.geojson`.
- The reproducibility details are in `aerialmesh-demo-manifest.json`.

## Quality report

The compact demo sampled 44 sharp frames at 1280 x 720 and ran CPU sequential structure-from-motion. COLMAP registered 2 images, triangulated 32 points, and reported a 0.097485-pixel mean reprojection error for those registered observations.

This is a successful end-to-end technical demonstration, but not a usable terrain/building model: the supplied clip does not provide enough reconstructable multi-view coverage for a dense scene. The flight path is synthetic and must not be used for mapping, measurement, or georeferencing.

## Production requirements

For a complete accurate model, the production pipeline needs a steady overlapping flyover, real telemetry, camera calibration, and ideally RTK/PPK. The app already supports those inputs and uses the same COLMAP handoff, but only real telemetry can establish a trustworthy coordinate system.

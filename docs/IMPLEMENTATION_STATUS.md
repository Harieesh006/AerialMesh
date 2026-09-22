# SIH requirement traceability

| Requirement | Implementation status |
| --- | --- |
| Single-pass video processing | Implemented: bounded sharp-frame sampling and sequential matching. |
| GPS and flight metadata | Implemented: CSV validation and GeoJSON flight-path output. |
| IMU, barometer, RTK/PPK | Input architecture pending; no trustworthy substitute is fabricated. |
| Camera calibration | Optional JSON intake; used as provenance and quality evidence. Camera-parameter injection is the next integration step. |
| 3D point cloud | Implemented: COLMAP sparse PLY export. |
| Textured dense mesh | Requires a dense reconstruction worker and sufficiently overlapping/calibrated imagery. Not claimed complete. |
| Terrain, structures, roofs, roads, vegetation, obstacles | Depend on dense coverage plus semantic segmentation; not inferable reliably from the supplied clip. |
| Georeferencing and <=1 m accuracy | Quality-gated. Needs genuine position/calibration data and ground-truth validation. |
| OBJ, LAS, GeoTIFF, glTF/GLB, FBX | PLY is implemented. Remaining conversions need a valid dense/georeferenced source model. |
| Web/Desktop visualisation | Browser upload/progress interface is implemented; interactive 3D viewer is pending. |
| <15 minute performance | Profiling infrastructure and target profile are pending hardware benchmark data. |

The application reports these limitations at runtime to prevent a sparse or synthetic demo from being mistaken for a complete survey-grade model.

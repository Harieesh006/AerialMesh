"""Evidence-based reconstruction quality checks.

These checks intentionally gate claims such as coverage and metric accuracy instead of
inferring them from the existence of an exported PLY file.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


def inspect_sparse_model(model_path: Path) -> dict:
    executable = shutil.which("colmap")
    if not executable or not model_path.exists():
        return {"available": False}
    completed = subprocess.run(
        [executable, "model_analyzer", "--path", str(model_path)],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if completed.returncode:
        return {"available": False, "error": completed.stderr[-500:]}
    metrics = {}
    labels = {
        "Registered images": "registered_images",
        "Points": "points",
        "Mean reprojection error": "mean_reprojection_error_px",
    }
    for label, key in labels.items():
        match = re.search(rf"{re.escape(label)}:\s+([0-9.]+)", completed.stderr)
        if match:
            value = float(match.group(1))
            metrics[key] = int(value) if key != "mean_reprojection_error_px" else value
    metrics["available"] = bool(metrics)
    return metrics


def quality_assessment(sparse_metrics: dict, telemetry_is_synthetic: bool, has_calibration: bool) -> dict:
    warnings: list[str] = []
    registered = sparse_metrics.get("registered_images", 0)
    points = sparse_metrics.get("points", 0)
    if registered < 8:
        warnings.append("Fewer than 8 images registered: scene coverage is insufficient for a usable model.")
    if points < 1000:
        warnings.append("Sparse point count is low: do not treat this as a complete terrain or structure model.")
    if telemetry_is_synthetic:
        warnings.append("Synthetic telemetry prevents georeferencing and metric-accuracy claims.")
    if not has_calibration:
        warnings.append("No camera calibration: scale and lens-distortion accuracy are unverified.")
    return {
        "sparse_metrics": sparse_metrics,
        "quality_gate_passed": not warnings,
        "warnings": warnings,
        "metric_accuracy_claim": "not validated" if warnings else "requires independent ground-truth validation",
    }

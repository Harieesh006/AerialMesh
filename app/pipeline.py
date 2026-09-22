from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import cv2


def select_frames(
    video: Path,
    output_dir: Path,
    max_frames: int = 350,
    max_dimension: Optional[int] = None,
    enhance_illumination: bool = True,
) -> dict:
    """Sample a bounded number of sharp frames, retaining enough overlap for SfM."""
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError("Could not open the video. Use MP4, MOV, or AVI encoded with a supported codec.")
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total < 2:
        raise ValueError("The video contains fewer than two readable frames.")
    # A bounded sample keeps the first-pass reconstruction practical on a laptop.
    # Ceiling division guarantees the selected candidate count cannot exceed max_frames.
    stride = max(1, math.ceil(total / max_frames))
    output_dir.mkdir(parents=True, exist_ok=True)
    selected, sharpness, output_size = 0, [], None
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % stride == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            # 45 is conservative: retain usable footage while excluding obvious blur.
            if score >= 45:
                if enhance_illumination:
                    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                    luminance, channel_a, channel_b = cv2.split(lab)
                    luminance = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(luminance)
                    frame = cv2.cvtColor(cv2.merge((luminance, channel_a, channel_b)), cv2.COLOR_LAB2BGR)
                if max_dimension and max(frame.shape[:2]) > max_dimension:
                    scale = max_dimension / max(frame.shape[:2])
                    frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                name = f"frame_{index:07d}.jpg"
                cv2.imwrite(str(output_dir / name), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
                selected += 1
                sharpness.append(score)
                output_size = [int(frame.shape[1]), int(frame.shape[0])]
        index += 1
    capture.release()
    if selected < 8:
        raise ValueError("Too few sharp frames were found. Capture a slower, steadier pass with more scene overlap.")
    return {
        "source_frames": total,
        "selected_frames": selected,
        "fps": round(fps, 3),
        "sample_stride": stride,
        "mean_sharpness": round(sum(sharpness) / len(sharpness), 2),
        "output_dimensions": output_size,
        "illumination_normalization": enhance_illumination,
    }


def video_duration_seconds(video: Path) -> float:
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError("Could not open the video to determine its duration.")
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    capture.release()
    return total / fps


def run_colmap(images: Path, workspace: Path) -> dict:
    """Run sparse SfM only when COLMAP is available locally."""
    executable = shutil.which("colmap")
    if not executable:
        return {"ran": False, "reason": "COLMAP is not installed or not on PATH."}
    database = workspace / "database.db"
    sparse = workspace / "sparse"
    sparse.mkdir(parents=True, exist_ok=True)
    commands = [
        [
            executable, "feature_extractor", "--database_path", str(database), "--image_path", str(images),
            "--FeatureExtraction.use_gpu", "0",
        ],
        # Sequential matching suits a single drone pass and avoids the quadratic cost of all-pairs matching.
        [executable, "sequential_matcher", "--database_path", str(database), "--FeatureMatching.use_gpu", "0"],
        [executable, "mapper", "--database_path", str(database), "--image_path", str(images), "--output_path", str(sparse)],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=900,
            env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        )
        if completed.returncode:
            return {"ran": True, "success": False, "reason": completed.stderr[-1000:]}
    model = sparse / "0"
    point_cloud = workspace / "sparse-point-cloud.ply"
    converted = subprocess.run(
        [executable, "model_converter", "--input_path", str(model), "--output_path", str(point_cloud), "--output_type", "PLY"],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    if converted.returncode:
        return {"ran": True, "success": False, "reason": converted.stderr[-1000:]}
    return {"ran": True, "success": True, "sparse_model": str(model), "point_cloud": str(point_cloud)}


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

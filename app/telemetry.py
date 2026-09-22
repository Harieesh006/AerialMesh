from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TelemetryPoint:
    timestamp: float
    latitude: float
    longitude: float
    altitude: float | None = None


def load_csv(path: Path) -> list[TelemetryPoint]:
    """Load canonical UAV telemetry CSV: timestamp, latitude, longitude, altitude?"""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    required = {"timestamp", "latitude", "longitude"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Telemetry CSV needs timestamp, latitude, and longitude columns.")

    points: list[TelemetryPoint] = []
    for number, row in enumerate(rows, start=2):
        try:
            point = TelemetryPoint(
                timestamp=float(row["timestamp"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                altitude=float(row["altitude"]) if row.get("altitude") else None,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid telemetry values on row {number}.") from error
        if not -90 <= point.latitude <= 90 or not -180 <= point.longitude <= 180:
            raise ValueError(f"Latitude/longitude out of range on row {number}.")
        points.append(point)
    return sorted(points, key=lambda point: point.timestamp)


def flight_path_geojson(points: list[TelemetryPoint]) -> dict:
    coordinates = [
        [p.longitude, p.latitude, p.altitude] if p.altitude is not None else [p.longitude, p.latitude]
        for p in points
    ]
    return {"type": "FeatureCollection", "features": [{
        "type": "Feature",
        "properties": {"samples": len(points)},
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }]}


def generate_demo_track(duration_seconds: float, interval_seconds: float = 1.0) -> list[TelemetryPoint]:
    """Create a clearly synthetic short flight path for product demonstrations only."""
    samples = max(2, math.ceil(duration_seconds / interval_seconds) + 1)
    origin_latitude, origin_longitude = 12.9716, 77.5946
    points: list[TelemetryPoint] = []
    for index in range(samples):
        progress = index / (samples - 1)
        # Roughly a 170 m eastbound pass with a gentle lateral arc and altitude change.
        points.append(TelemetryPoint(
            timestamp=round(progress * duration_seconds, 3),
            latitude=origin_latitude + 0.00012 * math.sin(progress * math.pi),
            longitude=origin_longitude + 0.00155 * progress,
            altitude=92.0 + 7.0 * math.sin(progress * math.pi),
        ))
    return points

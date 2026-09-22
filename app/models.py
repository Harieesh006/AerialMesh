from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    needs_reconstruction_engine = "needs-reconstruction-engine"
    complete = "complete"
    failed = "failed"


class JobSummary(BaseModel):
    id: str
    status: JobStatus
    progress: int
    message: str
    warnings: list[str] = []
    result: Optional[dict[str, Any]] = None


from pydantic import BaseModel
from typing import List, Optional, Literal, Dict

SizeBucket = Literal["small","medium","large"]
Protection = Literal["none","password","confidential","highly_confidential"]

class Config(BaseModel):
    scenario_id: str
    source_apps: List[str]
    file_size_bucket: SizeBucket
    protection_level: Protection
    file_type: Literal["xlsx","xls","csv","other"] = "xlsx"
    notes: Optional[str] = None

class FrameMeta(BaseModel):
    index: int
    ts_ms: int
    path: str

class Bug(BaseModel):
    id: str
    title: str
    description: str
    severity: Literal["low","medium","high","critical"]
    category: Literal["functional","perf","ux","accessibility","security","compat"]
    evidence_frames: List[int]
    suggestions: Optional[str] = None

class Step(BaseModel):
    step_no: int
    summary: str
    frames: List[int]

class LlmOutput(BaseModel):
    # We accept either unified bugs[] or split bugs_strong/bugs_minor and normalize later
    bugs: Optional[List[Bug]] = None
    bugs_strong: Optional[List[Bug]] = None
    bugs_minor: Optional[List[Bug]] = None
    steps: List[Step] = []
    assumptions: Optional[str] = None
    metadata: Dict[str, str] = {}

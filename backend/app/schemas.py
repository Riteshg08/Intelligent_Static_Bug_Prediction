from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RiskCounts(BaseModel):
    high: int
    medium: int
    low: int

class ProjectResponse(BaseModel):
    id: int
    name: str
    languages: List[str]
    risk_counts: RiskCounts
    function_count: int
    last_updated: Optional[str] = None
    latest_run_id: Optional[int] = None

class FileData(BaseModel):
    id: int
    path: str
    language: str
    line_count: int
    status: str
    risk_level: str

class ProjectFilesResponse(BaseModel):
    run_id: Optional[int] = None
    run_status: Optional[str] = None
    files: List[FileData]

class SourceResponse(BaseModel):
    source: str

class AnalysisRunResponse(BaseModel):
    run_id: int
    status: str

class StatusResponse(BaseModel):
    status: str

class PredictionResponse(BaseModel):
    id: int
    function_name: str
    language: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    risk_score: float
    risk_level: str
    file_id: int
    file_path: str

class AnalysisFileResponse(BaseModel):
    id: int
    path: str
    language: str
    max_risk_score: float
    risk_counts: RiskCounts

class FunctionAnnotation(BaseModel):
    id: int
    name: str
    start_line: int
    end_line: int
    risk_score: float
    risk_level: str

class Hotspot(BaseModel):
    id: Optional[int] = None
    start_line: int
    end_line: int
    severity: str
    rule_id: str
    message: str

class AnnotationsResponse(BaseModel):
    functions: List[FunctionAnnotation]
    hotspots: List[Hotspot]

class PredictionReportResponse(BaseModel):
    id: int
    function_name: str
    language: str
    risk_score: float
    risk_level: str
    confidence_note: Optional[str] = None
    explanation: Dict[str, Any]
    hotspots: List[Hotspot]
    file_id: int

class ModelCurrentResponse(BaseModel):
    version: str

class LanguagesResponse(BaseModel):
    languages: List[str]

class ProjectCreateResponse(BaseModel):
    id: int
    name: str

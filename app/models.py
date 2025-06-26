from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any


class RepoStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"


class RepoRequest(BaseModel):
    url: str
    branch: str = "main"


class RepoResponse(BaseModel):
    repo_id: str
    status: RepoStatus


class StatusResponse(BaseModel):
    status: RepoStatus
    message: Optional[str] = None


class QueryRequest(BaseModel):
    repo_id: str
    question: str


class QueryResponse(BaseModel):
    answer: str
    repo_id: str


class GraphResponse(BaseModel):
    nodes: list
    edges: list
    metadata: Dict[str, Any]

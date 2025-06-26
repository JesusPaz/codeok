from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class RepoStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    ERROR = "ERROR"


class PullRequestStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


# Database Models
class GitHubProfile(BaseModel):
    id: Optional[int] = None
    github_id: int
    username: str
    avatar_url: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Repository(BaseModel):
    id: Optional[int] = None
    github_id: int
    name: str
    full_name: str
    url: str
    branch: str = "main"
    status: RepoStatus = RepoStatus.PENDING
    owner_id: int  # Foreign key to GitHubProfile
    description: Optional[str] = None
    is_private: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PullRequest(BaseModel):
    id: Optional[int] = None
    github_id: int
    number: int
    title: str
    body: Optional[str] = None
    status: PullRequestStatus
    repository_id: int  # Foreign key to Repository
    author_id: int  # Foreign key to GitHubProfile
    base_branch: str
    head_branch: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    processed: bool = False


# API Request/Response Models
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


# Extended Response Models with Database Data
class RepositoryResponse(BaseModel):
    id: int
    name: str
    full_name: str
    url: str
    branch: str
    status: RepoStatus
    owner: GitHubProfile
    description: Optional[str] = None
    is_private: bool = False
    pull_requests_count: int = 0
    created_at: datetime
    updated_at: datetime


class PullRequestResponse(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    status: PullRequestStatus
    repository: Repository
    author: GitHubProfile
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime


class RepositoryListResponse(BaseModel):
    repositories: List[RepositoryResponse]
    total: int
    page: int
    per_page: int


class PullRequestListResponse(BaseModel):
    pull_requests: List[PullRequestResponse]
    total: int
    page: int
    per_page: int

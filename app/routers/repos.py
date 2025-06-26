from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import uuid
import json
import asyncio
from typing import Dict, Optional
from ..models import (
    RepoRequest, RepoResponse, StatusResponse, QueryRequest, 
    GraphResponse, RepoStatus
)

router = APIRouter(prefix="/repos", tags=["repositories"])

# In-memory storage (in production, use a database)
repos_db: Dict[str, Dict] = {}


@router.post("/", response_model=RepoResponse)
async def register_repository(repo: RepoRequest):
    """
    Registrar un repositorio (URL git + branch). 
    Devuelve repo_id y estado inicial PENDING.
    """
    repo_id = str(uuid.uuid4())
    
    # Store repository information
    repos_db[repo_id] = {
        "url": repo.url,
        "branch": repo.branch,
        "status": RepoStatus.PENDING,
        "created_at": None,  # Add timestamp in production
        "message": None
    }
    
    # Simulate async processing (in production, queue this task)
    asyncio.create_task(process_repository(repo_id))
    
    return RepoResponse(repo_id=repo_id, status=RepoStatus.PENDING)


@router.get("/{repo_id}/status", response_model=StatusResponse)
async def get_repository_status(repo_id: str):
    """
    Consultar el estado del proceso de ingesta 
    (QUEUED / PROCESSING / READY / ERROR).
    """
    if repo_id not in repos_db:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo_data = repos_db[repo_id]
    return StatusResponse(
        status=repo_data["status"],
        message=repo_data.get("message")
    )


@router.get("/{repo_id}/graph")
async def get_repository_graph(
    repo_id: str, 
    depth: Optional[int] = None, 
    node_id: Optional[str] = None
):
    """
    (Opcional / debug) Obtener un sub-grafo en JSON; 
    acepta filtros depth y node_id.
    """
    if repo_id not in repos_db:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo_data = repos_db[repo_id]
    if repo_data["status"] != RepoStatus.READY:
        raise HTTPException(
            status_code=400, 
            detail=f"Repository not ready. Current status: {repo_data['status']}"
        )
    
    # Mock graph data (in production, retrieve from graph database)
    mock_graph = {
        "nodes": [
            {"id": "node1", "type": "file", "name": "main.py"},
            {"id": "node2", "type": "function", "name": "process_data"},
            {"id": "node3", "type": "class", "name": "DataProcessor"}
        ],
        "edges": [
            {"source": "node1", "target": "node2", "relationship": "contains"},
            {"source": "node1", "target": "node3", "relationship": "contains"}
        ],
        "metadata": {
            "total_nodes": 3,
            "total_edges": 2,
            "depth_filter": depth,
            "node_filter": node_id
        }
    }
    
    # Apply filters if provided
    if node_id:
        mock_graph["nodes"] = [n for n in mock_graph["nodes"] if n["id"] == node_id]
    
    return GraphResponse(**mock_graph)


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str):
    """
    Borrar repo, embeddings y grafo asociados.
    """
    if repo_id not in repos_db:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Delete from storage (in production, also delete embeddings and graph data)
    del repos_db[repo_id]
    
    return {"message": f"Repository {repo_id} deleted successfully"}


async def process_repository(repo_id: str):
    """
    Simulate repository processing workflow
    """
    try:
        # Update status to QUEUED
        repos_db[repo_id]["status"] = RepoStatus.QUEUED
        await asyncio.sleep(1)
        
        # Update status to PROCESSING
        repos_db[repo_id]["status"] = RepoStatus.PROCESSING
        await asyncio.sleep(3)  # Simulate processing time
        
        # Update status to READY
        repos_db[repo_id]["status"] = RepoStatus.READY
        repos_db[repo_id]["message"] = "Repository processed successfully"
        
    except Exception as e:
        repos_db[repo_id]["status"] = RepoStatus.ERROR
        repos_db[repo_id]["message"] = f"Processing failed: {str(e)}"

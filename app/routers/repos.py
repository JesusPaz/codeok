from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import uuid
import json
import asyncio
from typing import Dict, Optional
from ..models import (
    RepoRequest, RepoResponse, StatusResponse, QueryRequest, 
    GraphResponse, RepoStatus, RepositoryResponse, RepositoryListResponse
)
from ..crud import repository_crud, github_profile_crud
import re
import logging

router = APIRouter(prefix="/repos", tags=["repositories"])
logger = logging.getLogger(__name__)

# Backward compatibility: In-memory storage for query router
# This mirrors the database state for repos that have been processed
repos_db: Dict[str, Dict] = {}

def extract_github_info(url: str) -> Dict[str, str]:
    """Extract owner and repo name from GitHub URL"""
    # Match GitHub URLs like https://github.com/owner/repo or https://github.com/owner/repo.git
    pattern = r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$'
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError("Invalid GitHub URL format")
    
    owner, repo = match.groups()
    return {
        "owner": owner,
        "repo": repo,
        "full_name": f"{owner}/{repo}"
    }


@router.post("/", response_model=RepoResponse)
async def register_repository(repo: RepoRequest):
    """
    Registrar un repositorio (URL git + branch). 
    Devuelve repo_id y estado inicial PENDING.
    """
    try:
        # Extract GitHub info from URL
        github_info = extract_github_info(repo.url)
        
        # Create or get GitHub profile (mock data for now)
        # In a real implementation, you'd fetch this from GitHub API
        profile_data = {
            "github_id": 12345,  # Mock GitHub ID
            "username": github_info["owner"],
            "avatar_url": f"https://github.com/{github_info['owner']}.png",
            "name": github_info["owner"]
        }
        
        profile = await github_profile_crud.create_or_update(profile_data)
        
        # Check if repository already exists
        existing_repo = await repository_crud.get_by_github_id(67890)  # Mock GitHub repo ID
        if existing_repo:
            return RepoResponse(repo_id=str(existing_repo.id), status=existing_repo.status)
        
        # Create new repository
        repo_data = {
            "github_id": 67890,  # Mock GitHub repo ID
            "name": github_info["repo"],
            "full_name": github_info["full_name"],
            "url": repo.url,
            "branch": repo.branch,
            "owner_id": profile.id,
            "description": f"Repository {github_info['full_name']}",
            "is_private": False
        }
        
        new_repo = await repository_crud.create(repo_data)
        
        # Add to in-memory storage for backward compatibility
        repos_db[str(new_repo.id)] = {
            "url": repo.url,
            "branch": repo.branch,
            "status": RepoStatus.PENDING,
            "created_at": new_repo.created_at,
            "message": None
        }
        
        # Start async processing
        asyncio.create_task(process_repository(new_repo.id))
        
        return RepoResponse(repo_id=str(new_repo.id), status=RepoStatus.PENDING)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering repository: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{repo_id}/status", response_model=StatusResponse)
async def get_repository_status(repo_id: str):
    """
    Consultar el estado del proceso de ingesta 
    (QUEUED / PROCESSING / READY / ERROR).
    """
    try:
        repo_id_int = int(repo_id)
        repo = await repository_crud.get_by_id(repo_id_int)
        
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        return StatusResponse(
            status=repo.status,
            message=repo.error_message
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")
    except Exception as e:
        logger.error(f"Error getting repository status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{repo_id}/graph")
async def get_repository_graph(
    repo_id: str, 
    depth: Optional[int] = Query(None, description="Graph depth filter"), 
    node_id: Optional[str] = Query(None, description="Specific node ID filter")
):
    """
    (Opcional / debug) Obtener un sub-grafo en JSON; 
    acepta filtros depth y node_id.
    """
    try:
        repo_id_int = int(repo_id)
        repo = await repository_crud.get_by_id(repo_id_int)
        
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        if repo.status != RepoStatus.READY:
            raise HTTPException(
                status_code=400, 
                detail=f"Repository not ready. Current status: {repo.status}"
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
                "node_filter": node_id,
                "repository_id": repo_id_int
            }
        }
        
        # Apply filters if provided
        if node_id:
            mock_graph["nodes"] = [n for n in mock_graph["nodes"] if n["id"] == node_id]
        
        return GraphResponse(**mock_graph)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")
    except Exception as e:
        logger.error(f"Error getting repository graph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=RepositoryListResponse)
async def list_repositories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID")
):
    """
    List repositories with pagination and optional filtering
    """
    try:
        if owner_id:
            repositories = await repository_crud.list_by_owner(owner_id, page, per_page)
        else:
            # For now, return empty list if no owner_id specified
            # In production, you might want to list all repositories with proper permissions
            repositories = []
        
        # Convert to response format (simplified for now)
        repo_responses = []
        for repo in repositories:
            # Get owner profile
            profile = await github_profile_crud.get_by_github_id(repo.owner_id)
            
            repo_response = RepositoryResponse(
                id=repo.id,
                name=repo.name,
                full_name=repo.full_name,
                url=repo.url,
                branch=repo.branch,
                status=repo.status,
                owner=profile,
                description=repo.description,
                is_private=repo.is_private,
                pull_requests_count=0,  # TODO: Count PRs
                created_at=repo.created_at,
                updated_at=repo.updated_at
            )
            repo_responses.append(repo_response)
        
        return RepositoryListResponse(
            repositories=repo_responses,
            total=len(repo_responses),
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error listing repositories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str):
    """
    Borrar repo, embeddings y grafo asociados.
    """
    try:
        repo_id_int = int(repo_id)
        repo = await repository_crud.get_by_id(repo_id_int)
        
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Delete repository (cascade will handle related data)
        await repository_crud.delete(repo_id_int)
        
        return {"message": f"Repository {repo_id} deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository ID")
    except Exception as e:
        logger.error(f"Error deleting repository: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_repository(repo_id: int):
    """
    Simulate repository processing workflow using database
    """
    repo_id_str = str(repo_id)
    try:
        # Update status to QUEUED
        await repository_crud.update_status(repo_id, RepoStatus.QUEUED)
        if repo_id_str in repos_db:
            repos_db[repo_id_str]["status"] = RepoStatus.QUEUED
        await asyncio.sleep(1)
        
        # Update status to PROCESSING
        await repository_crud.update_status(repo_id, RepoStatus.PROCESSING)
        if repo_id_str in repos_db:
            repos_db[repo_id_str]["status"] = RepoStatus.PROCESSING
        await asyncio.sleep(3)  # Simulate processing time
        
        # Update status to READY
        await repository_crud.update_status(
            repo_id, 
            RepoStatus.READY, 
            "Repository processed successfully"
        )
        if repo_id_str in repos_db:
            repos_db[repo_id_str]["status"] = RepoStatus.READY
            repos_db[repo_id_str]["message"] = "Repository processed successfully"
        
        logger.info(f"Repository {repo_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing repository {repo_id}: {e}")
        await repository_crud.update_status(
            repo_id, 
            RepoStatus.ERROR, 
            f"Processing failed: {str(e)}"
        )
        if repo_id_str in repos_db:
            repos_db[repo_id_str]["status"] = RepoStatus.ERROR
            repos_db[repo_id_str]["message"] = f"Processing failed: {str(e)}"

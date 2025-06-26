from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import json
import logging
from ..auth import verify_github_signature
from ..queues import enqueue_job
from ..crud import repository_crud, pull_request_crud, github_profile_crud
from ..models import PullRequestStatus
from ..config import get_github_webhook_secret

router = APIRouter(prefix="/github", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """
    Handle GitHub webhook events (pull_request, push, etc.)
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature
        if not verify_github_signature(body, x_hub_signature_256, get_github_webhook_secret()):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        event_type = request.headers.get("X-GitHub-Event")
        
        if event_type == "pull_request":
            await handle_pull_request_event(payload)
        elif event_type == "push":
            await handle_push_event(payload)
        else:
            logger.info(f"Received unhandled event type: {event_type}")
        
        return {"status": "success", "event": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_pull_request_event(payload: dict):
    """Handle pull_request webhook events"""
    try:
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})
        
        if action not in ["opened", "synchronize", "closed"]:
            logger.info(f"Ignoring PR action: {action}")
            return
        
        # Create or update GitHub profile for PR author
        author_data = pr_data.get("user", {})
        profile_data = {
            "github_id": author_data.get("id"),
            "username": author_data.get("login"),
            "avatar_url": author_data.get("avatar_url"),
            "name": author_data.get("name"),
            "email": author_data.get("email")
        }
        
        author_profile = await github_profile_crud.create_or_update(profile_data)
        
        # Create or update repository owner profile
        owner_data = repo_data.get("owner", {})
        owner_profile_data = {
            "github_id": owner_data.get("id"),
            "username": owner_data.get("login"),
            "avatar_url": owner_data.get("avatar_url"),
            "name": owner_data.get("name")
        }
        
        owner_profile = await github_profile_crud.create_or_update(owner_profile_data)
        
        # Create or update repository
        repository = await repository_crud.get_by_github_id(repo_data.get("id"))
        if not repository:
            repo_create_data = {
                "github_id": repo_data.get("id"),
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "url": repo_data.get("clone_url"),
                "branch": repo_data.get("default_branch", "main"),
                "owner_id": owner_profile.id,
                "description": repo_data.get("description"),
                "is_private": repo_data.get("private", False)
            }
            repository = await repository_crud.create(repo_create_data)
        
        # Determine PR status
        pr_status = "open"
        if pr_data.get("state") == "closed":
            if pr_data.get("merged"):
                pr_status = "merged"
            else:
                pr_status = "closed"
        
        # Create or update pull request
        pr_create_data = {
            "github_id": pr_data.get("id"),
            "number": pr_data.get("number"),
            "title": pr_data.get("title"),
            "body": pr_data.get("body"),
            "status": pr_status,
            "repository_id": repository.id,
            "author_id": author_profile.id,
            "base_branch": pr_data.get("base", {}).get("ref"),
            "head_branch": pr_data.get("head", {}).get("ref"),
            "closed_at": pr_data.get("closed_at"),
            "merged_at": pr_data.get("merged_at")
        }
        
        pull_request = await pull_request_crud.create_or_update(pr_create_data)
        
        # Enqueue background job for processing PR diff
        if action in ["opened", "synchronize"]:
            job_data = {
                "type": "process_pr_diff",
                "pull_request_id": pull_request.id,
                "repository_id": repository.id,
                "pr_number": pr_data.get("number"),
                "action": action,
                "diff_url": pr_data.get("diff_url"),
                "patch_url": pr_data.get("patch_url")
            }
            
            await enqueue_job(job_data)
            logger.info(f"Enqueued PR diff processing job for PR #{pr_data.get('number')}")
        
        logger.info(f"Processed PR event: {action} for PR #{pr_data.get('number')}")
        
    except Exception as e:
        logger.error(f"Error handling pull request event: {e}")
        raise


async def handle_push_event(payload: dict):
    """Handle push webhook events"""
    try:
        repo_data = payload.get("repository", {})
        ref = payload.get("ref", "")
        commits = payload.get("commits", [])
        
        # Only process pushes to main/master branches for now
        if not ref.endswith(("/main", "/master")):
            logger.info(f"Ignoring push to branch: {ref}")
            return
        
        # Get repository from database
        repository = await repository_crud.get_by_github_id(repo_data.get("id"))
        if not repository:
            logger.warning(f"Repository not found for push event: {repo_data.get('full_name')}")
            return
        
        # Enqueue background job for processing repository updates
        job_data = {
            "type": "process_push",
            "repository_id": repository.id,
            "ref": ref,
            "commits_count": len(commits),
            "head_commit": payload.get("head_commit", {}),
            "compare_url": payload.get("compare")
        }
        
        await enqueue_job(job_data)
        logger.info(f"Enqueued push processing job for {repo_data.get('full_name')}")
        
    except Exception as e:
        logger.error(f"Error handling push event: {e}")
        raise


@router.get("/webhook/health")
async def webhook_health():
    """Health check endpoint for webhook"""
    return {"status": "healthy", "service": "github-webhook"}

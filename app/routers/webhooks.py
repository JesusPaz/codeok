from fastapi import APIRouter, Header, Request, HTTPException
from typing import Optional
import logging
from ..auth import get_installation_token, verify_github_signature
from ..queues import enqueue_diff
from ..config import get_github_webhook_secret, get_github_app_id, get_github_private_key

router = APIRouter(prefix="/github", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(..., alias="X-Hub-Signature-256"),
    x_github_event: str = Header(..., alias="X-GitHub-Event")
):
    """
    Handle GitHub webhook events for pull requests
    """
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # Verify the webhook signature
        webhook_secret = get_github_webhook_secret()
        if not verify_github_signature(body, x_hub_signature_256, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the JSON payload
        payload = await request.json()
        
        logger.info(f"Received GitHub webhook event: {x_github_event}")
        
        # Handle pull request events
        if x_github_event == "pull_request" and payload.get("action") in {"opened", "synchronize"}:
            await handle_pull_request_event(payload)
        
        # Handle other events as needed
        elif x_github_event == "push":
            await handle_push_event(payload)
        
        else:
            logger.info(f"Ignoring event: {x_github_event} with action: {payload.get('action', 'N/A')}")
        
        return {"ok": True, "event": x_github_event}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_pull_request_event(payload: dict):
    """
    Handle pull request opened/synchronized events
    """
    try:
        installation_id = payload["installation"]["id"]
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["number"]
        
        logger.info(f"Processing PR event for {repo_full_name} PR #{pr_number}")
        
        # Get installation token for GitHub API access
        app_id = get_github_app_id()
        private_key = get_github_private_key()
        token = get_installation_token(app_id, str(installation_id), private_key)
        
        # Enqueue background job to process the diff
        await enqueue_diff(repo_full_name, pr_number, token)
        
        logger.info(f"Enqueued diff processing for {repo_full_name} PR #{pr_number}")
        
    except KeyError as e:
        logger.error(f"Missing required field in payload: {e}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
    except Exception as e:
        logger.error(f"Error processing PR event: {e}")
        raise


async def handle_push_event(payload: dict):
    """
    Handle push events (optional)
    """
    try:
        repo_full_name = payload["repository"]["full_name"]
        ref = payload["ref"]
        
        logger.info(f"Received push event for {repo_full_name} on {ref}")
        
        # Add logic to handle push events if needed
        # For example, re-index the repository if it's the main branch
        
    except Exception as e:
        logger.error(f"Error processing push event: {e}")


@router.get("/webhook/health")
async def webhook_health():
    """
    Health check endpoint for webhook service
    """
    return {
        "status": "healthy",
        "service": "github-webhook",
        "configured": {
            "app_id": bool(get_github_app_id() if hasattr(get_github_app_id, '__call__') else True),
            "webhook_secret": bool(get_github_webhook_secret())
        }
    }

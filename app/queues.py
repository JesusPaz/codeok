import asyncio
from typing import Dict, Any
import logging

# In-memory queue for background jobs (in production, use Redis/Celery)
job_queue = asyncio.Queue()

logger = logging.getLogger(__name__)


async def enqueue_diff(repo: str, pr_number: int, token: str) -> None:
    """
    Enqueue a diff processing job for a pull request
    """
    job = {
        "type": "process_pr_diff",
        "repo": repo,
        "pr_number": pr_number,
        "token": token,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await job_queue.put(job)
    logger.info(f"Enqueued diff processing job for {repo} PR #{pr_number}")


async def enqueue_job(job_data: Dict[str, Any]) -> None:
    """
    Enqueue a generic background job
    """
    job_data["timestamp"] = asyncio.get_event_loop().time()
    await job_queue.put(job_data)
    logger.info(f"Enqueued job: {job_data.get('type', 'unknown')}")


async def process_background_jobs():
    """
    Background worker to process queued jobs
    """
    while True:
        try:
            # Wait for a job from the queue
            job = await job_queue.get()
            
            if job["type"] == "process_pr_diff":
                await process_pr_diff(job)
            elif job["type"] == "process_push":
                await process_push_job(job)
            else:
                logger.warning(f"Unknown job type: {job.get('type')}")
            
            # Mark the job as done
            job_queue.task_done()
            
        except Exception as e:
            logger.error(f"Error processing background job: {e}")


async def process_pr_diff(job: Dict[str, Any]):
    """
    Process a pull request diff
    """
    if "repo" in job:
        # Legacy format from enqueue_diff
        repo = job["repo"]
        pr_number = job["pr_number"]
        token = job["token"]
        logger.info(f"Processing PR diff for {repo} PR #{pr_number}")
    else:
        # New format from webhook
        pull_request_id = job.get("pull_request_id")
        repository_id = job.get("repository_id")
        pr_number = job.get("pr_number")
        logger.info(f"Processing PR diff for repository {repository_id}, PR #{pr_number}")
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    # In a real implementation, you would:
    # 1. Fetch the PR diff using the GitHub API
    # 2. Analyze the changes
    # 3. Update embeddings/knowledge base
    # 4. Store results in database
    
    logger.info(f"Completed processing PR diff")


async def process_push_job(job: Dict[str, Any]):
    """
    Process a push event job
    """
    repository_id = job.get("repository_id")
    ref = job.get("ref")
    commits_count = job.get("commits_count", 0)
    
    logger.info(f"Processing push event for repository {repository_id}, ref {ref}, {commits_count} commits")
    
    # Simulate processing time
    await asyncio.sleep(3)
    
    # In a real implementation, you would:
    # 1. Fetch the new commits
    # 2. Re-analyze the repository
    # 3. Update embeddings/knowledge base
    # 4. Update repository status
    
    logger.info(f"Completed processing push event for repository {repository_id}")


def start_background_worker():
    """
    Start the background job processor
    """
    asyncio.create_task(process_background_jobs())

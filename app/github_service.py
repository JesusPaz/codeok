import httpx
import logging
from .github_auth import GitHubAppAuth

logger = logging.getLogger(__name__)

# Global authenticator instance
github_auth = GitHubAppAuth()

async def approve_pr(owner: str, repo: str, pr_number: int):
    """Approves a Pull Request using GitHub App exactly like the working script"""
    try:
        repository = f"{owner}/{repo}"
        
        # Get token using PyGithub like the working script
        access_token = github_auth.get_github_app_token_for_repo(repository)
        
        # Headers exactly like the working script
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        # Payload exactly like the working script
        data = {
            "event": "APPROVE"
        }
        
        print(f"🚀 Sending approval to: {url}")
        print(f"📦 Payload: {data}")
        print(f"🔑 Token: {access_token[:20]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"PR #{pr_number} approved successfully")
                print(f"✅ PR #{pr_number} APPROVED successfully")
                return True
            elif response.status_code == 201:
                logger.info(f"PR #{pr_number} approved successfully (201)")
                print(f"✅ PR #{pr_number} APPROVED successfully (201)")
                return True
            else:
                logger.error(f"Error approving PR #{pr_number}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                print(f"❌ Error approving PR #{pr_number}: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error approving PR #{pr_number}: {e}")
        print(f"❌ Exception approving PR #{pr_number}: {e}")
        return False

async def get_repository_info(owner: str, repo: str):
    """Gets repository information using GitHub App"""
    try:
        headers = await github_auth.get_authenticated_headers()
        
        url = f"https://api.github.com/repos/{owner}/{repo}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting repo info {owner}/{repo}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting repo info {owner}/{repo}: {e}")
        return None 
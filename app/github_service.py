import httpx
import logging
from .github_auth import GitHubAppAuth

logger = logging.getLogger(__name__)

# Instancia global del autenticador
github_auth = GitHubAppAuth()

async def approve_pr(owner: str, repo: str, pr_number: int):
    """Aprueba un Pull Request usando GitHub App exactamente como el script que funciona"""
    try:
        repository = f"{owner}/{repo}"
        
        # Obtener token usando PyGithub como el script que funciona
        access_token = github_auth.get_github_app_token_for_repo(repository)
        
        # Headers exactamente como el script que funciona
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        # Payload exactamente como el script que funciona
        data = {
            "event": "APPROVE"
        }
        
        print(f"🚀 Enviando aprobación a: {url}")
        print(f"📦 Payload: {data}")
        print(f"🔑 Token: {access_token[:20]}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"PR #{pr_number} aprobado exitosamente")
                print(f"✅ PR #{pr_number} APROBADO exitosamente")
                return True
            elif response.status_code == 201:
                logger.info(f"PR #{pr_number} aprobado exitosamente (201)")
                print(f"✅ PR #{pr_number} APROBADO exitosamente (201)")
                return True
            else:
                logger.error(f"Error aprobando PR #{pr_number}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                print(f"❌ Error aprobando PR #{pr_number}: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error aprobando PR #{pr_number}: {e}")
        print(f"❌ Exception aprobando PR #{pr_number}: {e}")
        return False

async def get_repository_info(owner: str, repo: str):
    """Obtiene información del repositorio usando GitHub App"""
    try:
        headers = await github_auth.get_authenticated_headers()
        
        url = f"https://api.github.com/repos/{owner}/{repo}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo info del repo {owner}/{repo}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error obteniendo info del repo {owner}/{repo}: {e}")
        return None 
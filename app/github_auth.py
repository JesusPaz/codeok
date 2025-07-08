import jwt
import time
import httpx
import logging
from github import GithubIntegration
from .config import get_github_app_id, get_github_private_key, get_github_installation_id

logger = logging.getLogger(__name__)

class GitHubAppAuth:
    """Class to handle GitHub App authentication using PyGithub like the working script"""
    
    def __init__(self):
        self.app_id = get_github_app_id()  # App ID (number)
        self.private_key = get_github_private_key()  # PEM file content
        self.installation_id = get_github_installation_id()
        self.git_integration = None
    
    def generate_jwt(self) -> str:
        """
        Generates a JWT following exactly the official documentation example
        https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
        """
        payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's App ID (must be number, not client ID)
            'iss': int(self.app_id)
        }
        
        # Clean and format the private key
        private_key = self.private_key.strip()
        
        # Remove quotes if present
        if private_key.startswith('"') and private_key.endswith('"'):
            private_key = private_key[1:-1]
        
        # Replace literal \n with actual line breaks
        private_key = private_key.replace('\\n', '\n')
        
        # Ensure it has the correct format
        if not private_key.startswith('-----BEGIN'):
            # If the key doesn't have headers, add them
            private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
        
        try:
            # Create JWT using RS256 algorithm as required by GitHub
            encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
            logger.info("JWT generated successfully")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error generating JWT: {e}")
            logger.error(f"Private key format: {private_key[:50]}...")
            raise
    
    def get_github_app_token_for_repo(self, repository: str) -> str:
        """
        Generates a GitHub App token for a specific repository using PyGithub
        Same as the working script
        """
        try:
            # Create a GitHub integration instance with App ID (number)
            if not self.git_integration:
                self.git_integration = GithubIntegration(int(self.app_id), self.private_key)
            
            # Parse the repository to get owner and repo name
            owner, repo_name = repository.split('/')
            
            # Find the installation ID for this repository
            try:
                installation_id = self.git_integration.get_repo_installation(owner, repo_name).id
                logger.info(f"Found installation ID {installation_id} for repository {repository}")
            except Exception as e:
                logger.error(f"Error finding installation for {repository}: {e}")
                raise Exception(f"Error finding installation for {repository}: {e}")
            
            # Generate an access token for this installation
            token = self.git_integration.get_access_token(installation_id).token
            logger.info("Successfully generated GitHub App installation token")
            
            return token
        except Exception as e:
            logger.error(f"Error generating GitHub App token: {e}")
            raise

    async def get_installation_access_token(self) -> str:
        """
        Gets an installation access token using the JWT
        Only needed if you want to make API requests
        """
        # Generate JWT for authentication
        jwt_token = self.generate_jwt()
        
        # Headers for GitHub API as per documentation
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        try:
            # First get the available installations
            async with httpx.AsyncClient() as client:
                installations_response = await client.get(
                    'https://api.github.com/app/installations',
                    headers=headers
                )
                
                if installations_response.status_code == 200:
                    installations = installations_response.json()
                    if installations:
                        # Use the first available installation
                        installation_id = installations[0]['id']
                        logger.info(f"Using installation ID: {installation_id}")
                        
                        # Get access token for this installation
                        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
                        response = await client.post(url, headers=headers)
                        
                        if response.status_code == 201:
                            data = response.json()
                            logger.info("Installation access token obtained successfully")
                            return data['token']
                        else:
                            logger.error(f"Error getting installation access token: {response.status_code}")
                            logger.error(f"Response: {response.text}")
                            raise Exception(f"Error getting installation access token: {response.status_code}")
                    else:
                        raise Exception("No installations found for this GitHub App")
                else:
                    logger.error(f"Error getting installations: {installations_response.status_code}")
                    raise Exception(f"Error getting installations: {installations_response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error in GitHub App authentication: {e}")
            raise
    
    async def get_authenticated_headers(self) -> dict:
        """
        Gets authenticated headers for GitHub API calls
        Uses the installation access token to authenticate requests
        """
        access_token = await self.get_installation_access_token()
        
        return {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "codeok-review-bot"
        } 
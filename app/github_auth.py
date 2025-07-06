import jwt
import time
import httpx
import logging
from github import GithubIntegration
from .config import get_github_app_id, get_github_private_key, get_github_installation_id

logger = logging.getLogger(__name__)

class GitHubAppAuth:
    """Clase para manejar la autenticación de GitHub App usando PyGithub como el script que funciona"""
    
    def __init__(self):
        self.app_id = get_github_app_id()  # App ID (número)
        self.private_key = get_github_private_key()  # PEM file content
        self.installation_id = get_github_installation_id()
        self.git_integration = None
    
    def generate_jwt(self) -> str:
        """
        Genera un JWT siguiendo exactamente el ejemplo de la documentación oficial
        https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
        """
        payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's App ID (debe ser número, no client ID)
            'iss': int(self.app_id)
        }
        
        # Limpiar y formatear la clave privada
        private_key = self.private_key.strip()
        
        # Remover comillas si las tiene
        if private_key.startswith('"') and private_key.endswith('"'):
            private_key = private_key[1:-1]
        
        # Reemplazar \n literales con saltos de línea reales
        private_key = private_key.replace('\\n', '\n')
        
        # Asegurar que tenga el formato correcto
        if not private_key.startswith('-----BEGIN'):
            # Si la clave no tiene los headers, agregarlos
            private_key = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key}\n-----END RSA PRIVATE KEY-----"
        
        try:
            # Create JWT using RS256 algorithm as required by GitHub
            encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
            logger.info("JWT generado exitosamente")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error generando JWT: {e}")
            logger.error(f"Formato de clave privada: {private_key[:50]}...")
            raise
    
    def get_github_app_token_for_repo(self, repository: str) -> str:
        """
        Genera un token de GitHub App para un repositorio específico usando PyGithub
        Igual que el script que funciona
        """
        try:
            # Crear una instancia de GitHub integration con App ID (número)
            if not self.git_integration:
                self.git_integration = GithubIntegration(int(self.app_id), self.private_key)
            
            # Parsear el repositorio para obtener owner y repo name
            owner, repo_name = repository.split('/')
            
            # Encontrar el installation ID para este repositorio
            try:
                installation_id = self.git_integration.get_repo_installation(owner, repo_name).id
                logger.info(f"Found installation ID {installation_id} for repository {repository}")
            except Exception as e:
                logger.error(f"Error finding installation for {repository}: {e}")
                raise Exception(f"Error finding installation for {repository}: {e}")
            
            # Generar un access token para esta instalación
            token = self.git_integration.get_access_token(installation_id).token
            logger.info("Successfully generated GitHub App installation token")
            
            return token
        except Exception as e:
            logger.error(f"Error generating GitHub App token: {e}")
            raise

    async def get_installation_access_token(self) -> str:
        """
        Obtiene un installation access token usando el JWT
        Solo se necesita si quieres hacer peticiones a la API
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
            # Primero obtenemos las instalaciones disponibles
            async with httpx.AsyncClient() as client:
                installations_response = await client.get(
                    'https://api.github.com/app/installations',
                    headers=headers
                )
                
                if installations_response.status_code == 200:
                    installations = installations_response.json()
                    if installations:
                        # Usar la primera instalación disponible
                        installation_id = installations[0]['id']
                        logger.info(f"Usando installation ID: {installation_id}")
                        
                        # Obtener access token para esta instalación
                        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
                        response = await client.post(url, headers=headers)
                        
                        if response.status_code == 201:
                            data = response.json()
                            logger.info("Installation access token obtenido exitosamente")
                            return data['token']
                        else:
                            logger.error(f"Error obteniendo installation access token: {response.status_code}")
                            logger.error(f"Response: {response.text}")
                            raise Exception(f"Error obteniendo installation access token: {response.status_code}")
                    else:
                        raise Exception("No se encontraron instalaciones para esta GitHub App")
                else:
                    logger.error(f"Error obteniendo instalaciones: {installations_response.status_code}")
                    raise Exception(f"Error obteniendo instalaciones: {installations_response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error en autenticación de GitHub App: {e}")
            raise
    
    async def get_authenticated_headers(self) -> dict:
        """
        Obtiene headers autenticados para las llamadas a la API de GitHub
        Usa el installation access token para autenticar las peticiones
        """
        access_token = await self.get_installation_access_token()
        
        return {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "fuse-review-bot"
        } 
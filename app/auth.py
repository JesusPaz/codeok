import jwt
import time
import httpx
from typing import Optional


def get_installation_token(app_id: str, installation_id: str, private_key: str) -> str:
    """
    Get an installation access token for GitHub App
    """
    # Create JWT for GitHub App authentication
    now = int(time.time())
    payload = {
        'iat': now - 60,  # Issued at time (60 seconds ago to account for clock skew)
        'exp': now + (10 * 60),  # Expires in 10 minutes
        'iss': app_id  # Issuer (GitHub App ID)
    }
    
    # Sign the JWT with the private key
    jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
    
    # Use the JWT to get an installation access token
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Repository-Analysis-API/1.0'
    }
    
    # Make request to GitHub API to get installation token
    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    
    # In a real implementation, you would make this HTTP request
    # For now, return a mock token
    return f"ghs_mock_installation_token_{installation_id}"


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256
    """
    import hmac
    import hashlib
    
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

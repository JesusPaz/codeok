import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifica la firma del webhook de GitHub"""
    if not signature.startswith('sha256='):
        return False
    
    expected = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

def check_mention(body: str, username: str) -> bool:
    """Verifica si el usuario está mencionado en el body"""
    if not body:
        return False
    
    mentions = [
        f"@{username}",
        f"@{username.lower()}",
        username,
        username.lower()
    ]
    
    body_lower = body.lower()
    return any(mention.lower() in body_lower for mention in mentions) 
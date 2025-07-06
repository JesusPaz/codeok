from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import json
import logging
from .config import get_webhook_secret, get_target_username
from .utils import verify_signature, check_mention
from .github_service import approve_pr

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "GitHub Webhook API",
        "version": "1.0.0",
        "endpoints": {
            "POST /webhook": "GitHub webhook endpoint",
            "GET /health": "Health check"
        }
    }

@router.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """Recibe webhooks de GitHub"""
    try:
        # Obtener body
        body = await request.body()
        
        # DEBUG: Imprimir información del webhook
        print("\n" + "="*60)
        print("🔍 DEBUG: WEBHOOK RECIBIDO")
        print("="*60)
        
        # Headers
        print("📋 HEADERS:")
        for key, value in request.headers.items():
            if key.lower().startswith('x-'):
                print(f"  {key}: {value}")
        
        # Verificar firma si está presente
        if x_hub_signature_256:
            print(f"🔐 Firma recibida: {x_hub_signature_256[:20]}...")
            if not verify_signature(body, x_hub_signature_256, get_webhook_secret()):
                print("❌ Firma inválida")
                raise HTTPException(status_code=401, detail="Firma inválida")
            else:
                print("✅ Firma válida")
        else:
            print("⚠️  No se recibió firma")
        
        # Parsear JSON
        payload = json.loads(body.decode('utf-8'))
        event_type = request.headers.get("X-GitHub-Event")
        
        print(f"🎯 Evento: {event_type}")
        print(f"📦 Payload keys: {list(payload.keys())}")
        
        # DEBUG: Imprimir payload completo (limitado)
        print("📄 PAYLOAD COMPLETO:")
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:1000] + "..." if len(json.dumps(payload)) > 1000 else json.dumps(payload, indent=2, ensure_ascii=False))
        
        logger.info(f"Recibido evento: {event_type}")
        
        # Solo procesar pull_request
        if event_type == "pull_request":
            action = payload.get("action")
            pr_data = payload.get("pull_request", {})
            repo_data = payload.get("repository", {})
            
            print(f"🔄 Acción: {action}")
            
            # Procesar PRs abiertos o actualizados
            if action in ["opened", "synchronize"]:
                pr_number = pr_data.get("number")
                pr_body = pr_data.get("body", "") or ""  # Manejar None
                pr_title = pr_data.get("title", "") or ""
                repo_full_name = repo_data.get("full_name", "")
                
                print(f"📝 PR #{pr_number}")
                print(f"🏠 Repositorio: {repo_full_name}")
                print(f"📖 Título: {pr_title}")
                print(f"📖 Body del PR: {pr_body}")
                
                logger.info(f"Procesando PR #{pr_number} en {repo_full_name}")
                
                # Verificar mención en título O body
                target_username = get_target_username()
                print(f"🎯 Buscando menciones de: {target_username}")
                
                # Buscar en título y body
                text_to_check = f"{pr_title} {pr_body}".lower()
                mention_found = False
                
                # Diferentes formas de mencionar
                mention_patterns = [
                    f"@{target_username}",
                    f"@{target_username.lower()}",
                    target_username.lower(),
                    "bot",  # Mención genérica al bot
                    "@bot"
                ]
                
                for pattern in mention_patterns:
                    if pattern.lower() in text_to_check:
                        mention_found = True
                        print(f"✅ Encontrada mención: '{pattern}'")
                        break
                
                if mention_found:
                    print(f"🚀 APROBANDO PR #{pr_number} automáticamente")
                    logger.info(f"Mención encontrada en PR #{pr_number}, aprobando automáticamente")
                    
                    if "/" in repo_full_name:
                        owner, repo = repo_full_name.split("/", 1)
                        success = await approve_pr(owner, repo, pr_number)
                        if success:
                            print(f"✅ PR #{pr_number} APROBADO exitosamente")
                        else:
                            print(f"❌ Error aprobando PR #{pr_number}")
                else:
                    print(f"❌ No se encontró mención relevante")
                    logger.info(f"No se encontró mención en PR #{pr_number}")
                    
            else:
                print(f"⏭️  Acción '{action}' no procesada (solo procesamos: opened, synchronize)")
        else:
            print(f"⏭️  Evento '{event_type}' no procesado (solo procesamos: pull_request)")
        
        print("="*60)
        print("✅ WEBHOOK PROCESADO")
        print("="*60 + "\n")
        
        return {"status": "success", "event": event_type}
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=500, detail="Error interno") 
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
    """Root endpoint"""
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
    """Receives GitHub webhooks"""
    try:
        # Get request body
        body = await request.body()
        
        # DEBUG: Print webhook information
        print("\n" + "="*60)
        print("🔍 DEBUG: WEBHOOK RECEIVED")
        print("="*60)
        
        # Headers
        print("📋 HEADERS:")
        for key, value in request.headers.items():
            if key.lower().startswith('x-'):
                print(f"  {key}: {value}")
        
        # Verify signature if present
        if x_hub_signature_256:
            print(f"🔐 Signature received: {x_hub_signature_256[:20]}...")
            if not verify_signature(body, x_hub_signature_256, get_webhook_secret()):
                print("❌ Invalid signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
            else:
                print("✅ Valid signature")
        else:
            print("⚠️  No signature received")
        
        # Parse JSON
        payload = json.loads(body.decode('utf-8'))
        event_type = request.headers.get("X-GitHub-Event")
        
        print(f"🎯 Event: {event_type}")
        print(f"📦 Payload keys: {list(payload.keys())}")
        
        # DEBUG: Print complete payload (limited)
        print("📄 COMPLETE PAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:1000] + "..." if len(json.dumps(payload)) > 1000 else json.dumps(payload, indent=2, ensure_ascii=False))
        
        logger.info(f"Received event: {event_type}")
        
        # Only process pull_request events
        if event_type == "pull_request":
            action = payload.get("action")
            pr_data = payload.get("pull_request", {})
            repo_data = payload.get("repository", {})
            
            print(f"🔄 Action: {action}")
            
            # Get PR data
            pr_number = pr_data.get("number")
            pr_body = pr_data.get("body", "") or ""  # Handle None
            pr_title = pr_data.get("title", "") or ""
            pr_state = pr_data.get("state", "")
            repo_full_name = repo_data.get("full_name", "")
            
            print(f"📝 PR #{pr_number}")
            print(f"🏠 Repository: {repo_full_name}")
            print(f"📖 Title: {pr_title}")
            print(f"📖 PR Body: {pr_body}")
            print(f"📊 State: {pr_state}")
            
            # Only process if PR is NOT closed
            if pr_state == "closed":
                print(f"⏭️  PR #{pr_number} is closed, not processing")
                logger.info(f"PR #{pr_number} is closed, not processing")
            else:
                logger.info(f"Processing PR #{pr_number} in {repo_full_name}")
                
                # Check for mention in title OR body
                target_username = get_target_username()
                print(f"🎯 Looking for mentions of: {target_username}")
                
                # Search in title and body
                text_to_check = f"{pr_title} {pr_body}".lower()
                mention_found = False
                
                # Different ways to mention
                mention_patterns = [
                    f"@{target_username}",
                    f"@{target_username.lower()}",
                    target_username.lower(),
                    "bot",  # Generic bot mention
                    "@bot"
                ]
                
                for pattern in mention_patterns:
                    if pattern.lower() in text_to_check:
                        mention_found = True
                        print(f"✅ Found mention: '{pattern}'")
                        break
                
                if mention_found:
                    print(f"🚀 APPROVING PR #{pr_number} automatically (action: {action})")
                    logger.info(f"Mention found in PR #{pr_number}, approving automatically (action: {action})")
                    
                    if "/" in repo_full_name:
                        owner, repo = repo_full_name.split("/", 1)
                        success = await approve_pr(owner, repo, pr_number)
                        if success:
                            print(f"✅ PR #{pr_number} APPROVED successfully")
                        else:
                            print(f"❌ Error approving PR #{pr_number}")
                else:
                    print(f"❌ No relevant mention found (action: {action})")
                    logger.info(f"No mention found in PR #{pr_number} (action: {action})")
        else:
            print(f"⏭️  Event '{event_type}' not processed (only processing: pull_request)")
        
        print("="*60)
        print("✅ WEBHOOK PROCESSED")
        print("="*60 + "\n")
        
        return {"status": "success", "event": event_type}
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal error") 
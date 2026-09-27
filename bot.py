import os
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

try:
    from src.context_store import ContextStore
    from src.conversation_manager import ConversationManager
    from src.composer import Composer
    from src.reply_handler import ReplyHandler
except ImportError:
    from context_store import ContextStore
    from conversation_manager import ConversationManager
    from composer import Composer
    from reply_handler import ReplyHandler

app = FastAPI(title="Vera Bot - SoloSpark")

context_store = ContextStore()
conv_manager = ConversationManager()
composer = Composer()
reply_handler = ReplyHandler()

class ContextPush(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]

class TickRequest(BaseModel):
    now: Optional[str] = None
    available_triggers: Optional[List[str]] = None
    available_trigger_ids: Optional[List[str]] = None
    max_actions: Optional[int] = 10

class ReplyRequest(BaseModel):
    conversation_id: str
    from_role: str
    message: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    trigger_id: Optional[str] = None
    received_at: Optional[str] = None
    turn_number: Optional[int] = None

@app.get("/v1/healthz")
async def healthz():
    return {
        "status": "ok",
        "contexts_loaded": context_store.get_counts()
    }

@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": "solospark",
        "team_members": ["solospark"],
        "model": os.environ.get("OPENROUTER_MODEL", "openrouter/free"),
        "approach": "4-context modular composer with prompt templates and multi-turn state manager",
        "contact_email": "solospark@example.com",
        "version": "1.0.0",
        "submitted_at": "2026-09-27T12:00:00Z"
    }

@app.post("/v1/context")
async def push_context(push: ContextPush):
    result = context_store.push(push.scope, push.context_id, push.version, push.payload)
    return result

@app.post("/v1/tick")
async def tick(req: TickRequest):
    actions = []
    triggers_to_check = req.available_triggers or req.available_trigger_ids or []
    max_actions = req.max_actions if req.max_actions is not None else 10
    
    for tid in triggers_to_check:
        if len(actions) >= max_actions:
            break
            
        trigger = context_store.get("trigger", tid)
        if not trigger:
            continue
            
        sup_key = trigger.get("suppression_key")
        if sup_key and conv_manager.is_key_suppressed(sup_key):
            continue
            
        merchant_id = trigger.get("merchant_id")
        if not merchant_id:
            continue
            
        merchant = context_store.get("merchant", merchant_id)
        if not merchant:
            continue
            
        customer_id = trigger.get("customer_id")
        customer = context_store.get("customer", customer_id) if customer_id else None
            
        category_slug = merchant.get("category_slug")
        category = context_store.get("category", category_slug) if category_slug else None
        
        if not category:
            continue
            
        # Compose message
        result = await composer.compose(category, merchant, trigger, customer)
        
        # Suppress the key once actioned
        if sup_key:
            conv_manager.add_suppression_key(sup_key)
            
        conv_id = f"conv_{tid}_{merchant_id}"
        conv_manager.add_turn(conv_id, "vera", result["body"], merchant_id=merchant_id)
            
        actions.append({
            "conversation_id": conv_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "send_as": "vera",
            "trigger_id": tid,
            "body": result["body"],
            "cta": result.get("cta", "open_ended"),
            "suppression_key": sup_key or f"sup_{tid}",
            "rationale": result.get("rationale", "Proactive merchant engagement.")
        })
        
    return {"actions": actions}

@app.post("/v1/reply")
async def handle_reply(req: ReplyRequest):
    # Log turn
    conv_manager.add_turn(req.conversation_id, req.from_role, req.message, req.merchant_id)
    
    if conv_manager.is_suppressed(req.conversation_id):
        return {"action": "end", "rationale": "Conversation previously suppressed or ended."}
        
    # Check hostile / opt-out
    lower_msg = req.message.lower().strip()
    hostile_triggers = ["stop", "unsubscribe", "not interested", "fuck off", "useless spam", "stop messaging", "don't message"]
    if any(trigger in lower_msg for trigger in hostile_triggers):
        conv_manager.suppress_conversation(req.conversation_id)
        return {
            "action": "send",
            "body": "I apologize for troubling you. I will not message you again. Wishing your business the very best!",
            "cta": "none",
            "rationale": "Merchant opted out; acknowledged politely and suppressed."
        }
        
    # Check auto-reply patterns
    auto_reply_phrases = [
        "thank you for contacting",
        "will respond shortly",
        "our team will respond",
        "out of office",
        "automated response",
        "auto-reply",
        "automated message",
        "we have received your message",
        "will get back to you"
    ]
    is_auto_reply = any(phrase in lower_msg for phrase in auto_reply_phrases)
    auto_count = conv_manager.get_auto_reply_count(req.conversation_id)
    
    if is_auto_reply or auto_count >= 1:
        return {
            "action": "wait",
            "wait_seconds": 86400,
            "rationale": "Automated auto-reply message detected; waiting for business to respond."
        }
    
    history = conv_manager.get_history(req.conversation_id)
    merchant = context_store.get("merchant", req.merchant_id) if req.merchant_id else None
    customer = context_store.get("customer", req.customer_id) if req.customer_id else None
    
    result = await reply_handler.handle_reply(merchant, customer, history)
    
    # Ensure default fields exist
    if result.get("action") == "send":
        conv_manager.add_turn(req.conversation_id, "vera", result["body"])
        if "cta" not in result:
            result["cta"] = "open_ended"
    if "rationale" not in result:
        result["rationale"] = "Contextual multi-turn follow-up."
        
    return result

@app.post("/v1/teardown")
async def teardown():
    """Wipes in-memory state at the end of the test as specified in the testing brief."""
    context_store.store.clear()
    conv_manager.conversations.clear()
    conv_manager.suppressed_triggers.clear()
    return {"status": "ok", "cleared": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.bot:app", host="0.0.0.0", port=port, reload=True)

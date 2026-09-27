class ConversationManager:
    def __init__(self):
        # Maps conversation_id -> dict of state
        self.conversations = {}
        # Keep track of suppressed triggers for a merchant
        self.suppressed_triggers = set()

    def add_turn(self, conversation_id: str, from_role: str, message: str, merchant_id: str = None):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "turns": [],
                "auto_reply_count": 0,
                "is_suppressed": False,
                "merchant_id": merchant_id
            }
            
        conv = self.conversations[conversation_id]
        
        # Check for auto-replies
        if from_role == "merchant" and conv["turns"]:
            last_merchant_turn = None
            for t in reversed(conv["turns"]):
                if t["from"] == "merchant":
                    last_merchant_turn = t
                    break
            
            if last_merchant_turn and last_merchant_turn["msg"] == message:
                conv["auto_reply_count"] += 1
            else:
                conv["auto_reply_count"] = 0
                
        conv["turns"].append({"from": from_role, "msg": message})

    def get_history(self, conversation_id: str) -> list:
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["turns"]
        return []

    def get_auto_reply_count(self, conversation_id: str) -> int:
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["auto_reply_count"]
        return 0

    def suppress_conversation(self, conversation_id: str):
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["is_suppressed"] = True
            mid = self.conversations[conversation_id]["merchant_id"]
            if mid:
                # Optionally suppress all future proactive triggers for this merchant
                pass

    def is_suppressed(self, conversation_id: str) -> bool:
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["is_suppressed"]
        return False
        
    def add_suppression_key(self, key: str):
        self.suppressed_triggers.add(key)
        
    def is_key_suppressed(self, key: str) -> bool:
        return key in self.suppressed_triggers

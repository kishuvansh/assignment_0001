class ContextStore:
    def __init__(self):
        # Dictionary structure: (scope, context_id) -> {"version": int, "payload": dict}
        self.store = {}

    def push(self, scope: str, context_id: str, version: int, payload: dict) -> dict:
        key = (scope, context_id)
        current = self.store.get(key)
        
        if current and current["version"] >= version:
            return {
                "accepted": False, 
                "reason": "stale_version", 
                "current_version": current["version"]
            }
            
        self.store[key] = {
            "version": version,
            "payload": payload
        }
        
        return {
            "accepted": True,
            "ack_id": f"ack_{context_id}_v{version}"
        }
        
    def get(self, scope: str, context_id: str) -> dict:
        data = self.store.get((scope, context_id))
        return data["payload"] if data else None

    def get_counts(self) -> dict:
        counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
        for (scope, _) in self.store:
            if scope in counts:
                counts[scope] += 1
        return counts

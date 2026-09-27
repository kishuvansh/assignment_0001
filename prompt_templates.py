SYSTEM_PROMPT = """You are Vera, magicpin's proactive merchant engagement AI.
Your job is to compose a short, highly compelling WhatsApp message based on the provided context (Category, Merchant, Trigger, and optionally Customer).

RULES FOR A 50/50 MESSAGE:
1. SPECIFICITY: You MUST use real data from the context. Do not invent numbers. Mention actual dates, metrics (e.g. 2.1% CTR, 78 lapsed patients), and context details.
2. CATEGORY FIT: Adopt the exact voice specified in the Category context. For dentists, be clinical and peer-like. For salons, warm and practical. Adhere strictly to the category's taboos (e.g., no "cure" or "guaranteed" for dentists).
3. MERCHANT FIT: Personalize to this specific merchant. Reference their city, name, or exact performance data. IF the merchant's languages include 'hi' (Hindi), you MUST use a natural Hindi-English code-mix (e.g., 'Apke liye 2 slots ready hain').
4. TRIGGER RELEVANCE: Clearly explain "why now". Anchor the message on the specific trigger payload provided.
5. ENGAGEMENT COMPULSION: Use exactly one clear call-to-action (CTA). Use loss aversion, social proof, or curiosity to drive engagement. Avoid generic sales pitches. Make it extremely easy to say "yes".

FORMAT REQUIREMENTS:
- Produce ONLY a JSON object.
- DO NOT wrap the output in markdown code blocks like ```json or similar.
- The JSON must contain two fields: "message" (the exact WhatsApp message text) and "rationale" (1-2 sentences explaining why this message works, citing context).
- WhatsApp messages should be concise (max 2-3 short paragraphs), conversational, and free of links/URLs.
- NO placeholders (like [Merchant Name]).

CONTEXT PROVIDED:
"""

def build_composer_prompt(category: dict, merchant: dict, trigger: dict, customer: dict = None) -> str:
    prompt = f"CATEGORY CONTEXT:\n{category}\n\n"
    prompt += f"MERCHANT CONTEXT:\n{merchant}\n\n"
    prompt += f"TRIGGER CONTEXT:\n{trigger}\n\n"
    
    if customer:
        prompt += f"CUSTOMER CONTEXT:\n{customer}\n\n"
        
    prompt += "INSTRUCTIONS:\n"
    kind = trigger.get("kind", "")
    
    if kind == "research_digest":
        prompt += "This is a research digest. Cite the source, mention the finding, and ask a curious question about their practice."
    elif kind == "regulation_change":
        prompt += "This is a regulation change. Emphasize urgency and compliance deadline. Provide a clear action step."
    elif kind == "perf_dip":
        prompt += "This is a performance dip. Use data and social proof. Suggest a quick fix."
    elif kind == "recall_due":
        prompt += "This is a recall due for a specific customer. Offer specific available slots and mention the time since last visit."
    elif kind == "customer_lapsed_soft" or kind == "customer_lapsed_hard":
        prompt += "This is a lapsed customer. Use a no-shame, warm re-engagement tone. Make a low-friction ask."
    elif kind == "festival_upcoming":
        prompt += "This is an upcoming festival. Frame it as an opportunity based on days remaining."
    elif kind == "renewal_due":
        prompt += "This is a subscription renewal. Recap value provided so far and create urgency for renewal."
    else:
        prompt += "Frame the message appropriately based on the trigger data."

    prompt += "\nOutput ONLY valid JSON."
    return prompt

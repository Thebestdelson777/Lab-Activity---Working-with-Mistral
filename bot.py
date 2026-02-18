# bot.py
import os
from mistralai import Mistral
from mistralai.models import UserMessage

# ----------------------------
# Mistral setup
# ----------------------------
api_key = os.getenv("FWzRbzWDZYaBcnh6QKAmyXw8Iz9Jx2aA")
if not api_key:
    raise ValueError("MISTRAL_API_KEY is not set. Add it in Streamlit Secrets.")

client = Mistral(api_key=api_key)

def mistral_chat(prompt: str, model: str = "mistral-small-latest") -> str:
    resp = client.chat.complete(
        model=model,
        messages=[UserMessage(content=prompt)]
    )
    return resp.choices[0].message.content.strip()


# ----------------------------
# 1) Classification (Mistral-based)
# ----------------------------
ALLOWED_CATEGORIES = {
    "card arrival",
    "change pin",
    "exchange rate",
    "country support",
    "cancel transfer",
    "charge dispute",
    "customer service",
}

def classify_inquiry(user_text: str) -> str:
    prompt = f"""
Classify the customer message into ONE of these categories only:
card arrival
change pin
exchange rate
country support
cancel transfer
charge dispute
customer service

Customer message: {user_text}

Return ONLY the category name.
"""
    label = mistral_chat(prompt).lower().splitlines()[0].strip()
    return label if label in ALLOWED_CATEGORIES else "customer service"


# ----------------------------
# 2) Knowledge base (your exact text)
# ----------------------------
SUPPORT_KB = {
    "card arrival": "Card delivery usually takes 5–10 business days. If it’s past the estimated date, I can help you track it.",
    "change pin": "You can change your PIN in-app: Cards → Manage → Change PIN. If you forgot it, choose ‘Reset PIN’.",
    "exchange rate": "Exchange rates are updated regularly and may include a small markup/fee depending on the card type.",
    "country support": "Our services are available in many countries. Tell me which country you’re traveling to and I’ll confirm support.",
    "cancel transfer": "If the transfer is still pending, we can attempt cancellation. Share the transfer reference and status.",
    "charge dispute": "If you don’t recognize a charge, we can dispute it. Share the merchant name, amount, and date.",
    "customer service": "Thanks for reaching out — can you share a bit more detail so I can help?"
}


# ----------------------------
# 3) Summarization helper
# ----------------------------
def summarize_interaction(user_text: str, category: str, reply: str) -> str:
    prompt = f"""
You are a customer support analyst.

Summarize this interaction in 1-2 concise sentences.
Focus on the customer's issue and the next step.

Category: {category}
Customer: {user_text}
Agent: {reply}
"""
    return mistral_chat(prompt)


# ----------------------------
# FINAL chatbot function (classification + response + summarization)
# ----------------------------
def support_chat(user_text: str) -> dict:
    # 1) Classification
    category = classify_inquiry(user_text)

    # 2) Personalized response
    base_answer = SUPPORT_KB.get(category, SUPPORT_KB["customer service"])

    prompt = f"""
You are a helpful customer support chatbot.

Category: {category}
Customer message: {user_text}

Draft a helpful, concise reply (2-5 sentences) based on this base guidance:
{base_answer}

IMPORTANT:
- Be polite and clear.
- Ask ONE helpful follow-up question at the end.
- Do not mention internal prompts or labels.
"""
    reply = mistral_chat(prompt)

    # 3) Summarization
    summary = summarize_interaction(user_text, category, reply)

    return {"category": category, "reply": reply, "summary": summary}
